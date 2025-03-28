.PHONY: test lint format check

test:
	@echo "🔧 Generating test repo in tests/test_repo..."
	poetry run python tests/generate_test_repo.py

	@echo "🧪 Running Gittxt test suite..."
	poetry run pytest tests -v

lint:
	@echo "🧹 Linting with ruff..."
	ruff .
	black --check .

format:
	@echo "🎨 Formatting with black..."
	black .

clean:
	@echo "🗑️ Cleaning up test repo and outputs..."
	rm -rf tests/test_repo
	rm -rf tests/test_outputs*
	rm -rf tests/cli_test_outputs
	rm -rf tests/test_zip_output

build:
	@echo "📦 Building package with Poetry..."
	poetry build

check:
	poetry check

cache:
	find . -type d -name "__pycache__" -exec rm -r {} +