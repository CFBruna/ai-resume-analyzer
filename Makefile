.PHONY: up down build logs test lint typecheck shell

up:
	docker-compose up

down:
	docker-compose down

build:
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
