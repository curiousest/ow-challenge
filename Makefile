# Install dependencies
install:
	@echo "Installing dependencies..."
	uv sync
	uv pip install -U pip setuptools wheel
	uv pip install torch>2.0.0

# Run tests
test:
	@echo "Running Python unit tests..."
	uv run pytest tests/

# Run performance comparison
perf:
	@echo "Running performance comparison..."
	PYTHONPATH=$$PYTHONPATH:src/ uv run python tests/compare_performance.py

# Run the FastAPI application
run:
	@echo "Starting FastAPI application..."
	PYTHONPATH=$$PYTHONPATH:src/ uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# Clean up cache files
clean:
	@echo "Cleaning up cache files..."
	rm -rf __pycache__/ 