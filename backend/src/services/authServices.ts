import type { Request, Response } from "express";
import { findSessionFromRequest } from "./sessionServices.js";

export type AuthBody = {
  name?: string;
  email?: string;
  password?: string;
};

function validateAuthBody(body: AuthBody | undefined, requireName: boolean) {
  if (!body || typeof body !== "object") {
    return { error: "Request body is required." };
  }

  const name = body.name?.trim();
  const emailRaw = body.email?.trim();
  const password = body.password;

  if (requireName && !name) {
    return { error: "Name is required." };
  }

  // For registration (requireName === true) require an email.
  if (requireName && !emailRaw) {
    return { error: "Email is required." };
  }

  // For login (requireName === false) allow either email or name.
  if (!requireName && !emailRaw && !name) {
    return { error: "Email or name is required." };
  }

  if (!password) {
    return { error: "Password is required." };
  }

  return {
    name,
    email: emailRaw ? normalizeEmail(emailRaw) : undefined,
    password,
  };
}

export async function requireAuth(
  req: Request,
  res: Response,
): Promise<boolean> {
  const session = await findSessionFromRequest(req);
  if (!session) {
    res.status(401).json({ error: "Not authenticated." });
    return false;
  }

  req.authUser = sanitizeUser(session.user);
  req.authSessionId = session.id;
  return true;
}


function sanitizeUser(user: {
  id: string;
  name: string;
  email: string;
  password?: string;
}) {
  const { password: _password, ...safeUser } = user;
  return safeUser;
}

function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

export { validateAuthBody, sanitizeUser, normalizeEmail };