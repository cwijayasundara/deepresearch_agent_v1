.PHONY: test lint fmt check

test:
	python -m pytest tests/ -v --tb=short

lint:
	python -m ruff check src/ tests/
	python3 .claude/linters/layer_deps.py src/
	python3 .claude/linters/file_size.py src/

fmt:
	python -m ruff format src/ tests/

check: lint test
