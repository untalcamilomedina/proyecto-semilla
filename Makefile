PROJECT_SLUG ?= acme_saas
PYTHON ?= python3
MANAGE ?= $(PYTHON) manage.py
COMPOSE ?= docker compose -f compose/docker-compose.yml

.PHONY: dev lint fmt typecheck test build migrate seed deploy audit frontend-install frontend-dev

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

deploy:
	bash ./deploy/flyio/deploy.sh

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev
