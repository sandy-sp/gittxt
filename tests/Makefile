.PHONY: all clean cli-tests api-tests

# Run all tests
all: cli-tests api-tests

# Run CLI tests
cli-tests:
    @echo "Running CLI tests..."
    pytest tests/cli --maxfail=5 --disable-warnings -v

# Run API tests
api-tests:
    @echo "Running API tests..."
    pytest tests/api --maxfail=5 --disable-warnings -v

# Clean up generated test outputs
clean:
    @echo "Cleaning up test outputs..."
    rm -rf tests/cli/test_repo tests/cli/cli_test_outputs tests/api/test_repo tests/api/test_repo.zip