.PHONY: test lint format build check cache

test:
	@echo "🔧 Generating test repo in tests/test_repo..."
	poetry run python tests/generate_test_repo.py

	@echo "🧪 Running Gittxt test suite..."
	poetry run pytest tests -v

	@echo "🗑️ Cleaning up test repo and outputs..."
	rm -rf tests/test_repo
	rm -rf tests/test_outputs*
	rm -rf tests/cli_test_outputs
	rm -rf tests/test_zip_output

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

api:
	poetry run uvicorn src.gittxt_api.main:app --reload

ui:
	npm run dev