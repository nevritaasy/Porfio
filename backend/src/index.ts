import express from "express";
import cors from "cors";
import compression from "compression";
import morgan from "morgan";
import prisma from "./lib/prisma.js";

import routes from "./routes/index.js";

const app = express();
const port = 8080;

app.use(
  cors({
    origin: true,
    credentials: true,
  }),
);
app.use(compression());
app.use(morgan("combined"));
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

testDatabaseConnection();

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

process.on("SIGINT", async () => {
  console.log("Shutting down gracefully...");
  await prisma.$disconnect();
  console.log("Database disconnected");
  process.exit(0);
});

process.on("SIGTERM", async () => {
  console.log("Shutting down gracefully...");
  await prisma.$disconnect();
  console.log("Database disconnected");
  process.exit(0);
});
