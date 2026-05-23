import multer from "multer";
import type { Request, Response, NextFunction, RequestHandler } from "express";

import { MAX_FILE_SIZE_BYTES } from "../config/multer.js";

const ALLOWED_MIME_TYPE = "application/pdf";
const ALLOWED_EXTENSION = ".pdf";

const upload = multer({
  storage: multer.memoryStorage(),
  fileFilter: (_req, file, cb) => {
    const isMimeValid = file.mimetype === ALLOWED_MIME_TYPE;
    const isExtValid = file.originalname
      .toLowerCase()
      .endsWith(ALLOWED_EXTENSION);

    if (isMimeValid && isExtValid) {
      cb(null, true);
      return;
    }

    cb(new Error("Invalid file type. Only PDF files are accepted."));
  },
  limits: {
    fileSize: MAX_FILE_SIZE_BYTES,
    files: 1,
  },
});

export const uploadMemoryMiddleware: RequestHandler = (
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  const handler = upload.single("file");

  handler(req, res, (err: unknown) => {
    if (err instanceof multer.MulterError) {
      if (err.code === "LIMIT_FILE_SIZE") {
        res.status(413).json({
          error: `File too large. Maximum allowed size is ${MAX_FILE_SIZE_BYTES / (1024 * 1024)} MB.`,
        });
        return;
      }

      res.status(400).json({ error: `Upload error: ${err.message}` });
      return;
    }

    if (err instanceof Error) {
      res.status(400).json({ error: err.message });
      return;
    }

    next();
  });
};
