import type { Request, Response } from "express";
import prisma from "../lib/prisma.js";
import { validateAuthBody, sanitizeUser } from "../services/authServices.js";
import {
  createSession,
  findSessionFromRequest,
  buildCookieOptions,
  SESSION_COOKIE_NAME,
} from "../services/sessionServices.js";

export async function me(req: Request, res: Response): Promise<void> {
  const session = await findSessionFromRequest(req);
  if (!session) {
    res.status(401).json({ error: "Not authenticated." });
    return;
  }

  res.json({ user: sanitizeUser(session.user) });
}

export async function getUser(req: Request, res: Response): Promise<void> {
  const session = await findSessionFromRequest(req);
  if (!session) {
    res.status(401).json({ error: "Not authenticated." });
    return;
  }

  const rawUserId = req.params.id;
  if (Array.isArray(rawUserId)) {
    res.status(400).json({ error: "Invalid user id." });
    return;
  }
  const userId = rawUserId;
  if (!userId || session.userId !== userId) {
    res.status(403).json({ error: "Forbidden." });
    return;
  }

  const user = await prisma.user.findUnique({ where: { id: userId } });
  if (!user) {
    res.status(404).json({ error: "User not found." });
    return;
  }
  res.json({ user: sanitizeUser(user) });
}

export async function getOwnUser(req: Request, res: Response): Promise<void> {
  const session = await findSessionFromRequest(req);
  if (!session) {
    res.status(401).json({ error: "Not authenticated." });
    return;
  }

  const user = await prisma.user.findUnique({
    where: { id: session.userId },
    include: {
      analyses: {
        orderBy: {
          createdAt: "desc",
        },
      },
    },
  });

  if (!user) {
    res.status(404).json({ error: "User not found." });
    return;
  }

  res.json({ user: sanitizeUser(user) });
}

export async function getOwnLatestAnalysis(
  req: Request,
  res: Response,
): Promise<void> {
  const session = await findSessionFromRequest(req);
  if (!session) {
    res.status(401).json({ error: "Not authenticated." });
    return;
  }

  const analysis = await prisma.analysis.findFirst({
    where: { userId: session.userId },
    orderBy: { createdAt: "desc" },
  });

  if (!analysis) {
    res.status(404).json({ error: "Analysis not found." });
    return;
  }

  res.json({ analysis });
}
