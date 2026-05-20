import multer from 'multer';
import type { Request, Response, NextFunction, RequestHandler } from 'express';

import { upload } from '../config/multer.js';
import { MAX_FILE_SIZE_BYTES } from '../config/multer.js';

export const uploadMiddleware: RequestHandler = (req: Request, res: Response, next: NextFunction) => {
  const handler = upload.single('file');

  handler(req, res, (err: unknown) => {
    if (err instanceof multer.MulterError) {
      if (err.code === 'LIMIT_FILE_SIZE') {
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