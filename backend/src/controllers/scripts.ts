import { spawn, spawnSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";
import type { Request, Response } from "express";

import { sanitizeUser } from "../services/authServices.js";
import { findSessionFromRequest } from "../services/sessionServices.js";
import prisma from "../lib/prisma.js";

const SCRIPT_PATH = path.resolve(process.cwd(), "ai_services", "main.py");
const MAX_BUFFER_BYTES = 10 * 1024 * 1024;
const TIMEOUT_MS = 100_000;

type PythonCommand = {
  command: string;
  args: string[];
};

function isCommandAvailable(command: string, args: string[]): boolean {
  const result = spawnSync(command, [...args, "--version"], {
    stdio: "ignore",
    windowsHide: true,
  });

  return !result.error && result.status === 0;
}

function resolvePythonCommand(): PythonCommand {
  const envPython = process.env.PYTHON_BIN?.trim();
  if (envPython) {
    return { command: envPython, args: [] };
  }

  const candidates: PythonCommand[] =
    process.platform === "win32"
      ? [
          { command: "py", args: ["-3"] },
          { command: "python", args: [] },
          { command: "python3", args: [] },
        ]
      : [
          { command: "python3", args: [] },
          { command: "python", args: [] },
        ];

  for (const candidate of candidates) {
    if (isCommandAvailable(candidate.command, candidate.args)) {
      return candidate;
    }
  }

  throw new Error(
    "No Python interpreter found on PATH. Set PYTHON_BIN to a valid executable.",
  );
}

function getUseOllama(req: Request): boolean {
  const val = req.query.useOllama ?? req.body?.useOllama;
  if (val === undefined || val === null || val === "") {
    return true;
  }

  return !(val === "false" || val === false);
}

const processScript = async (req: Request, res: Response): Promise<void> => {
  const uploadedFile = req.file;
  const session = await findSessionFromRequest(req);
  if (!session) {
    res.status(401).json({ error: "Not authenticated." });
    return;
  }

  const user = sanitizeUser(session.user);

  if (!uploadedFile) {
    res.status(400).json({
      error: 'No file uploaded. Expected a PDF under the "file" field.',
    });
    return;
  }

  const useOllama = getUseOllama(req);
  const pythonCommand = resolvePythonCommand();
  const tempDir = await fs.promises.mkdtemp(path.join(os.tmpdir(), "porfio-"));
  const tempPdfPath = path.join(
    tempDir,
    path.basename(uploadedFile.originalname).replace(/[^a-zA-Z0-9._-]/g, "_"),
  );

  await fs.promises.writeFile(tempPdfPath, uploadedFile.buffer);

  const cleanupTempFile = async (): Promise<void> => {
    await fs.promises.rm(tempDir, { recursive: true, force: true });
  };

  const pythonArgs = [
    ...pythonCommand.args,
    SCRIPT_PATH,
    "--input",
    tempPdfPath,
  ];

  pythonArgs.push(useOllama ? "--use-ollama" : "--no-ollama");

  let python: ReturnType<typeof spawn>;
  try {
    python = spawn(pythonCommand.command, pythonArgs, {
      stdio: ["pipe", "pipe", "pipe"],
      env: {
        ...process.env,
        PYTHONIOENCODING: "utf-8",
        PYTHONUTF8: "1",
      },
    });
  } catch (err) {
    console.error("Failed to spawn Python process:", err);
    await cleanupTempFile();
    res.status(500).json({
      error: (err as Error).message || "Failed to start processing script.",
    });
    return;
  }

  let resolved = false;
  let bufferedBytes = 0;
  let result = "";

  // Timeout guard
  const timeout = setTimeout(() => {
    if (!resolved) {
      resolved = true;
      python.kill();
      console.error("Python process timed out.");
      void cleanupTempFile();
      res.status(504).json({ error: "Processing timed out." });
    }
  }, TIMEOUT_MS);

  python.stdin?.end();

  // Collect stdout with a size cap
  python.stdout?.on("data", (data: Buffer) => {
    bufferedBytes += data.byteLength;
    if (bufferedBytes > MAX_BUFFER_BYTES) {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        python.kill();
        console.error("Python process output exceeded max buffer size.");
        void cleanupTempFile();
        res.status(500).json({ error: "Output too large." });
      }
      return;
    }
    result += data.toString();
  });

  // Log stderr
  python.stderr?.on("data", (data: Buffer) => {
    console.error(`[python stderr]: ${data.toString().trim()}`);
  });

  python.on("error", (err) => {
    if (!resolved) {
      resolved = true;
      clearTimeout(timeout);
      console.error("Python process error:", err);
      void cleanupTempFile();
      if ((err as NodeJS.ErrnoException).code === "ENOENT") {
        res.status(500).json({
          error:
            "Failed to run processing script. Python was not found on PATH.",
        });
        return;
      }
      res.status(500).json({ error: "Failed to run processing script." });
    }
  });

  python.on("close", (code: number | null, signal: NodeJS.Signals | null) => {
    if (resolved) return;
    resolved = true;
    clearTimeout(timeout);

    if (signal !== null) {
      console.error(`Python process was killed by signal: ${signal}`);
      void cleanupTempFile();
      res.status(500).json({ error: `Process killed by signal: ${signal}` });
      return;
    }

    if (code !== 0) {
      console.error(`Python process exited with code ${code}`);
      void cleanupTempFile();
      res.status(500).json({ error: `Script failed with exit code ${code}` });
      return;
    }

    try {
      const parsedResult = JSON.parse(result);
      void cleanupTempFile();

      void (async () => {
        try {
          await prisma.analysis.create({
            data: {
              content: parsedResult,
              userId: user.id,
            },
          });
          res.json(parsedResult);
        } catch (saveError) {
          console.error("Failed to save analysis:", saveError);
          res.status(500).json({
            error: "Processing succeeded but saving analytics failed.",
          });
        }
      })();
    } catch (err) {
      console.error("Failed to parse Python JSON output:", err);
      void cleanupTempFile();
      res.status(500).json({
        error: "Processing script returned invalid JSON.",
        raw: result,
      });
    }
  });
};

export { processScript };
