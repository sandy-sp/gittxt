# gittxt-api/Dockerfile
FROM python:3.11-slim

# System setup
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full API app
COPY . /app

# Optional: expose port
EXPOSE 8000

# Entrypoint
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]