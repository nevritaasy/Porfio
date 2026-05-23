import express from "express";
import auth from "./auth.js";
import scripts from "./scripts.js";
import file from "./file.js";

const router = express.Router();

auth(router);
scripts(router);
file(router);

export default router;
