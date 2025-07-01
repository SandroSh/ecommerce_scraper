# Testing Documentation

This document provides comprehensive information about the testing setup and practices for the ecommerce scraper project.

## Overview

The project includes a comprehensive test suite covering:
- Unit tests for individual functions and classes
- Integration tests for module interactions
- Mock-based tests for external dependencies
- Performance and error handling tests

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_data_helpers.py        # Tests for data utilities
├── test_logger.py              # Tests for logging functionality
├── test_ee_scraper.py          # Tests for EE scraper
├── test_analysis_statistics.py # Tests for statistical analysis
└── test_integration.py         # Integration tests
```

## Running Tests

### Prerequisites

Install testing dependencies:
```bash
pip install -r requirements-test.txt
```

### Basic Test Execution

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_data_helpers.py
```

Run specific test class:
```bash
pytest tests/test_data_helpers.py::TestProduct
```

Run specific test method:
```bash
pytest tests/test_data_helpers.py::TestProduct::test_product_creation
```

### Coverage Reporting

Run tests with coverage:
```bash
pytest --cov=src --cov-report=html
```

This generates:
- Terminal coverage report
- HTML coverage report in `htmlcov/`
- XML coverage report for CI integration

### Test Markers

Run tests by category:
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Scraper-related tests
pytest -m scraper

# Analysis-related tests
pytest -m analysis
```

### Parallel Execution

Run tests in parallel (faster execution):
```bash
pytest -n auto
```

## Test Categories

### Unit Tests

Unit tests focus on testing individual functions and classes in isolation:

- **Data Helpers** (`test_data_helpers.py`):
  - Product dataclass functionality
  - JSON and CSV export functions
  - Brand extraction utilities
  - Price cleaning functions

- **Logger** (`test_logger.py`):
  - Logger configuration
  - Handler management
  - Formatter setup
  - File and console output

- **EE Scraper** (`test_ee_scraper.py`):
  - Scraper initialization
  - Price cleaning methods
  - Product parsing logic
  - Error handling

- **Statistics Analysis** (`test_analysis_statistics.py`):
  - Data preparation
  - Descriptive statistics
  - Price distribution analysis
  - Brand analysis

### Integration Tests

Integration tests verify the interaction between different modules:

- **Data Flow Integration**:
  - Scraper output to data helpers
  - Data helpers to analysis modules
  - Logger integration with other modules

- **End-to-End Pipeline**:
  - Complete data processing workflow
  - Error handling across modules
  - Performance with larger datasets

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `temp_dir`: Temporary directory for test files
- `sample_products`: Sample product data
- `sample_dataframe`: Sample pandas DataFrame
- `mock_logger`: Mock logger for testing
- `sample_html_content`: Sample HTML for scraper tests
- `sample_product_html`: Sample product detail HTML

## Mocking Strategy

The test suite uses comprehensive mocking to isolate units and avoid external dependencies:

### HTTP Requests
```python
@patch('requests.get')
def test_http_request(self, mock_get):
    mock_get.return_value = MagicMock(content='<html>...</html>')
    # Test implementation
```

### File Operations
```python
@patch('builtins.open', new_callable=mock_open)
@patch('os.makedirs')
def test_file_operations(self, mock_makedirs, mock_file):
    # Test file operations
```

### Logging
```python
@patch('logging.getLogger')
def test_logging(self, mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    # Test logging functionality
```

## Test Data

### Sample Products
```python
sample_products = [
    {
        'name': 'iPhone 13 Pro',
        'price': 999,
        'brand': 'Apple',
        'category': 'phones',
        'description': 'Latest iPhone model'
    },
    # ... more products
]
```

### Sample HTML
```html
<div class="product">
    <h3 class="sc-3ff391e0-4">iPhone 13 Pro</h3>
    <a href="/mobile-phone/iphone-13-pro">View Details</a>
    <span class="sc-3ff391e0-6">999₾</span>
</div>
```

## Best Practices

### Test Organization
- One test class per module/class
- Descriptive test method names
- Use of `setUp()` and `tearDown()` for fixtures
- Proper cleanup of temporary files

### Assertions
- Use specific assertions (`assertEqual`, `assertIn`, etc.)
- Test both positive and negative cases
- Verify error conditions and edge cases

### Mocking
- Mock external dependencies (HTTP, files, databases)
- Use `unittest.mock.patch` for method-level mocking
- Verify mock calls when testing interactions

### Coverage
- Aim for >90% code coverage
- Focus on critical business logic
- Test error handling paths

## Continuous Integration

The test suite is designed to run in CI environments:

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=src --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Local Development
```bash
# Run tests before committing
pytest --cov=src --cov-fail-under=90

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m unit        # Only unit tests
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `sys.path` includes project root
2. **Mock Issues**: Verify mock setup and return values
3. **File Permission Errors**: Use temporary directories for file tests
4. **Network Timeouts**: Mock all HTTP requests

### Debug Mode
```bash
# Run with debug output
pytest -s -v --tb=long

# Run single test with debugger
pytest -s tests/test_data_helpers.py::TestProduct::test_product_creation
```

## Performance Testing

The test suite includes performance benchmarks:

```bash
# Run performance tests
pytest -m performance

# Profile test execution
pytest --durations=10
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain >90% coverage
4. Add integration tests for new workflows
5. Update this documentation

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<method_name>_<scenario>`

Example:
```python
class TestDataProcessor(unittest.TestCase):
    def test_process_file_success(self):
        # Test successful file processing
        
    def test_process_file_invalid_format(self):
        # Test error handling for invalid format
``` 