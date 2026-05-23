import express from "express";
import { processScript } from "../controllers/scripts.js";
import { uploadMiddleware } from "../middleware/handleInputFile.js";

export default (router: express.Router) => {
  router.post("/process-pdf", uploadMiddleware, processScript);
};