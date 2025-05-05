# ────────────────────────────────────────────────
#  Gittxt-web  ▸  production image
# ────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# — System packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ───────────── 1 ▸ Python dependencies  ─────────
# Upgrade tooling first
RUN pip install --upgrade pip setuptools wheel

# Core library published to PyPI
RUN pip install "gittxt>=1.7.7"

# Project deps (layer cached unless these files change)
COPY pyproject.toml poetry.lock* /app/
RUN pip install .                      # builds from pyproject

# ───────────── 2 ▸ Application code  ────────────
COPY . /app

# ───────────── 3 ▸ Runtime config  ──────────────
EXPOSE 8000
CMD ["uvicorn", "gittxt_web.main:app", "--host", "0.0.0.0", "--port", "8000"]
