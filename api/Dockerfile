FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git ffmpeg libsndfile1 \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    libopenblas-dev liblapack-dev gfortran libjpeg-dev zlib1g-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY pipeline/ ./pipeline/
COPY api/ ./api/
COPY migrations/ ./migrations/

RUN useradd -m appuser && mkdir -p /app/weights && chown -R appuser:appuser /app/weights
USER appuser

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]