import multer from 'multer';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';


// Constants
export const UPLOAD_DIR = process.env.PDF_UPLOAD_DIR ?? path.join(process.cwd(), 'uploads');
export const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB
const ALLOWED_MIME_TYPE = 'application/pdf';
const ALLOWED_EXTENSION = '.pdf';

// Fs check
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}


// Storage config
const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, UPLOAD_DIR);
  },
  filename: (_req, file, cb) => {
    // Prefix with a random hex string to avoid collisions and path traversal
    const randomPrefix = crypto.randomBytes(8).toString('hex');
    const safeName = path.basename(file.originalname).replace(/[^a-zA-Z0-9._-]/g, '_');
    cb(null, `${randomPrefix}-${safeName}`);
  },
});


// File filter
const fileFilter: multer.Options['fileFilter'] = (_req, file, cb) => {
  const ext = path.extname(file.originalname).toLowerCase();
  const isMimeValid = file.mimetype === ALLOWED_MIME_TYPE;
  const isExtValid = ext === ALLOWED_EXTENSION;

  if (isMimeValid && isExtValid) {
    cb(null, true);
  } else {
    cb(new Error(`Invalid file type. Only PDF files are accepted.`));
  }
};

// Multer instance

export const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: MAX_FILE_SIZE_BYTES,
    files: 1,
  },
});

