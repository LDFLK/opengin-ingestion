SHELL := /bin/bash

# Default PYTHONPATH to include src
export PYTHONPATH := src

.PHONY: test
test:
	pytest tests/

.PHONY: run-tests
run-tests: test

.PHONY: run-integration-tests
run-integration-tests:
	# Running integration tests. Use UPDATE_GOLDEN_DATA=1 to update snapshots.
	pytest integration_tests/

.PHONY: run-server-ui
run-server-ui:
	# Running the backend server for the UI
	uvicorn opengin.server.main:app --host 0.0.0.0 --port 8001 --reload

.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

.PHONY: format-fix format-check

format-fix:
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py
	isort .
	black .

format-check:
	isort --check .
	black --check .
	flake8 .
