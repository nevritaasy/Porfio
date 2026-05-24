import "dotenv/config";
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "@prisma/client";

declare global {
  var __prisma: PrismaClient | undefined;
}

const connectionString = process.env.DB_URL;

if (!connectionString) {
  throw new Error(
    "Missing database connection string. Set DB_URL or DATABASE_URL.",
  );
}

function normalizeConnectionString(rawConnectionString: string): string {
  const trimmedConnectionString = rawConnectionString
    .trim()
    .replace(/^['"]|['"]$/g, "");

  try {
    new URL(trimmedConnectionString);
    return trimmedConnectionString;
  } catch {
    const match = trimmedConnectionString.match(
      /^(?<protocol>[a-z][a-z0-9+.-]*:\/\/)(?<username>[^:/?#@]+)(?::(?<password>[^@]*))?@(?<rest>.+)$/i,
    );

    if (!match?.groups) {
      return trimmedConnectionString;
    }

    const {
      protocol,
      username,
      password = "",
      rest,
    } = match.groups as {
      protocol: string;
      username: string;
      password?: string;
      rest: string;
    };

    const encodedUsername = encodeURIComponent(username);
    const encodedPassword = password ? encodeURIComponent(password) : "";

    return `${protocol}${encodedUsername}${password ? `:${encodedPassword}` : ""}@${rest}`;
  }
}

const adapter = new PrismaPg({
  connectionString: normalizeConnectionString(connectionString),
});
const prisma = global.__prisma ?? new PrismaClient({ adapter });
if (process.env.NODE_ENV === "development") {
  global.__prisma = prisma;
}

export default prisma;
