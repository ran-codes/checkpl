# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-01-12

### Changed

- **BREAKING**: Renamed package from `checkpl` to `assert-polars` for better clarity and discoverability
- Updated README with correct package name and installation instructions

## [0.1.1] - 2025-01-12

### Changed

- Relaxed Polars dependency from `>=1.37.0` to `>=1.0.0` for broader compatibility

## [0.1.0] - 2025-01-12

### Added

- `verify()` - Validate DataFrames using Polars boolean expressions or predicates
- `is_uniq()` - Check for duplicate values across one or more columns
- `CheckError` - Exception with descriptive messages and check names
- LazyFrame support for all validations
