# Developer Guide

Welcome to the **OpenGIN Tracer** developer guide. This document provides best practices for contributing to the codebase, focusing on setting up your environment, running tests, and managing third-party dependencies effectively.

## 1. Environment Setup

We recommend using `micromamba` or `conda` to manage the development environment.

### Prerequisites
- Python 3.11+
- Micromamba or Conda

### Installation
1. Create the environment using the provided `environment.yml`:
   ```bash
   # Using micromamba
   micromamba env create -f python/environment.yml -y
   micromamba activate doctracer

   # Using conda
   conda env create -f python/environment.yml
   conda activate doctracer
   ```

2. Alternatively, install manually in editable mode with all dependencies:
   ```bash
   cd python
   pip install -e ".[dev,tracer]"
   ```

## 2. Running Tests

We use `pytest` for our testing framework. Our test suite includes unit tests for individual components and integration tests for end-to-end workflows.

### Running the Suite
Execute all tests from the `python` directory:
```bash
cd python
pytest tests
```

### Test Structure
- **Unit Tests**: Located in `tests/test_agents.py`, `tests/test_fs_manager.py`, etc. These test isolated logic.
- **Integration Tests**: Located in `tests/test_integration.py`. These verify the full pipeline flow.

## 3. Mocking & External Dependencies (Critical)

A core principle of our testing strategy is **avoiding external API calls** during tests. 

### Why Mock?
- **Cost**: APIs like Google Gemini incur costs per request.
- **Reliability**: External services can flounder or rate-limit, causing flaky CI builds.
- **Speed**: Network requests are slow; mocks are instant.

### How We Mock
We use `unittest.mock.patch` to intercept calls to external services.

**Example: Mocking Gemini API**
Instead of allowing `extract_data_with_gemini` to hit Google's servers, we patch it to return a pre-defined JSON string.

```python
from unittest.mock import patch

# Correct: Patch the function WHERE IT IS USED
@patch("opengin.tracer.agents.scanner.extract_data_with_gemini")
def test_scanner(mock_extract, fs_manager):
    # Setup mock return value
    mock_extract.return_value = '{"tables": []}'
    
    # Run code that calls the external API
    agent = Agent1(fs_manager)
    agent.run(...)
    
    # Assert the mock was called, but no real request was made
    mock_extract.assert_called_once()
```

### Best Practices
1.  **Always Mock `google.genai`**: never let a test function initialize a real Client or make a `generate_content` call.
2.  **Patch where it's used**: If `module_a.py` imports `foo` from `module_b`, patch `module_a.foo`, not `module_b.foo`.
3.  **Use `conftest.py`**: Common mocks (like fake LLM responses) are defined as fixtures in `tests/conftest.py`.

## 4. Code Style & Linting

We enforce code quality using `flake8`, `black`, and `isort`.

### Running Checks
```bash
cd python
make format-check
```

### Auto-Formatting
To automatically fix formatting (black/isort) and clean up unused imports (autoflake):
```bash
cd python
make format-fix
```

**Note**: Please ensure your code passes `make format-check` before submitting a PR.
