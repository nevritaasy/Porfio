import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import multer from 'multer';
import type { Request, Response, NextFunction, RequestHandler } from 'express';

import { UPLOAD_DIR, MAX_FILE_SIZE_BYTES } from '../config/multer.js';

export const receivePdf = (req: Request, res: Response): void => {
  const file = req.file;

  if (!file) {
    res.status(400).json({ error: 'No file uploaded. Expected a PDF under the "file" field.' });
    return;
  }

  const savedPath = path.join(UPLOAD_DIR, file.filename);

  // Paranoia check: confirm the resolved path stays inside the upload directory
  if (!savedPath.startsWith(path.resolve(UPLOAD_DIR))) {
    fs.unlinkSync(savedPath);
    res.status(400).json({ error: 'Invalid file path.' });
    return;
  }

  res.status(201).json({
    message: 'PDF uploaded successfully.',
    filename: file.filename,
    originalName: file.originalname,
    sizeBytes: file.size,
    path: savedPath,
  });
};