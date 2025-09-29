FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (avoid obsolete package names)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    pkg-config \
    python3-dev \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-xlib-2.0-dev \
    shared-mime-info \
    libjpeg-dev \
    zlib1g-dev \
&& rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create media/static dirs and collect static files
RUN mkdir -p /app/media /app/staticfiles && python manage.py collectstatic --noinput || true

# Expose port and run
EXPOSE 8000
CMD ["gunicorn", "inventory_app.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

