.PHONY: help install-dev install download-models test test-cov lint format check clean run-verify-cleaner reinstall

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install-dev:  ## Install dev dependencies
	pip install .[dev]

install:  ## Install main dependencies
	pip install .

download-models: ## Download necessary models for spaCy
	python -m spacy download en_core_web_sm

test:  ## Run tests using pytest
	PYTHONPATH=.  pytest

test-cov:  ## Run tests with coverage report
	PYTHONPATH=src python -m pytest tests/ \
		--cov=src \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov-report=term-missing

lint:  ## Run lint checks using flake8 and mypy
	flake8 src/ tests/
	mypy src/

format:  ## Format code using black and isort
	black src/ tests/
	isort src/ tests/

check:  ## Check code style without modifying files
	black --check src/ tests/
	isort --check-only src/ tests/

clean:  ## Remove venv, Python cache, and build files
	rm -rf .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type d -name '.pytest_cache' -exec rm -r {} +
	rm -rf .mypy_cache .coverage.* htmlcov dist build *.egg-info

run-verify-cleaner:  ## Run verify_new_text_cleaner.py with PYTHONPATH set
	PYTHONPATH=. python scripts/verify_new_text_cleaner.py


reinstall: clean ## Reinstall the project in a fresh virtual environment
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -e .[dev]
