.PHONY: all clean cli-tests api-tests

# Run all tests
all: cli-tests api-tests

# Run CLI tests
cli-tests:
	@echo "🔧 Generating test repo in tests/cli/test_repo..."
	pytest cli --maxfail=5 --disable-warnings -v

# Run API tests
api-tests:
	@echo "🔧 Generating test repo in tests/api/test_repo..."
	pytest api --maxfail=5 --disable-warnings -v

# Clean up generated test outputs
clean:
	@echo "🗑️ Cleaning up test repo and outputs..."
	rm -rf tests/cli/cli_test_outputs tests/cli/test_outputs tests/cli/test_outputs_lite tests/cli/test_repo tests/cli/test_zip_output tests/api/test_repo tests/api/test_repo.zip