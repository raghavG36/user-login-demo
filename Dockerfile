# Production-ready Dockerfile: Python 3.11, non-root user, layer caching
FROM python:3.11-slim

# Prevent Python from writing pyc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cloud Run / flexible port (default 8080)
ENV PORT=8080

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (do not copy .env into image; use runtime env)
COPY app/ ./app/

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

# Gunicorn with Uvicorn worker; bind to 0.0.0.0 for external access
CMD exec gunicorn app.main:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${PORT}" \
    --access-logfile - \
    --capture-output
