import express from "express";
import auth from "./auth.js";
import scripts from "./scripts.js";
import file from "./file.js";
import user from "./user.js";

const router = express.Router();

auth(router);
scripts(router);
file(router);
user(router);

export default router;
