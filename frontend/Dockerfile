# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# Compiles TypeScript and produces the static dist/ bundle.
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (layer cache)
COPY package.json package-lock.json* ./
RUN npm ci --frozen-lockfile

# Build production bundle
COPY . .
RUN npm run build


# ── Stage 2: Production ───────────────────────────────────────────────────────
# Serves the static build with nginx. No Node.js in the final image.
FROM nginx:1.27-alpine AS production

# SPA routing: redirect all routes to index.html
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf

# Copy built static files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]


# ── Stage 4: Development ──────────────────────────────────────────────────────
FROM node:20-alpine AS development

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
