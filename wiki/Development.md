# Development

## Setup

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended) or `pip`

### Clone the Repository

```bash
git clone https://github.com/jjack/python-atmos-energy.git
cd python-atmos-energy
```

### Install with `uv` (Recommended)

Install `uv` if you haven't already:

```bash
pip install uv
```

Then install the project and all development dependencies:

```bash
uv sync --all-groups
```

### Install with `pip`

If you prefer `pip`:

```bash
pip install -e ".[dev]"
```

---

## Project Structure

```
python-atmos-energy/
├── src/
│   └── atmos_energy/
│       ├── __init__.py           # Main API client
│       ├── cli.py                # Command-line interface
│       ├── constants.py          # Configuration constants
│       └── py.typed              # PEP 561 type hints marker
├── tests/
│   ├── test_atmosenergy.py       # API tests (27 tests)
│   └── test_cli.py               # CLI tests (26 tests)
├── .github/
│   └── workflows/
│       └── build.yml             # CI/CD pipeline
├── pyproject.toml               # Project metadata and dependencies
├── README.md                    # Project overview
├── LICENSE                      # Apache 2.0 license
└── wiki/                        # Documentation
```

---

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run Specific Test File

```bash
uv run pytest tests/test_atmosenergy.py
```

### Run Specific Test Class

```bash
uv run pytest tests/test_cli.py::TestMainCli
```

### Run Specific Test

```bash
uv run pytest tests/test_cli.py::TestMainCli::test_main_usage_success
```

### Run with Verbose Output

```bash
uv run pytest -v
```

### Run with Print Statements

```bash
uv run pytest -s
```

---

## Test Coverage

### Generate Coverage Report

```bash
uv run pytest --cov=atmos_energy --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Coverage Summary

```bash
uv run pytest --cov=atmos_energy
```

### Current Coverage

The project includes 53 comprehensive tests:

- **API Tests** (`test_atmosenergy.py`): 27 tests (including 4 new `get_usage_history` tests)
  - Initialization, request handling, URL generation
  - Billing period calculation, response validation
  - Usage data formatting, login/logout, error handling
  - Transparent request count tests for both `get_current_usage()` and `get_usage_history()`

- **CLI Tests** (`test_cli.py`): 26 tests
  - Timestamp formatting, CSV writing
  - Table printing, config loading
  - Argument merging, end-to-end CLI tests
  - Routing to correct API method based on `--months` parameter

---

## Code Quality

### Linting

Check code style with Ruff:

```bash
uv run ruff check src/ tests/
```

### Formatting

Format code with Ruff:

```bash
uv run ruff format src/ tests/
```

### Both Check and Format

```bash
uv run ruff check --fix src/ tests/
```

### Configuration

Ruff configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "B"]
```

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Edit files in `src/atmos_energy/`.

### 3. Run Tests

```bash
uv run pytest -v
```

### 4. Check Code Quality

```bash
uv run ruff check --fix src/ tests/
```

### 5. Commit and Push

```bash
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

### 6. Create Pull Request

Open a PR on GitHub for review.

---

## Adding Tests

### Test Structure

Tests use class-based organization with `unittest.mock`:

```python
import unittest
from unittest.mock import patch, MagicMock

class TestMyFeature(unittest.TestCase):
    def test_something(self):
        # Arrange
        expected = "result"
        
        # Act
        actual = my_function()
        
        # Assert
        self.assertEqual(expected, actual)
```

### Running Your New Tests

```bash
uv run pytest tests/test_my_new_feature.py -v
```

---

## Building

### Build Distribution Packages

```bash
uv build
```

This creates `dist/` directory with:
- `atmos_energy-0.1.0-py3-none-any.whl` (wheel)
- `atmos_energy-0.1.0.tar.gz` (source distribution)

### Build Without Intermediates

```bash
uv build --no-directory
```

---

## Publishing

### PyPI Credentials

The project uses GitHub Actions with OIDC for automated publishing. No credentials are needed locally.

### Manual Publishing (Not Recommended)

If publishing manually:

```bash
pip install twine
twine upload dist/*
```

### Automated Publishing (Recommended)

1. Create a git tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. GitHub Actions automatically:
   - Runs tests on Python 3.10-3.14
   - Builds packages
   - Publishes to PyPI

### TestPyPI Staging

The CI/CD pipeline also publishes to TestPyPI on every push to `main`:

```bash
pip install --index-url https://test.pypi.org/simple/ atmos-energy
```

---

## Dependencies

### Core Dependencies

```toml
requests = "^2.31.0"          # HTTP client
beautifulsoup4 = "^4.12.0"    # HTML parsing
xlrd = "^2.0.1"               # Excel reading
python-dateutil = "^2.8.2"    # Date utilities
pyyaml = "^6.0"               # YAML configuration
```

### Development Dependencies

```toml
pytest = "^7.4.3"             # Testing framework
pytest-cov = "^4.1.0"         # Coverage reporting
requests-mock = "^1.11.0"     # Mock HTTP requests
ruff = "^0.1.8"               # Linting and formatting
```

### Adding Dependencies

Add with `uv`:

```bash
uv add package-name
```

Add as development dependency:

```bash
uv add --dev package-name
```

---

## Environment Variables

The CLI and API use environment variables for sensitive data:

- `ATMOS_USERNAME`: Atmos Energy username (optional, CLI arg/config takes precedence)
- `ATMOS_PASSWORD`: Atmos Energy password (optional, CLI arg/config takes precedence)

Example:

```bash
export ATMOS_USERNAME=user@example.com
export ATMOS_PASSWORD=mypassword
atmos-energy --months 6
```

---

## Debugging

### Enable Debug Logging

The library uses Python's standard `logging` module:

```python
import logging
from atmos_energy import AtmosEnergy

logging.basicConfig(level=logging.DEBUG)

client = AtmosEnergy(username='user@example.com', password='mypassword')
client.login()

# Get current month (1 API request)
usage = client.get_current_usage()

# Get historical data (N API requests)
history = client.get_usage_history(months=6)
```

### CLI Debug Mode

```bash
atmos-energy --verbose --config config.yaml
```

### Interactive Development

```bash
python -i -c "from atmos_energy import AtmosEnergy; client = AtmosEnergy(username='user', password='pass')"
```

---

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` (if present)
3. Create commit: `git commit -m "Release v0.2.0"`
4. Create tag: `git tag v0.2.0`
5. Push: `git push origin main --tags`
6. GitHub Actions handles the rest

---

## Common Issues

### Import Errors

```
ModuleNotFoundError: No module named 'atmos_energy'
```

Solution:
```bash
uv sync --all-groups
```

### Test Failures

Run with verbose output:
```bash
uv run pytest -vv --tb=short
```

### Linting Errors

Auto-fix with:
```bash
uv run ruff format src/ tests/
```

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/jjack/python-atmos-energy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jjack/python-atmos-energy/discussions)
