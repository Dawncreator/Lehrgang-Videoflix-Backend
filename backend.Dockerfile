FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt update && apt install -y \
    ffmpeg \
    postgresql-client \
    gcc \
    libpq-dev \
    python3-dev \
    build-essential \
    && apt clean

WORKDIR /app

# Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Project
COPY . /app/

# Collect static files (ignore failure during build)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "core.wsgi", "-b", "0.0.0.0:8000"]
