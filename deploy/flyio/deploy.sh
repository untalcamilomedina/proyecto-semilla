#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="deploy/flyio/fly.toml"

if ! command -v flyctl >/dev/null 2>&1; then
  echo "flyctl not found. Install it from https://fly.io/docs/flyctl/"
  exit 1
fi

APP_NAME="${FLY_APP_NAME:-$(grep '^app' "$CONFIG_PATH" | awk '{print $3}' | tr -d '\"')}"

echo "Deploying app: $APP_NAME"
flyctl deploy -c "$CONFIG_PATH" --app "$APP_NAME"

echo "Running migrations (public + tenant schemas)..."
flyctl ssh console -c "python manage.py migrate_tenants --noinput" --app "$APP_NAME"

echo "Collecting static files..."
flyctl ssh console -c "python manage.py collectstatic --noinput" --app "$APP_NAME"

echo "Done."

