# Use an official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install -r requirements.txt

# Expose FastAPI default port
EXPOSE 8000

# Run the API with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
