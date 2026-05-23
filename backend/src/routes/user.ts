import express from "express";
import { me } from "../controllers/user.js";

export default (router: express.Router) => {
  router.get("/user/me", me);
};
