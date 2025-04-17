.PHONY: all clean cli api

# Run all tests
all: cli api

# Run CLI tests
cli::
	@echo "🔧 Generating test repository for CLI tests..."
	python cli/generate_test_repo.py
	@echo "🔧 Generating test repo in tests/cli/test_repo..."
	poetry run pytest cli -v
	@echo "🗑️ Cleaning up test repo and outputs..."
	rm -rf cli/cli_test_outputs cli/test_outputs cli/test_outputs_lite cli/test_repo cli/test_zip_output cli/test_repo

# Run API tests
api::
	@echo "🔧 Generating test repository for API tests..."
	python api/generate_test_repo.py
	@echo "🔧 Generating test repo in tests/api/test_repo..."
	poetry run pytest api -v
	@echo "🗑️ Cleaning up test repo and outputs..."
	rm -rf api/test_repo.zip

# Clean up generated test outputs
clean:
	@echo "🗑️ Cleaning up test repo and outputs..."
	rm -rf cli/cli_test_outputs cli/test_outputs cli/test_outputs_lite cli/test_repo cli/test_zip_output cli/test_repo
	rm -rf api/test_repo api/test_repo.zip