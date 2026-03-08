FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY .env.example ./.env.example

EXPOSE 8000

# Default Ollama configuration; override via env vars if needed.
ENV API_BASE=http://host.docker.internal:11434/v1 \
    MODEL_NAME=llama3.2 \
    API_KEY=ollama \
    CORS_ORIGINS=http://localhost:4200

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

