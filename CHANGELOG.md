# Changelog

All notable changes to this project will be documented in this file.

## [0.2.2] - 2026-06-04

### Fixed
- `create_bids_directory_structure()` now defaults to NOT creating session directories
  to comply with BIDS validator expectations for motion data
- Session directories can still be created by setting `use_session_dir=True`

### Added
- New example `examples/from_xdf_movella.py` demonstrating batch conversion of
  XDF files with Movella DOT IMU sensors
- Example shows proper handling of zero nominal sample rates and correct data loading sequence

## [0.2.1] - 2026-04-07

### Changed

- Package is now available on PyPI (`pip install motionbids`)
- Updated installation instructions across README and docs
- Added PyPI version badge to README

### Added

- Import examples for CSV, C3D (ezc3d), and IMU data in README and workflow docs

## [0.2.0] - 2026-03-09

### Added

- `export_participants_tsv()` function for creating and updating `participants.tsv` files
  - Supports `age`, `sex`, `handedness`, and custom columns via `**kwargs`
  - Automatically prefixes `participant_id` with `sub-` when needed
  - Appends new participants or updates existing entries in-place
  - Warns when the file already exists
- `export_dataset_description()` now warns when `dataset_description.json` or `participants.tsv` already exist
- PascalCase validation for `dataset_description` metadata keys
- Required-field validation on `channels.tsv` export with clear error messages
- Warning for unknown fields in channel metadata during export
- Additional keyword arguments support in `export_dataset_description()` for extra BIDS fields
- Documentation for `export_participants_tsv` in workflow and class-reference pages

### Changed

- `Channel` attributes renamed for BIDS compliance (`channel_name`, `channel_component`, etc.)
- `export_channels_tsv()` now uses `Channel.to_tsv_row()` method
- Improved validation logic for data and channels in `MotionData`

### Fixed

- Channel attribute usage in `example.py` and `exporter.py`
- Test suite compatibility fixes

## [0.1.0] - 2025-11-04

### Added

- Initial release
- `MotionData` dataclass for BIDS-compliant motion capture metadata
- Dynamic dataclass generation from BIDS schema (`datamodel_dynamic.py`)
- `Channel` dataclass with schema-validated fields
- `export_bids_motion()` for full BIDS export (JSON, TSV, channels TSV)
- `export_json_metadata()` for JSON sidecar files
- `export_tsv_data()` for motion time series data
- `export_channels_tsv()` for channel description files
- `export_scans_tsv()` with append/update support and sub-millisecond precision
- `export_dataset_description()` for `dataset_description.json`
- `create_bids_directory_structure()` helper
- `validate_motion_data()` and `validate_bids_compliance()` validators
- Schema utilities for BIDS field discovery
- MkDocs documentation site
- GitHub Actions CI for testing and docs deployment
