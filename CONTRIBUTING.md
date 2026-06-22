# Contributing to motionbids

Thanks for your interest in improving **motionbids**! Contributions of all kinds
are welcome — bug reports, feature ideas, documentation, and code.

## Reporting a bug or requesting a feature

Please [open an issue](https://github.com/JuliusWelzel/motionbids/issues) and include:

- What you expected to happen and what actually happened
- A minimal example that reproduces the problem (a small data snippet + code)
- Your `motionbids` version
  (`python -c "import motionbids; print(motionbids.__version__)"`),
  Python version, and operating system

## Asking a question / getting support

For usage questions or general discussion, use
[GitHub Discussions](https://github.com/JuliusWelzel/motionbids/discussions),
or open an issue if you're unsure — we're happy to help.

## Contributing code

1. **Fork** the repository and create a branch for your change.
2. **Set up a development environment:**
   ```bash
   git clone https://github.com/<your-username>/motionbids.git
   cd motionbids
   pip install -e ".[dev]"
   ```
3. **Make your change.** Keep it focused, and add or update tests for any change
   in behaviour.
4. **Run the test suite** and make sure it passes:
   ```bash
   pytest
   ```
5. **Open a pull request** against the `main` branch. Describe what the change
   does and why, and link any related issue.

## A few guidelines

- Follow the style of the surrounding code (PEP 8, descriptive names).
- Document public functions with docstrings — the API docs are generated from them.
- Keep BIDS-facing changes consistent with the
  [BIDS specification](https://bids-specification.readthedocs.io/) and the
  bundled BIDS schema.

## Code of conduct

Please be respectful and constructive. We follow the spirit of the
[Contributor Covenant](https://www.contributor-covenant.org/); by participating,
you help keep this a welcoming space for everyone.

## License

By contributing, you agree that your contributions will be licensed under the
project's [MIT License](LICENSE).
