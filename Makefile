.PHONY: lint format build check cache

lint:
	poetry run ruff check . --fix

format:
	poetry run black .

build:
	@echo "📦 Building package with Poetry..."
	poetry build

check:
	poetry check
	poetry run ruff check .
	poetry run black . --check

cache:
	find . -type d -name "__pycache__" -exec rm -r {} +
