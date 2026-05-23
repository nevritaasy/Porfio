import type { Request, Response } from "express";
import prisma from "../lib/prisma.js";

import { validateAuthBody, sanitizeUser } from "../services/authServices.js";
import { createSession, findSessionFromRequest, buildCookieOptions, SESSION_COOKIE_NAME } from "../services/sessionServices.js";
import { hashPassword, verifyPassword } from "../services/passwordService.js";
import type { AuthBody } from "../services/authServices.js";

export async function register(req: Request, res: Response): Promise<void> {
  const validated = validateAuthBody(req.body as AuthBody | undefined, true);
  if ("error" in validated) {
    res.status(400).json({ error: validated.error });
    return;
  }

  const reg = validated as { name: string; email: string; password: string };

  const existingUser = await prisma.user.findFirst({
    where: {
      OR: [{ email: reg.email }, { name: reg.name }],
    },
  });

  if (existingUser) {
    res
      .status(409)
      .json({ error: "A user with that email or name already exists." });
    return;
  }

  const { name, email, password } = validated as {
    name: string;
    email: string;
    password: string;
  };

  const user = await prisma.user.create({
    data: {
      name,
      email,
      password: hashPassword(password),
    },
  });

  const { token } = await createSession(user.id);
  res.cookie(SESSION_COOKIE_NAME, token, buildCookieOptions());
  res.status(201).json({ user: sanitizeUser(user) });
}

export async function login(req: Request, res: Response): Promise<void> {
  const validated = validateAuthBody(req.body as AuthBody | undefined, false);
  if ("error" in validated) {
    res.status(400).json({ error: validated.error });
    return;
  }

  // Allow login by email or by name
  const whereClause: any = validated.email
    ? { email: validated.email }
    : { name: (validated as any).name };

  const user = await prisma.user.findFirst({ where: whereClause });

  if (!user || !verifyPassword((validated as any).password, user.password)) {
    res.status(401).json({ error: "Invalid credentials." });
    return;
  }

  const { token } = await createSession(user.id);
  res.cookie(SESSION_COOKIE_NAME, token, buildCookieOptions());
  res.json({ user: sanitizeUser(user) });
}

export async function logout(req: Request, res: Response): Promise<void> {
  const session = await findSessionFromRequest(req);

  if (session) {
    await (prisma as any).session.delete({ where: { id: session.id } });
  }

  res.clearCookie(SESSION_COOKIE_NAME, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
  });

  res.json({ message: "Logged out successfully." });
}