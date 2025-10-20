FROM python:3.11-slim

# Optimization of layers and assembly speed
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/backend

RUN apt-get update && apt-get install -y docker-cli && \
    apt-get install -y --no-install-recommends \
    git build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Open port FastAPI
EXPOSE 8000
