#!/bin/bash
# scripts/generate-api.sh

# Exit on error
set -e

echo "Generating OpenAPI schema..."
docker exec compose-web-1 python manage.py spectacular --file schema.yml --validate

echo "Generating TypeScript client types..."
# Note: This assumes openapi-typescript is installed in frontend or available via npx
cd frontend
if [ -f "schema.yml" ]; then rm schema.yml; fi
docker cp compose-web-1:/app/schema.yml .

npx openapi-typescript schema.yml -o src/types/api.ts

echo "API Generation complete! Types saved to frontend/src/types/api.ts"
rm schema.yml
