import type { Request, Response } from "express";
import prisma from "../lib/prisma.js";
import { validateAuthBody, sanitizeUser } from "../services/authServices.js";
import { createSession, findSessionFromRequest, buildCookieOptions, SESSION_COOKIE_NAME } from "../services/sessionServices.js";

export async function me(req: Request, res: Response): Promise<void> {
  const session = await findSessionFromRequest(req);
  if (!session) {
    res.status(401).json({ error: "Not authenticated." });
    return;
  }

  res.json({ user: sanitizeUser(session.user) });
}
