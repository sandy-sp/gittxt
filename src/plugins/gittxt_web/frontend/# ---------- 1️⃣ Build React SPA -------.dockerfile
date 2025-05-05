# ---------- 1️⃣  Build React SPA ---------- #
FROM node:20-alpine AS frontend-build

WORKDIR /frontend
COPY src/plugins/gittxt_web/frontend/package.json src/plugins/gittxt_web/frontend/package-lock.json ./
RUN npm ci --silent
COPY src/plugins/gittxt_web/frontend .
RUN npm run build           # outputs to /frontend/dist

# ---------- 2️⃣  Build Python backend ----- #
FROM python:3.12-slim AS backend-build

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY src/plugins/gittxt_web/backend/requirements.txt .
RUN pip install -r requirements.txt

COPY src /app/src

# ---------- 3️⃣  Final stage with Uvicorn + Nginx ---------- #
FROM nginx:1.25-alpine AS runtime

# --- nginx
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/conf.d/default.conf.default 2>/dev/null || true

# --- backend
COPY --from=backend-build /usr/local /usr/local
COPY --from=backend-build /app /app

# --- static SPA assets
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html

# --- tini + supervisor (one‑PID approach)
RUN apk add --no-cache tini && \
    pip install --no-cache-dir supervisor

COPY deploy/supervisord.conf /etc/supervisord.conf

EXPOSE 80
ENTRYPOINT ["/sbin/tini","--","/usr/local/bin/supervisord","-c","/etc/supervisord.conf"]
