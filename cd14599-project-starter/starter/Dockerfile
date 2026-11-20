# Lightweight image for the Udatracker backend (Flask API + static frontend).
# Build and run from this directory (starter/):
#   docker build -t udatracker .
#   docker run --rm -p 8000:8000 udatracker
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached until requirements change.
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend
COPY frontend frontend

# Run as a non-root user.
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["python", "-m", "backend.app"]
