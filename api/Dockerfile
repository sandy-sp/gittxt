FROM python:3.11-slim

WORKDIR /app

# Copy everything into /app
COPY . .

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies using pyproject.toml
RUN poetry install --no-root

RUN mkdir -p /app/api/outputs /app/api/uploads

ENV PYTHONPATH=/app/api:/app/gittxt

EXPOSE 8000

WORKDIR /app/api
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

