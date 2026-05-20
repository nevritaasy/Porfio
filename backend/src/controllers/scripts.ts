import { spawn } from 'child_process';
import path from 'path';
import type { Request, Response } from 'express';

const PYTHON_EXECUTABLE = process.env.PYTHON_BIN ?? 'python3';
const SCRIPT_PATH = path.join('ai_services', 'main.py');
const MAX_BUFFER_BYTES = 10 * 1024 * 1024; 
const TIMEOUT_MS = 30_000; 

function getPdfPath(): string {
  const pdfPath = process.env.PDF_PATH;
  if (!pdfPath) {
    throw new Error('PDF_PATH environment variable is required but not set.');
  }
  return pdfPath;
}

function getUseOllama(req: Request): boolean {
  const val = req.query.useOllama ?? req.body?.useOllama;
  return val === 'true' || val === true;
}

const processScript = async (req: Request, res: Response): Promise<void> => {
  let pdfPath: string;

  try {
    pdfPath = getPdfPath();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server misconfiguration: PDF_PATH is not set.' });
    return;
  }

  const useOllama = getUseOllama(req);

  let python: ReturnType<typeof spawn>;
  try {
    python = spawn(PYTHON_EXECUTABLE, [
      SCRIPT_PATH,
      `--use-ollama=${useOllama}`,
      pdfPath,
    ], { stdio: ['pipe', 'pipe', 'pipe'] });
  } catch (err) {
    console.error('Failed to spawn Python process:', err);
    res.status(500).json({ error: 'Failed to start processing script.' });
    return;
  }

  let resolved = false;
  let bufferedBytes = 0;
  let result = '';

  // Timeout guard
  const timeout = setTimeout(() => {
    if (!resolved) {
      resolved = true;
      python.kill();
      console.error('Python process timed out.');
      res.status(504).json({ error: 'Processing timed out.' });
    }
  }, TIMEOUT_MS);

  // Write request body to stdin
  if (req.body && Object.keys(req.body).length > 0) {
    python.stdin?.on('error', (err) => {
      console.error('stdin error:', err);
    });
    try {
      python.stdin?.write(JSON.stringify(req.body));
    } catch (err) {
      console.error('Failed to write to stdin:', err);
    } finally {
      python.stdin?.end();
    }
  } else {
    python.stdin?.end();
  }

  // Collect stdout with a size cap
  python.stdout?.on('data', (data: Buffer) => {
    bufferedBytes += data.byteLength;
    if (bufferedBytes > MAX_BUFFER_BYTES) {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        python.kill();
        console.error('Python process output exceeded max buffer size.');
        res.status(500).json({ error: 'Output too large.' });
      }
      return;
    }
    result += data.toString();
  });

  // Log stderr but don't expose it to the client
  python.stderr?.on('data', (data: Buffer) => {
    console.error(`[python stderr]: ${data.toString().trim()}`);
  });

  python.on('error', (err) => {
    if (!resolved) {
      resolved = true;
      clearTimeout(timeout);
      console.error('Python process error:', err);
      res.status(500).json({ error: 'Failed to run processing script.' });
    }
  });

  // 'close' fires after all stdio streams have ended — safe to send response here
  python.on('close', (code: number | null, signal: NodeJS.Signals | null) => {
    if (resolved) return;
    resolved = true;
    clearTimeout(timeout);

    if (signal !== null) {
      console.error(`Python process was killed by signal: ${signal}`);
      res.status(500).json({ error: `Process killed by signal: ${signal}` });
      return;
    }

    if (code !== 0) {
      console.error(`Python process exited with code ${code}`);
      res.status(500).json({ error: `Script failed with exit code ${code}` });
      return;
    }

    res.json({ result });
  });
};

export { processScript };