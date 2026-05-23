import express from "express";
import {
  me,
  getUser,
  getOwnUser,
  getOwnLatestAnalysis,
} from "../controllers/user.js";

export default (router: express.Router) => {
  router.get("/user/me", me);
  router.get("/user/own", getOwnUser);
  router.get("/user/own/latest", getOwnLatestAnalysis);
};
