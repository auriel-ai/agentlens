.PHONY: test install dev clean

# Default target
all: install test

# Install the package
install:
	pip3 install -e .

# Install development dependencies
dev:
	pip3 install -e ".[dev]"
	pip3 install pytest pytest-cov black isort flake8

# Run tests
test:
	python3 -m unittest discover -s tests

# Run tests with coverage
coverage:
	python3 -m pytest --cov=agentlens tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.pyc" -delete

# Format code
format:
	python3 -m isort agentlens tests examples
	python3 -m black agentlens tests examples

# Run linting
lint:
	python3 -m flake8 agentlens tests examples

# Build package
build: clean
	python3 -m build

# Run examples
examples:
	./setup_and_run.sh

# Help target
help:
	@echo "Available targets:"
	@echo "  install    - Install the package"
	@echo "  dev        - Install development dependencies"
	@echo "  test       - Run tests"
	@echo "  coverage   - Run tests with coverage"
	@echo "  clean      - Clean build artifacts"
	@echo "  format     - Format code"
	@echo "  lint       - Run linting"
	@echo "  build      - Build package"
	@echo "  examples   - Run examples"
	@echo "  help       - Show this help message" 