import express from "express";
import scripts from "./scripts.js";
import file from "./file.js";

const router = express.Router();

scripts(router);
file(router);

export default router;