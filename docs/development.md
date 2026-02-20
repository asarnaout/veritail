# Development

This guide covers setting up a local development environment for veritail.

## Getting started

Clone the repository and install in editable mode with development and cloud provider dependencies:

```bash
git clone https://github.com/asarnaout/veritail.git
cd veritail
pip install -e ".[dev,cloud]"
```

The `dev` extra includes test and lint tooling (pytest, ruff, mypy) along with all provider SDKs. The `cloud` extra pulls in the Anthropic and Google Gemini client libraries.

## Running checks

```bash
# Unit tests
pytest

# Linting
ruff check src tests

# Type checking
mypy src
```

All three commands should pass before submitting a pull request.

## See also

- [Backends](backends.md) -- storage backend options
- [Supported LLM Providers](supported-llm-providers.md) -- provider setup and model guidance
