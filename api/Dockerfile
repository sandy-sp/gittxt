FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Copy Gittxt CLI source and API
COPY ./src ./src
COPY ./api ./

# Install requirements and local package
RUN pip install --no-cache-dir --upgrade pip \
 && pip install -r requirements.txt \
 && pip install ./src

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
