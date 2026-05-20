import express from "express";
import { processScript } from "../controllers/scripts.js";

export default (router: express.Router) => {
  router.post("/process-pdf", processScript);
};