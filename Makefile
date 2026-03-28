.PHONY: up down build logs test lint typecheck shell

up:
	@echo "🚀 Starting stack... first run may take 5-12 minutes"
	docker-compose up

down:
	docker-compose down

build:
	@echo "🚀 Building stack... first run may take 5-12 minutes"
	docker-compose up --build

logs:
	docker-compose logs -f api

test:
	docker-compose exec api uv run pytest

lint:
	docker-compose exec api uv run ruff check src/ tests/

typecheck:
	docker-compose exec api uv run mypy src/

shell:
	docker-compose exec api bash
