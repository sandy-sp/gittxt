FROM python:3.11-slim

WORKDIR /app

# Copy everything into /app
COPY . .

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies using pyproject.toml
RUN poetry install --no-root

# Set PYTHONPATH so /api sees its own modules
ENV PYTHONPATH=/app/api

# Set PYTHONPATH so gittxt sees its own modules
ENV PYTHONPATH=/app/gittxt

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
