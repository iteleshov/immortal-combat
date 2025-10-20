FROM python:3.11-slim

# Optimization of layers and assembly speed
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/immortal-combat

RUN apt-get update && apt-get install -y docker-cli && \
    apt-get install -y --no-install-recommends \
    git build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app .

# Open port FastAPI
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
