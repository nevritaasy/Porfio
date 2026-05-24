import crypto from "crypto";
import type { Request } from "express";
import prisma from "../lib/prisma.js";

// Session consts
const SESSION_COOKIE_NAME = "porfio_session";
const SESSION_DURATION_MS = 1000 * 60 * 60 * 24 * 7;

function generateSessionToken(): string {
  return crypto.randomBytes(32).toString("hex");
}

function hashSessionToken(token: string): string {
  return crypto.createHash("sha256").update(token).digest("hex");
}

function getCookieValue(req: Request, cookieName: string): string | undefined {
  const cookieHeader = req.headers.cookie;
  if (!cookieHeader) {
    return undefined;
  }

  const cookies = cookieHeader.split(";").map((cookie) => cookie.trim());
  const target = cookies.find((cookie) => cookie.startsWith(`${cookieName}=`));
  if (!target) {
    return undefined;
  }

  return decodeURIComponent(target.slice(cookieName.length + 1));
}

function buildCookieOptions() {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: SESSION_DURATION_MS,
  };
}

async function createSession(userId: string) {
  const token = generateSessionToken();
  const tokenHash = hashSessionToken(token);
  const expiresAt = new Date(Date.now() + SESSION_DURATION_MS);
  const session = await (prisma as any).session.create({
    data: {
      tokenHash,
      userId,
      expiresAt,
    },
  });

  return { token, session };
}

async function findSessionFromRequest(req: Request) {
  const token = getCookieValue(req, SESSION_COOKIE_NAME);
  if (!token) {
    return null;
  }

  const tokenHash = hashSessionToken(token);
  const session = await (prisma as any).session.findUnique({
    where: { tokenHash },
    include: { user: true },
  });

  if (!session || session.expiresAt <= new Date()) {
    if (session) {
      await (prisma as any).session.delete({ where: { id: session.id } });
    }
    return null;
  }

  return session;
}

export {
  createSession,
  findSessionFromRequest,
  buildCookieOptions,
  SESSION_COOKIE_NAME,
};