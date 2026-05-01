FROM python:3.12-slim

# Environment variables

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY . /app/

RUN addgroup --system app && adduser --system --group app
USER app

EXPOSE 8000

# -----------------------------
# Start production server
# -----------------------------
CMD ["gunicorn", "src.config.wsgi:application", "--bind", "0.0.0.0:8000"]
