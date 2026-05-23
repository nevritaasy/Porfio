import crypto from "crypto";
import type { Request, Response } from "express";
import prisma from "../lib/prisma.js";

const SESSION_COOKIE_NAME = "porfio_session";
const SESSION_DURATION_MS = 1000 * 60 * 60 * 24 * 7;

type AuthBody = {
  name?: string;
  email?: string;
  password?: string;
};

function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

export function sanitizeUser(user: {
  id: string;
  name: string;
  email: string;
  password?: string;
}) {
  const { password: _password, ...safeUser } = user;
  return safeUser;
}

function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16).toString("hex");
  const derivedKey = crypto.scryptSync(password, salt, 64).toString("hex");
  return `${salt}:${derivedKey}`;
}

function verifyPassword(password: string, storedPassword: string): boolean {
  const [salt, storedHash] = storedPassword.split(":");
  if (!salt || !storedHash) {
    return false;
  }

  const derivedKey = crypto.scryptSync(password, salt, 64).toString("hex");
  const storedBuffer = Buffer.from(storedHash, "hex");
  const derivedBuffer = Buffer.from(derivedKey, "hex");

  if (storedBuffer.length !== derivedBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(storedBuffer, derivedBuffer);
}

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

export async function findSessionFromRequest(req: Request) {
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

export async function me(req: Request, res: Response): Promise<void> {
  const session = await findSessionFromRequest(req);
  if (!session) {
    res.status(401).json({ error: "Not authenticated." });
    return;
  }

  res.json({ user: sanitizeUser(session.user) });
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
