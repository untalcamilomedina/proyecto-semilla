FROM python:3.12 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements/ /build/requirements/

RUN pip install --upgrade pip wheel \
  && pip wheel --wheel-dir /build/wheels -r /build/requirements/prod.txt


FROM python:3.12 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONPATH=/app/src \
  DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  libpq5 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY src/ /app/src/
COPY manage.py /app/manage.py

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--chdir", "/app/src"]


FROM runtime AS dev

ENV DJANGO_SETTINGS_MODULE=config.settings.dev

COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r /app/requirements/dev.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
