FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (for cache efficiency)
COPY requirements.txt .

# Install dependencies including gittxt from PyPI
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API source code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
