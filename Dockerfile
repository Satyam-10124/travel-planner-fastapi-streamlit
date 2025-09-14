FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1         PIP_NO_CACHE_DIR=1         PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app
COPY data ./data
# Copy example env as .env for default settings (safe to override via Railway vars)
COPY env.example .env

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
