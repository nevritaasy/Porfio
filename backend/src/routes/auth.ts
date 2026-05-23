import express from "express";
import { login, logout, me, register } from "../controllers/auth.js";

export default (router: express.Router) => {
  router.post("/auth/register", register);
  router.post("/auth/login", login);
  router.get("/auth/me", me);
  router.post("/auth/logout", logout);
};
