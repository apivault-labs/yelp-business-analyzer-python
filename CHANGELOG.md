# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-05-22

### Added
- Initial release of the Python SDK
- `YelpAnalyzerClient` with synchronous `analyze()` and `analyze_one()` methods
- Support for all 5 layer flags of the underlying actor:
  `extract_core`, `extract_hours_intel`, `extract_website`,
  `extract_age`, `extract_derived_signals`
- 6 example scripts: quickstart, bulk analyze, chain detection, CSV export,
  neighborhood comparison, open-now finder
- MIT license
