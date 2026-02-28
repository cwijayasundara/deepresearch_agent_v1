.PHONY: test lint fmt check

test:
	python -m pytest backend/tests/ -v --tb=short

lint:
	python -m ruff check backend/
	python3 .claude/linters/layer_deps.py backend/
	python3 .claude/linters/file_size.py backend/

fmt:
	python -m ruff format backend/

check: lint test
