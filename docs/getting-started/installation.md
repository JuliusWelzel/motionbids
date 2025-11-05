# Installation

## Requirements

motionbids requires:

- **Python 3.8 or higher**
- NumPy (≥ 1.20.0)
- bidsschematools (≥ 0.8.0)
- dataclasses-json (≥ 0.6.0)

## Installation Methods

=== "uv (Recommended)"

    The fastest way to install using [uv](https://github.com/astral-sh/uv):

    ```bash
    uv pip install motionbids
    ```

    Or add to your project:

    ```bash
    uv add motionbids
    ```

=== "pip"

    Standard installation with pip:

    ```bash
    pip install motionbids
    ```

=== "From Source"

    Install the latest development version:

    ```bash
    git clone https://github.com/JuliusWelzel/motionbids.git
    cd motionbids
    uv pip install -e .
    ```

    Or with pip:

    ```bash
    pip install -e .
    ```

## Verify Installation

Check that motionbids is installed correctly:

```python
import motionbids
print(motionbids.__version__)
```

You should see the version number printed (e.g., `0.1.0`).

## Optional Dependencies

### Development Dependencies

If you want to contribute or run tests:

```bash
# With uv
uv pip install -e ".[dev]"

# With pip
pip install -e ".[dev]"
```

This installs additional tools:

- `pytest` for testing
- `pytest-cov` for coverage reports
- `black` for code formatting
- `ruff` for linting

### Documentation Dependencies

To build the documentation locally:

```bash
# With uv
uv pip install -e ".[docs]"

# With pip
pip install -e ".[docs]"
```

This installs:

- `mkdocs` documentation generator
- `mkdocs-material` theme
- `mkdocstrings` for API docs

## Troubleshooting

### ImportError: No module named 'bidsschematools'

If you see this error, the bidsschematools package is missing:

```bash
pip install bidsschematools>=0.8.0
```

### NumPy Version Issues

motionbids requires NumPy 1.20.0 or higher. If you have an older version:

```bash
pip install --upgrade numpy
```

### Python Version

Make sure you're using Python 3.8 or higher:

```bash
python --version
```

If you have an older version, consider using [pyenv](https://github.com/pyenv/pyenv) or [conda](https://docs.conda.io/) to install a newer Python version.

## Next Steps

Once installed, proceed to the [Quick Start](quickstart.md) guide to create your first BIDS motion dataset.
