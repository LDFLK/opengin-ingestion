.PHONY: format-fix format-check

format-fix:
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py
	isort .
	black .

format-check:
	isort --check .
	black --check .
	flake8 .
