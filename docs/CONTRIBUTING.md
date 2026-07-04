# Contributing

Contributions welcome.

## What to contribute

- New AI writing trope patterns for `rules/ai_writing_tropes.md`
- Lint rule improvements (fewer false positives, better patterns)
- Line-fill measurement accuracy improvements
- New template formats
- Documentation improvements
- Bug fixes

## How to contribute

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Run the linter on the example application to verify nothing breaks:
   ```bash
   cd examples/sample_application
   jat lint Resume__Research_Scientist__Example_Role.md
   jat crosscheck .
   ```
5. Submit a pull request

## Code style

- Python 3.10+
- Ruff for formatting (`ruff check --fix .`)
- Type hints on function signatures
- Docstrings on public functions

## What not to contribute

- Your personal ground truth, profile, or corrections log
- Application-specific content
- AI-generated boilerplate (ironic, but the tropes list exists for a reason)
