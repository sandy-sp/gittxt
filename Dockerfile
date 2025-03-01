FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install
CMD ["poetry", "run", "uvicorn", "src.gittxt_ui.app:app", "--host", "0.0.0.0", "--port", "8000"]
