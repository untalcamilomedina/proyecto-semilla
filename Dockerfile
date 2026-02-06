FROM python:3.12.8-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements/ /build/requirements/

RUN pip install --upgrade pip==24.3.1 wheel \
  && pip wheel --wheel-dir /build/wheels -r /build/requirements/prod.txt


FROM python:3.12.8-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONPATH=/app/src \
  DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  libpq5 curl \
  && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system app && useradd --system --gid app --create-home app

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY --chown=app:app src/ /app/src/
COPY --chown=app:app manage.py /app/manage.py

USER app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--chdir", "/app/src", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]


FROM runtime AS dev

ENV DJANGO_SETTINGS_MODULE=config.settings.dev

# Dev stage runs as root for convenience
USER root

COPY requirements/ /app/requirements/
RUN pip install --default-timeout=100 --no-cache-dir -r /app/requirements/dev.txt

USER app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
