# Contributing to TendedLoop Arena

Thanks for your interest in contributing! Here's how to get started.

## Ways to Contribute

- **Bug reports** — Found a problem? Open an issue with steps to reproduce
- **New examples** — Built a cool agent strategy? Share it
- **Documentation** — Improvements, clarifications, or translations
- **Feature requests** — Ideas for SDK improvements
- **Bug fixes** — PRs welcome for any open issue

## Development Setup

```bash
# Clone the repo
git clone https://github.com/osheryadgar/tendedloop-arena.git
cd tendedloop-arena

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode with all extras
pip install -e ".[all]"

# Run tests
pytest

# Run linter
ruff check .
ruff format .
```

## Pull Request Process

1. Fork the repo and create a feature branch
2. Make your changes with clear, descriptive commits
3. Add tests if applicable
4. Update documentation if you changed behavior
5. Open a PR with a clear description of what and why

## Code Style

- Python 3.10+ features are fine (union types, match statements, etc.)
- Format with `ruff format`, lint with `ruff check`
- Type hints for all public APIs
- Docstrings for all public classes and methods
- Examples should be self-contained and runnable

## Adding Examples

Examples live in `examples/` and should follow this pattern:

1. Module docstring explaining what the example does and how to run it
2. Clear configuration section at the top
3. Well-commented decision logic
4. A `main()` function as entry point
5. Use `if __name__ == "__main__": main()`

## Questions?

Open an issue or reach out at [support@tendedloop.com](mailto:support@tendedloop.com).
