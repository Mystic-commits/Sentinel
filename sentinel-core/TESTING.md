# Testing Guide

This document describes how to run tests and maintain code quality for Sentinel.

## Quick Start

```bash
cd sentinel-core

# Install dependencies with dev packages
poetry install

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=sentinel_core --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Structure

```
sentinel-core/tests/
├── conftest.py              # Pytest fixtures
├── utils/
│   ├── mock_filesystem.py   # Test filesystem
│   └── fake_generator.py    # Fake data generator
├── test_scanner.py          # Scanner tests
├── test_safety.py           # Safety validator tests
├── test_executor.py         # Executor tests
└── test_cleanpc.py          # Clean PC pipeline tests
```

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test File
```bash
pytest tests/test_scanner.py
```

### Specific Test Class
```bash
pytest tests/test_scanner.py::TestFileTypeDetection
```

### Specific Test
```bash
pytest tests/test_scanner.py::TestFileTypeDetection::test_image_detection
```

### With Verbose Output
```bash
pytest -v
```

### With Coverage
```bash
pytest --cov=sentinel_core --cov-report=term-missing
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

## Test Utilities

### MockFilesystem

Creates temporary directories for isolated testing:

```python
def test_something(mock_fs):
    # Create test files
    file_path = mock_fs.create_file("test/file.txt", content="Hello")
    
    # Create old files
    old_file = mock_fs.create_file("old.txt", age_days=60)
    
    # Test your code
    scanner = Scanner(mock_fs.get_path("test"))
    result = scanner.scan()
    
    # Cleanup happens automatically
```

### FakeDirectoryGenerator

Generates realistic test data:

```python
def test_cleanup(mock_fs, fake_generator):
    # Generate complete structure
    stats = fake_generator.generate_complete_structure(mock_fs)
    
    # Or generate specific parts
    fake_generator.generate_downloads(mock_fs)
    fake_generator.generate_desktop(mock_fs)
```

### Pytest Fixtures

Available fixtures:
- `mock_fs` - Empty mock filesystem
- `fake_generator` - Fake data generator
- `populated_fs` - Pre-populated filesystem
- `minimal_fs` - Minimal test data

## Linting and Formatting

### Ruff (Linting)
```bash
# Check for issues
poetry run ruff check .

# Auto-fix issues
poetry run ruff check --fix .
```

### Black (Formatting)
```bash
# Check formatting
poetry run black --check .

# Format files
poetry run black .
```

### Mypy (Type Checking)
```bash
poetry run mypy sentinel_core
```

### All Checks
```bash
# Run all quality checks
poetry run ruff check .
poetry run black --check .
poetry run mypy sentinel_core
poetry run pytest
```

## Pre-commit Hooks

Install pre-commit hooks to run checks automatically:

```bash
# Install pre-commit
pip install pre-commit

# Set up git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Writing Tests

### Test Structure

```python
class TestFeatureName:
    """Tests for feature X."""
    
    def test_basic_case(self, mock_fs):
        """Test description."""
        # Arrange
        setup_data()
        
        # Act
        result = do_something()
        
        # Assert
        assert result == expected
```

### Async Tests

```python
import pytest

class TestAsyncFeature:
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async functionality."""
        result = await async_function()
        assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("file.txt", FileType.DOCUMENT),
    ("image.png", FileType.IMAGE),
    ("video.mp4", FileType.VIDEO),
])
def test_file_types(input, expected):
    """Test various file types."""
    assert detect_type(input) == expected
```

## Coverage Goals

- **Minimum:** 80% code coverage
- **Target:** 90% code coverage
- **Critical modules:** 95%+ coverage
  - Scanner
  - Safety validator
  - Executor

## CI/CD

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests

GitHub Actions workflow:
- Linting (ruff, black, mypy)
- Tests on multiple platforms (Ubuntu, macOS, Windows)
- Python versions: 3.11, 3.12
- Coverage reporting

## Troubleshooting

### Tests Failing Locally

1. **Clean cache:**
   ```bash
   pytest --cache-clear
   rm -rf .pytest_cache __pycache__
   ```

2. **Reinstall dependencies:**
   ```bash
   poetry install
   ```

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.11+
   ```

### Import Errors

Make sure you're in the correct directory:
```bash
cd sentinel-core
poetry run pytest
```

### Async Warnings

Install pytest-asyncio:
```bash
poetry add --group dev pytest-asyncio
```

## Best Practices

1. **Write tests first:** Use TDD when possible
2. **Test one thing:** Each test should verify one behavior
3. **Use descriptive names:** `test_scanner_skips_hidden_files`
4. **Clean up:** Use fixtures for setup/teardown
5. **Mock external dependencies:** Don't hit real APIs
6. **Test edge cases:** Null, empty, max values
7. **Keep tests fast:** <5 seconds for unit tests

## Examples

See existing tests for examples:
- `tests/test_scanner.py` - File scanning
- `tests/test_safety.py` - Safety validation
- `tests/test_executor.py` - File operations
- `tests/test_cleanpc.py` - Full pipeline
