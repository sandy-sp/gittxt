FROM python:3.12-slim
WORKDIR /app
COPY src/plugins/gittxt_web/backend/requirements.txt .
RUN pip install -r requirements.txt
COPY src /app/src
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "gittxt_web.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
