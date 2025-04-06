FROM python:3.11-slim

# Set working dir inside the container
WORKDIR /app

# Copy the full project repo (src/, api/, pyproject.toml, etc.)
COPY . .

# Install core dependencies first
RUN pip install --no-cache-dir --upgrade pip \
 && pip install -r api/requirements.txt \
 && pip install .

# Set environment variables
ENV PYTHONPATH=/app/api

# Expose FastAPI port
EXPOSE 8000

# Run the API app inside api/
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
