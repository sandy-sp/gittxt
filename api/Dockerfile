FROM python:3.11-slim

WORKDIR /app

# Copy everything into /app
COPY . .

# Install Poetry
RUN pip install --no-cache-dir poetry

# ⬅️ Install your local Gittxt FIRST
RUN poetry install

# ✅ Then install external API deps
RUN pip install --no-cache-dir --upgrade pip \
 && pip install -r api/requirements.txt

# Set PYTHONPATH so /api sees its own modules
ENV PYTHONPATH=/app/api

# Set PYTHONPATH so gittxt sees its own modules
ENV PYTHONPATH=/app/src/gittxt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
