FROM node:20-alpine AS builder
WORKDIR /app

# Avoid failing install when schema is not present yet; generate later explicitly.
ENV PRISMA_SKIP_POSTINSTALL_GENERATE=1
ARG DB_URL=postgresql://dummy:dummy@localhost:5432/porfiodb
ENV DB_URL=${DB_URL}

COPY package.json package-lock.json ./
RUN npm ci

COPY prisma.config.ts ./
COPY tsconfig.json ./
COPY prisma ./prisma
COPY src ./src
COPY ai_services ./ai_services

RUN npx prisma generate
RUN npx tsc --rootDir src --outDir dist

# Keep only production dependencies for runtime image.
RUN npm prune --omit=dev

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=8080
ENV VENV_PATH=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN apk add --no-cache python3 py3-pip py3-virtualenv tesseract-ocr
RUN addgroup -S app && adduser -S app -G app

COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/package-lock.json ./package-lock.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/prisma.config.ts ./prisma.config.ts
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/ai_services ./ai_services

RUN python3 -m venv "${VENV_PATH}" \
	&& "${VENV_PATH}/bin/pip" install --no-cache-dir --upgrade pip \
	&& "${VENV_PATH}/bin/pip" install --no-cache-dir -r ai_services/requirements.txt

RUN mkdir -p /app/uploads && chown -R app:app /app/uploads

EXPOSE 8080
USER app

CMD ["sh", "-c", "./node_modules/.bin/prisma migrate deploy && exec node dist/index.js"]
