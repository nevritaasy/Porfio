import express from "express";
import cors from "cors";
import compression from "compression";
import morgan from "morgan";
import prisma from "./lib/prisma.js";

import routes from "./routes/index.js";

const app = express();
const port = 8080;

const isDevelopment = process.env.NODE_ENV !== "production";
const defaultAllowedOrigins = new Set([
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "http://localhost",
  "http://127.0.0.1",
  "http://frontend:3000",
]);

function getAllowedOrigins(): string[] {
  const configuredOrigins = [
    process.env.CORS_ORIGIN,
    process.env.FRONTEND_ORIGIN,
    process.env.NGINX_ORIGIN,
  ]
    .filter((origin): origin is string => Boolean(origin?.trim()))
    .flatMap((origin) =>
      origin
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean),
    );

  return configuredOrigins.length > 0
    ? [...new Set(configuredOrigins)]
    : [...defaultAllowedOrigins];
}

const corsOptions = {
  origin(
    origin: string | undefined,
    callback: (error: Error | null, allow?: boolean) => void,
  ) {
    if (!origin) {
      callback(null, true);
      return;
    }

    const allowedOrigins = getAllowedOrigins();
    callback(null, allowedOrigins.includes(origin));
  },
  credentials: true,
};

app.use(
  morgan(isDevelopment ? "dev" : "combined", {
    immediate: false,
  }),
);

app.use(cors(corsOptions));
app.options("*", cors(corsOptions));
app.use(compression());
app.use(express.json());

// Routes
app.use("/api", routes);
app.get("/", (req, res) => {
  res.json({ message: "API is running" });
});

async function testDatabaseConnection() {
  try {
    await prisma.$connect();
    console.log("Connected to the database successfully.");
  } catch (error) {
    console.error("Failed to connect to the database:", error);
  }
}

// testDatabaseConnection();

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

// process.on("SIGINT", async () => {
//   console.log("Shutting down gracefully...");
//   await prisma.$disconnect();
//   console.log("Database disconnected");
//   process.exit(0);
// });

// process.on("SIGTERM", async () => {
//   console.log("Shutting down gracefully...");
//   await prisma.$disconnect();
//   console.log("Database disconnected");
//   process.exit(0);
// });
