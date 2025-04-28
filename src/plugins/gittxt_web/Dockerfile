# syntax=docker/dockerfile:1
FROM python:3.12-slim

# System-level deps
RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*

# Set working dir
WORKDIR /app

# Copy poetry files and install deps first
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction

# Copy all plugin source code
COPY src/plugins/gittxt_web /app/

# Expose FastAPI port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
