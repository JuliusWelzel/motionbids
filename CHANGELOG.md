# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-06-22

### Changed
- **Breaking:** stricter BIDS entity-label validation in `validate_motion_data()`.
  The `subject`, `session`, `task_name`, `acquisition`, and `tracksys` labels
  must now match the BIDS label format `[0-9a-zA-Z+]+` (ASCII alphanumerics and
  `+` only). `_`, `-`, spaces, and non-ASCII characters are now rejected, since
  `_` and `-` are reserved BIDS entity/key-value separators. Previously only
  `subject` and `task_name` were checked, and `_`/`-` were incorrectly allowed,
  so inputs that passed validation before may now raise a `ValidationError`.
- Consolidated the development dependencies into the `dev` optional-dependencies
  extra so `pip install -e ".[dev]"` works on any pip version (removed the
  PEP 735 `[dependency-groups]` table).

### Added
- New example `examples/from_c3d_vicon.py` converting Vicon C3D marker data to
  BIDS, with a bundled sample recording downloaded on first run.
- Documentation "Examples" section with per-system walkthrough pages
  (Vicon C3D and Movella XDF).

### Fixed
- Updated all README and documentation examples to the `subject`/`session`
  parameter names introduced in 0.3.0.

## [0.3.0] - 2026-06-08

### Changed
- **Breaking:** the `subject_id` and `session_id` parameters (and the
  `MotionData.subject_id` / `MotionData.session_id` fields) are renamed to
  `subject` and `session` across the API (`MotionData`,
  `create_bids_directory_structure()`, and validation), following the BIDS
  "subject label" / "session label" terminology. The `participants.tsv`
  `participant_id` column is unchanged.
- Updated installation instructions across README and docs

### Added
- New example `examples/from_xdf_movella.py` demonstrating batch conversion of
  XDF files with Movella DOT IMU sensors
- Example shows proper handling of zero nominal sample rates and correct data loading sequence
- Import examples for CSV, C3D (ezc3d), and IMU data in README and workflow docs
- PyPI version badge to README

### Fixed
- `create_bids_directory_structure()` now creates a `ses-<label>` directory level
  if and only if a `session` is provided, matching the BIDS rule that the
  session directory must be present exactly when the `ses-` entity appears in
  filenames. This keeps filenames and their on-disk location consistent and fixes
  BIDS validator `INVALID_LOCATION` errors (replaces the earlier `use_session_dir`
  flag, which has been removed)

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
