FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     gcc     libpq-dev     && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the app
RUN useradd -m -u 10001 appuser

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations
COPY src /app/src
COPY tests /app/tests

USER appuser

EXPOSE 8000

# Default command (docker-compose overrides it, but this keeps the image runnable)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
