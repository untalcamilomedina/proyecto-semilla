# syntax=docker/dockerfile:1
FROM node:22.12-alpine AS base

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

# ── Desarrollo (hot reload, código montado por volumen) ──────────────
FROM base AS dev
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]

# ── Build de producción ──────────────────────────────────────────────
FROM base AS builder
# El rewrite /api/* queda fijado en build (output standalone). En producción
# nginx enruta /api directamente a Django, así que este valor solo aplica a
# fetches server-side del propio Next.
ARG DJANGO_BASE_URL=http://web:8000
ENV DJANGO_BASE_URL=${DJANGO_BASE_URL}
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ── Runtime de producción (next standalone, usuario no-root) ─────────
FROM base AS runner
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
