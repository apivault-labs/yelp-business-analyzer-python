# Contributing

Thanks for your interest in improving this SDK.

## Reporting bugs

Open a [GitHub issue](https://github.com/apivault-labs/yelp-business-analyzer-python/issues)
with:
- Python version (`python --version`)
- SDK version (`pip show yelp-business-analyzer`)
- The Yelp URL that triggered the issue (if applicable)
- The full traceback or unexpected output
- A minimal reproducer

## Suggesting features

Two flavors:
- **Client-side improvements** (better error messages, async client, retries) — open an issue here
- **New extracted fields** (more tech-stack patterns, new derived metrics) — those live in the
  underlying Apify actor; open an issue and we'll discuss where it fits

## Development setup

```bash
git clone https://github.com/apivault-labs/yelp-business-analyzer-python.git
cd yelp-business-analyzer-python
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
```

## Pull requests

- Keep changes focused — one PR per feature/bugfix
- Add a line to `CHANGELOG.md` under `[Unreleased]`
- Match the existing code style (PEP 8, type hints, no unnecessary abstractions)

## License

By contributing you agree that your code will be released under the MIT license.
