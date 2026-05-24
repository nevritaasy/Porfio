import type { User } from "@prisma/client";

declare global {
  namespace Express {
    interface Request {
      authUser?: Omit<User, "password">;
      authSessionId?: string;
    }
  }
}

export {};
