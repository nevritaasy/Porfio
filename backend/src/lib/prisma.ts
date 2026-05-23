import "dotenv/config";
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "@prisma/client";

declare global {
  var __prisma: PrismaClient | undefined;
}

const connectionString = process.env.DB_URL ?? process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error(
    "Missing database connection string. Set DB_URL or DATABASE_URL.",
  );
}

const adapter = new PrismaPg({ connectionString });
const prisma = global.__prisma ?? new PrismaClient({ adapter });
if (process.env.NODE_ENV === "development") {
  global.__prisma = prisma;
}

export default prisma;
