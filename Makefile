PROJECT_SLUG ?= proyecto_semilla
PYTHON ?= python3
MANAGE ?= $(PYTHON) manage.py
COMPOSE ?= docker compose -f compose/docker-compose.yml

.PHONY: init dev lint fmt typecheck test build migrate seed deploy audit frontend-install frontend-dev frontend-test frontend-build api-schema

init:
	$(PYTHON) scripts/bootstrap.py

dev:
	$(COMPOSE) up --build

lint:
	ruff check src tests
	black --check src tests
	isort --check-only src tests
	djlint src/templates src/**/*.html --lint
	bandit -c pyproject.toml -r src

fmt:
	ruff check --fix src tests
	ruff format src tests
	isort src tests
	black src tests
	djlint src/templates src/**/*.html --reformat

typecheck:
	mypy src

test:
	pytest

build:
	docker build -t $(PROJECT_SLUG):latest .

migrate:
	$(COMPOSE) exec web python manage.py migrate

seed:
	$(COMPOSE) exec web python manage.py seed_demo

audit:
	pip-audit -r requirements/dev.txt
	safety check -r requirements/dev.txt

api-schema:
	$(COMPOSE) exec web python manage.py spectacular --file openapi.yaml
	@echo "Esquema OpenAPI exportado a openapi.yaml"

deploy:
	bash ./deploy/flyio/deploy.sh

frontend-install:
	cd frontend && npm ci

frontend-dev:
	cd frontend && npm run dev

frontend-test:
	cd frontend && npm run lint && npm run type-check && npm run test

frontend-build:
	cd frontend && npm run build
