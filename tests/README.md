# Aria2TUI Testing Suite

This directory contains the comprehensive testing suite for the aria2tui project.

## Overview

The testing suite is organized into multiple categories:
- **Unit tests**: Test individual functions and modules in isolation
- **Integration tests**: Test RPC communication with mocked aria2 server
- **End-to-end tests**: Test complete workflows using kitty terminal control

## Test Structure

```
tests/
├── conftest.py                # Pytest configuration and shared fixtures
├── unit/                      # Pure unit tests (~220 tests)
│   ├── test_format_utils.py  # Formatting utilities (35 tests)
│   ├── test_aria2c_wrapper.py # JSON-RPC request builders (40 tests)
│   ├── test_data_transformation.py # Data transformation (50 tests)
│   ├── test_parsing.py       # URL/path parsing (25 tests)
│   ├── test_operation_class.py # Operation class (15 tests)
│   ├── test_batch_operations.py # Batch operations (20 tests)
│   ├── test_data_flattening.py # Flatten/unflatten utils (15 tests)
│   └── test_config_loading.py # Config loading (20 tests)
├── integration/               # Integration tests (~125 tests)
│   ├── test_rpc_communication.py # RPC with mock server (30 tests)
│   ├── test_download_operations.py # Download workflows (35 tests)
│   ├── test_file_operations.py # File handling (25 tests)
│   ├── test_config_integration.py # Config integration (15 tests)
│   └── test_graphing.py      # Graph generation (20 tests)
├── e2e/                       # End-to-end tests (~27 tests)
│   ├── kitty_helper.py       # Terminal controller
│   ├── test_smoke.py         # Basic smoke tests (5 tests)
│   ├── test_download_display.py # Download UI (8 tests)
│   ├── test_menu_navigation.py # Menu navigation (6 tests)
│   └── test_operations_ui.py # Operation UI (8 tests)
├── fixtures/                  # Test data files
│   ├── configs/              # Sample TOML configs
│   ├── rpc_responses/        # Mock JSON-RPC responses
│   ├── torrents/             # Sample torrent files
│   └── input_files/          # Download input files
└── mocks/                     # Mock objects for testing
    ├── mock_aria2_server.py  # Mock aria2 RPC server
    └── sample_responses.py   # Response builders
```

## Current Test Count

**Total: ~370 tests planned**

- Unit Tests: 220 tests
- Integration Tests: 125 tests
- End-to-End Tests: 27 tests

## Running Tests

### Quick Start

```bash
# Run all tests with coverage
./tests/scripts/run_tests.sh

# Run only unit tests (fastest)
./tests/scripts/run_unit_tests.sh

# Run integration tests
./tests/scripts/run_integration_tests.sh

# Run E2E tests (requires kitty terminal)
./tests/scripts/run_e2e_tests.sh
```

### Test Options

```bash
# Verbose output
./tests/scripts/run_tests.sh -v

# Show print statements
./tests/scripts/run_tests.sh -s

# Stop on first failure
./tests/scripts/run_tests.sh -x

# Run only tests matching a pattern
./tests/scripts/run_tests.sh -k "test_format"

# Run specific test file
./tests/scripts/run_unit_tests.sh tests/unit/test_format_utils.py

# Generate HTML coverage report
./tests/scripts/run_tests.sh --cov-report=html
```

### Running Tests by Category

```bash
# Unit tests only (no external dependencies)
./tests/scripts/run_unit_tests.sh

# Integration tests (mocked RPC server)
./tests/scripts/run_integration_tests.sh

# End-to-end tests (requires kitty terminal)
./tests/scripts/run_e2e_tests.sh

# Run only smoke tests (fastest E2E tests)
./tests/scripts/run_e2e_tests.sh -m smoke
```

### Running Tests in Parallel

```bash
# Use pytest-xdist for parallel execution
./tests/scripts/run_tests.sh -n auto
```

## Test Markers

Tests are categorized with markers:

- `@pytest.mark.unit`: Pure unit tests
- `@pytest.mark.integration`: Integration tests with mocked server
- `@pytest.mark.e2e`: End-to-end tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.requires_kitty`: Tests requiring kitty terminal
- `@pytest.mark.requires_aria2`: Tests requiring aria2c daemon
- `@pytest.mark.smoke`: Quick smoke tests

Example usage:

```bash
# Run only unit tests
./tests/scripts/run_tests.sh -m unit

# Skip slow tests
./tests/scripts/run_tests.sh -m "not slow"

# Run only smoke tests
./tests/scripts/run_tests.sh -m smoke
```

## Installation

### Install Test Dependencies

```bash
# Install testing dependencies
pip install -r requirements-test.txt

# Or install everything including test dependencies
pip install -e ".[test]"
```

### Dependencies

- pytest >= 8.0.0
- pytest-cov >= 4.1.0
- pytest-mock >= 3.12.0
- pytest-xdist >= 3.5.0
- responses >= 0.24.0

## Writing Tests

### Unit Test Example

```python
import pytest
from aria2tui.utils.aria2c_utils import format_size


class TestFormatSize:
    """Test format_size function."""

    def test_format_bytes(self):
        """Test formatting bytes."""
        assert format_size(0) == "0B"
        assert format_size(100) == "100B"

    def test_format_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1024 * 1024) == "1.0MB"
        assert format_size(1024 * 1024 * 50) == "50.0MB"
