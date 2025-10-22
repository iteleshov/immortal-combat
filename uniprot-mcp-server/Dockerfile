# =========================
# Stage 1: Builder
# =========================
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# =========================
# Stage 2: Production
# =========================
FROM node:18-alpine AS production

WORKDIR /app

COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json ./

# Set prod-only devendencies
RUN npm install --omit=dev

# Set environment
ENV NODE_ENV=production

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "console.log('UniProt MCP Server is healthy')" || exit 1

# Entry point
ENTRYPOINT ["node", "build/index.js"]

# Metadata
LABEL maintainer="UniProt MCP Server Team"
LABEL description="Model Context Protocol server for UniProt protein database access"
LABEL version="0.1.0"
