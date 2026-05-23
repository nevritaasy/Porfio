import express from "express";
import { processScript } from "../controllers/scripts.js";
import { uploadMemoryMiddleware } from "../middleware/handleInputFileMemory.js";

export default (router: express.Router) => {
  router.post("/process-pdf", uploadMemoryMiddleware, processScript);
};