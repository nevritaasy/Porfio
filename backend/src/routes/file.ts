import express from 'express';
import { receivePdf } from '../controllers/files.js';
import { uploadMiddleware } from '../middleware/handleInputFile.js';

export default (router: express.Router) => {
  router.post('/upload-pdf', uploadMiddleware, receivePdf);
};
