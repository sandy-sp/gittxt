.PHONY: test lint format check

check:
	poetry check

lint:
	ruff .
	black --check .

format:
	black .

test:
	poetry run pytest tests/

cache:
	find . -type d -name "__pycache__" -exec rm -r {} +