```

### Using Fixtures

Fixtures are defined in `conftest.py` and can be used in any test:

```python
def test_with_fixtures(sample_download, default_config):
    """Use fixtures defined in conftest.py."""
    assert sample_download["gid"] == "2089b05ecca3d829"
    assert default_config["general"]["port"] == 6800
```

### Integration Test Example

```python
@pytest.mark.integration
def test_rpc_communication(mock_aria2_server):
    """Test RPC communication with mocked server."""
    # Set up mock response
    mock_aria2_server("aria2.getVersion", {"version": "1.36.0"})

    # Test your code
    from aria2tui.lib.aria2c_wrapper import getVersionFull
    result = getVersionFull(token="test")

    # Verify
    assert "version" in result
```

### Adding New Tests

1. Create test file in appropriate directory:
   - `tests/unit/` for unit tests
   - `tests/integration/` for integration tests
   - `tests/e2e/` for end-to-end tests

2. Name test files with `test_` prefix: `test_module_name.py`

3. Name test functions with `test_` prefix: `test_function_behavior()`

4. Group related tests in classes: `class TestFunctionName:`

5. Add docstrings to describe what each test verifies

6. Use clear assertions and helpful failure messages

## Coverage Reports

Coverage reports show which code is tested:

```bash
# Generate terminal coverage report
./tests/scripts/run_tests.sh

# Generate HTML coverage report
./tests/scripts/run_tests.sh --cov-report=html
open htmlcov/index.html
```

### Coverage Targets

| Module | Target | Priority |
|--------|--------|----------|
| `aria2c_wrapper.py` | 95%+ | High - Pure functions |
| `aria2c_utils.py` (formatting) | 95%+ | High - Critical utilities |
| `aria2c_utils.py` (operations) | 85%+ | High - Complex logic |
| `display_info.py` | 80%+ | Medium |
| `graphing/` modules | 70%+ | Medium - Visual output |
| `aria2tui_app.py` | 60%+ | Low - UI orchestration |
| **Overall** | **80%+** | **Project goal** |

## End-to-End Testing

E2E tests use the kitty terminal emulator for automated UI testing.

### Requirements

- **kitty terminal** must be installed:
  ```bash
  brew install kitty  # macOS
  ```

### Running E2E Tests

```bash
# Run all E2E tests
./tests/scripts/run_e2e_tests.sh

# Run specific E2E test
./tests/scripts/run_e2e_tests.sh tests/e2e/test_smoke.py -v
```

### E2E Test Structure

E2E tests use the `KittyController` class to control a kitty terminal instance:

```python
@pytest.mark.e2e
def test_basic_navigation(kitty):
    """Test basic navigation in aria2tui."""
    # Launch app
    kitty.launch_aria2tui()

    # Wait for app to load
    kitty.wait_for_text("Active Downloads", timeout=3)

    # Navigate
    kitty.navigate_down(2)
    time.sleep(0.2)

    # Verify
    kitty.assert_text_present("expected text")

    # Clean up
    kitty.quit_app()
```

## Troubleshooting

### Import Errors

If you see import errors, make sure aria2tui is installed:

```bash
pip install -e .
```

### Kitty Tests Failing

End-to-end tests require kitty terminal:

```bash
# Install kitty
brew install kitty  # macOS

# Skip kitty tests
./tests/scripts/run_tests.sh -m "not requires_kitty"
```

### Slow Test Runs

Use parallel execution:

```bash
./tests/scripts/run_tests.sh -n auto
```

### Coverage Not Generated

Make sure pytest-cov is installed:

```bash
pip install pytest-cov
```

## Continuous Integration

Tests can run automatically on every commit:

- Unit and integration tests run on all PRs
- Coverage reports can be uploaded to coverage services
- E2E tests may require special setup in CI

## Test Design Principles

1. **Fast**: Unit tests should run in milliseconds
2. **Isolated**: Tests don't depend on each other
3. **Repeatable**: Same input = same output
4. **Comprehensive**: Test edge cases and error conditions
5. **Clear**: Easy to understand what failed and why

## Contributing

When adding new features:

1. Write tests first (TDD approach preferred)
2. Ensure all existing tests still pass
3. Add tests for edge cases and error conditions
4. Update this README if adding new test categories
5. Maintain or improve coverage percentage

## Mock Infrastructure

### Mock Aria2 Server

The `MockAria2Server` class simulates an aria2 RPC server for testing:

```python
from tests.mocks.mock_aria2_server import MockAria2Server

def test_with_mock_server():
    """Test with mocked aria2 server."""
    server = MockAria2Server()
    server.add_download("http://example.com/file.zip")

    # Test your code with the mock server
    response = server.handle_request(rpc_request)
    assert response["result"] is not None
```

### Sample Response Builders

Helper functions to create common test data:

```python
from tests.mocks.sample_responses import build_active_download

def test_with_sample_data():
    """Test with pre-built sample data."""
    download = build_active_download(
        gid="abc123",
        filename="test.zip",
        total_size=1024000,
        completed=512000
    )

    assert download["completedLength"] == "512000"
```

## Contact

For questions about the testing suite, please open an issue on GitHub.
