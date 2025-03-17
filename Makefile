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