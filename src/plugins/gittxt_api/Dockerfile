FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install git (for clone ops), and other dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Poetry if you use it (optional), else fallback to pip requirements
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry && poetry install --no-root

# Copy source
COPY . .

# Expose API port
EXPOSE 8000

# Default: Run API
CMD ["uvicorn", "plugins.gittxt_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
