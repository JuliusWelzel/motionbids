# motion2bids

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **lightweight** Python package for defining and managing **BIDS-compliant motion data**. 

`motion2bids` provides a simple, schema-driven interface to create, validate, and export motion data following the [Brain Imaging Data Structure (BIDS)](https://bids-specification.readthedocs.io/) standard.

## Features

- ✅ **Dynamic dataclass** derived from BIDS schema using [`bidsschematools`](https://pypi.org/project/bidsschematools/)
- ✅ **Field validation** for required and recommended metadata
- ✅ **BIDS-compliant export** to `.json` and `.tsv` files
- ✅ **Lightweight** with minimal dependencies

---

## Installation

### Using `uv` (recommended)

```bash
uv pip install motion2bids
```

### Using `pip`

```bash
pip install motion2bids
```

### From source

```bash
git clone https://github.com/juliuswelzel/motion2bids.git
cd motion2bids
uv pip install -e .
```

---

## Quick Start

```python
from motion2bids import MotionData, validate_motion_data, export_bids_motion
import numpy as np

# Create motion time series data
# Data format: rows = timepoints, columns = channels
# Shape: (n_timepoints, n_channels)
n_timepoints = 1000  # 1000 time samples
n_channels = 30      # 30 channels (10 markers × 3 axes)
data = np.random.randn(n_timepoints, n_channels)

# Define channel names (must match data columns)
columns = [f"marker{i}_x" for i in range(10)] + \
          [f"marker{i}_y" for i in range(10)] + \
          [f"marker{i}_z" for i in range(10)]

# Define units for each channel (must match columns)
units = ["mm"] * n_channels

# Create motion data object
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120,
    tracked_points_count=10,
    manufacturer="Vicon",
    manufacturers_model_name="Vantage",
    recording_type="continuous",
    data=data,           # NumPy array: rows=timepoints, columns=channels
    columns=columns,     # Channel names (must match data.shape[1])
    units=units          # Units per channel (must match len(columns))
)

# Validate the data
validate_motion_data(motion)  # Raises ValidationError if invalid

# Export to BIDS format
files = export_bids_motion(motion, out_dir="bids_dataset/sub-01/ses-01/motion/")

print(files)
# {
#     'json': PosixPath('bids_dataset/.../sub-01_task-walk_motion.json'),
#     'tsv': PosixPath('bids_dataset/.../sub-01_task-walk_motion.tsv'),
#     'channels': PosixPath('bids_dataset/.../sub-01_task-walk_channels.tsv')
# }
```

---

## Usage

### Creating MotionData

The `MotionData` dataclass represents a single motion capture recording with BIDS metadata.

#### Required Fields

All motion data objects must include these fields:

```python
motion = MotionData(
    subject_id="01",              # Subject identifier
    task_name="rest",             # Task name (e.g., 'rest', 'walk')
    tracksys="optical",         # Tracking system label
    sampling_frequency=100.0,     # Sampling rate in Hz
    tracked_points_count=10,      # Number of tracked markers/points
    data=np.random.randn(1000, 10),  # Motion data: rows=timepoints, columns=channels
    columns=[f"marker{i}" for i in range(10)],  # Channel names (must match data columns)
    units=["mm"] * 10             # Units for each channel (must match columns)
)
```

**Data Format Requirements:**
- `data`: NumPy array where **rows = timepoints** and **columns = channels**
- `columns`: List of channel names that **must match** the number of data columns
- `units`: List of units per channel that **must match** the length of `columns`
- The `columns` and `units` lists define the structure written to `*_channels.tsv`

#### Recommended Fields

Include these fields for better BIDS compliance:

```python
import numpy as np

# Create sample data: 1000 timepoints, 30 channels (10 markers × 3 axes)
data = np.random.randn(1000, 30)  # rows=timepoints, columns=channels

motion = MotionData(
    subject_id="01",
    task_name="walk",
    sampling_frequency=120.0,
    tracked_points_count=10,
    tracksys="optical",
    # Recommended fields
    manufacturer="Vicon",
    manufacturers_model_name="Vantage V5",
    software_versions="Nexus 2.12",
    motion_channel_count=30,
    recording_duration=10.0,
    recording_type="continuous",
    # Motion data (rows=timepoints, columns=channels)
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x', 'y', 'z']],
    units=["mm"] * 30
)
```

#### Optional BIDS Entities

Add optional BIDS entities for multi-session or multi-run studies:

```python
import numpy as np

# Motion data: 500 timepoints, 15 channels
data = np.random.randn(500, 15)  # rows=timepoints, columns=channels

motion = MotionData(
    subject_id="01",
    task_name="walk",
    sampling_frequency=120.0,
    tracked_points_count=5,
    tracksys="optical",       # Tracking system label
    # Optional entities
    session_id="01",          # Session identifier
    acquisition="outdoor",    # Acquisition label
    run=1,                    # Run number
    # Motion data and channel definitions
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(5) for axis in ['x', 'y', 'z']],
    units=["mm"] * 15
)
```

#### Including Time Series Data

**Important:** Motion data must be organized with **rows as timepoints** and **columns as channels**. The `columns` list must match the data dimensions and defines the structure of the `*_channels.tsv` file.

```python
import numpy as np

# Example: 10 markers with x, y, z coordinates = 30 channels
# Data shape: (n_timepoints, n_channels)
n_timepoints = 1000
n_markers = 10
n_channels = n_markers * 3  # x, y, z for each marker

# Create motion data: rows=timepoints, columns=channels
data = np.random.randn(n_timepoints, n_channels)

# Define channel names - must match data.shape[1]
columns = [f"marker{i}_{axis}" for i in range(n_markers) for axis in ['x', 'y', 'z']]

# Define units per channel - must match len(columns)
units = ["mm"] * n_channels

motion = MotionData(
    subject_id="01",
    task_name="walk",
    sampling_frequency=120.0,
    tracked_points_count=n_markers,
    data=data,          # Shape: (1000, 30) - rows are timepoints, columns are channels
    columns=columns,    # Length: 30 - must match data.shape[1]
    units=units         # Length: 30 - must match len(columns)
)
```

**Key Requirements:**
- `data.shape[0]` = number of timepoints
- `data.shape[1]` = number of channels = `len(columns)` = `len(units)`
- The `columns` and `units` lists are used to generate the `*_channels.tsv` file
- Each row in `*_channels.tsv` corresponds to one column in the data array

---

### Validation

The package provides comprehensive validation for BIDS compliance:

```python
from motion2bids import validate_motion_data

try:
    validate_motion_data(motion)
    print("✓ Yaaay, your motion data seems to be valid BIDS! \n But remember to double-check with the validator as well. ")
```

#### Validation Features

- **Required fields**: Raises `ValidationError` if missing
- **Recommended fields**: Issues warnings if missing (use `strict=True` to raise errors)
- **Field format validation**: Checks BIDS naming conventions
- **Data consistency**: Validates that:
  - Array dimensions match metadata (`data.shape[1]` == `len(columns)`)
  - Units match columns (`len(units)` == `len(columns)`)
  - Number of samples matches recording duration (within 1% tolerance)

```python
import numpy as np

# Create motion data with proper dimensions
data = np.random.randn(1000, 30)  # 1000 timepoints, 30 channels
columns = [f"ch{i}" for i in range(30)]
units = ["mm"] * 30

motion = MotionData(
    subject_id="01",
    task_name="walk",
    sampling_frequency=120.0,
    tracked_points_count=10,
    data=data,
    columns=columns,
    units=units
)

# Strict validation (treats missing recommended fields as errors)
validate_motion_data(motion, strict=True)
```

---

### Exporting to BIDS

Export motion data to BIDS-compliant files:

```python
from motion2bids import export_bids_motion

files = export_bids_motion(
    data=motion,
    out_dir="bids_dataset/sub-01/motion/",
    validate=True,      # Validate before export
    create_dirs=True,   # Create output directory
    overwrite=False     # Don't overwrite existing files
)

# Example output with all entities:
# sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-01_motion.json
```

#### Output Files

The export creates up to three BIDS-compliant files:

1. **`*_motion.json`**: Metadata sidecar file
   ```json
   {
     "TaskName": "walk",
     "SamplingFrequency": 120.0,
     "TrackedPointsCount": 10,
     "Manufacturer": "Vicon",
     "Columns": ["marker0_x", "marker0_y", "marker0_z", ...],
     "Units": ["mm", "mm", "mm", ...]
   }
   ```

2. **`*_motion.tsv`**: Time series data file (if `data` is provided)
   - **Format:** Tab-separated values where **columns = channels** and **rows = timepoints**
   - First row contains channel names (from `columns` list)
   - Subsequent rows contain time series data
   
   ```tsv
   marker0_x    marker0_y    marker0_z    marker1_x    ...
   123.45       678.90       234.56       456.78       ...
   123.48       679.01       234.60       456.82       ...
   123.51       679.12       234.64       456.86       ...
   ```

3. **`*_channels.tsv`**: Channel descriptions (if `units` are provided)
   - **Required:** This file must match the columns in `*_motion.tsv`
   - Each row describes one channel (column) from the motion data
   - **Required columns (in order):** name, component, type, tracked_point, units
   
   ```tsv
   name          component    type    tracked_point    units
   marker0_x     x            POS     marker0          mm
   marker0_y     y            POS     marker0          mm
   marker0_z     z            POS     marker0          mm
   marker1_x     x            POS     marker1          mm
   ```
   
   **Column descriptions:**
   - `name`: Full channel name (matches column header in motion.tsv)
   - `component`: Measurement component (x, y, z, quat_w, roll, etc.)
   - `type`: Type of measurement (POS=position, ORNT=orientation, VEL=velocity, ACCEL=acceleration)
   - `tracked_point`: Label of the tracked point/marker
   - `units`: Physical units (mm, rad, m/s, etc.)

**Important:** The `channels.tsv` file is automatically generated from the `columns` and `units` lists provided to `MotionData`. The package will attempt to parse channel names (e.g., "marker0_x") to extract component and tracked_point information. The order and number of rows in `channels.tsv` must exactly match the order and number of columns in the `motion.tsv` file.

#### BIDS Filenames

Filenames follow BIDS naming conventions with entities in the correct order:

```python
motion.get_bids_filename()
# 'sub-01_task-walk_motion.json'

motion.get_bids_filename(suffix="channels", extension="tsv")
# 'sub-01_task-walk_channels.tsv'
```

With all entities (note the order: tracksys comes before acq):
```python
# sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-02_motion.json
```

**Entity Order:**
- `sub-<label>` (required)
- `ses-<label>` (optional)
- `task-<label>` (required)
- `tracksys-<label>` (optional)
- `acq-<label>` (optional)
- `run-<index>` (optional)

---

### Creating a BIDS Dataset

Helper functions for organizing a complete BIDS dataset:

```python
from motion2bids import (
    MotionData, 
    create_bids_directory_structure, 
    export_dataset_description,
    export_bids_motion
)
import numpy as np

# Create directory structure
motion_dir = create_bids_directory_structure(
    base_dir="bids_root",
    subject_id="01",
    session_id="01"
)
# Creates: bids_root/sub-01/ses-01/motion/

# Create dataset_description.json
export_dataset_description(
    bids_root="bids_root",
    name="My Motion Capture Study",
    authors=["Jane Doe", "John Smith"],
    dataset_type="raw"
)

# Create and export motion data
data = np.random.randn(1000, 30)  # rows=timepoints, columns=channels
motion = MotionData(
    subject_id="01",
    session_id="01",
    task_name="walk",
    sampling_frequency=120.0,
    tracked_points_count=10,
    manufacturer="Vicon",
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x', 'y', 'z']],
    units=["mm"] * 30
)

# Export to the created directory
export_bids_motion(motion, out_dir=motion_dir)
```

---

## Advanced Usage

### Custom Metadata

Add custom fields not in the standard BIDS specification:

```python
import numpy as np

# Motion data with custom metadata
data = np.random.randn(800, 24)  # rows=timepoints, columns=channels

motion = MotionData(
    subject_id="01",
    task_name="walk",
    sampling_frequency=120.0,
    tracked_points_count=8,
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(8) for axis in ['x', 'y', 'z']],
    units=["mm"] * 24,
    additional_metadata={
        "CustomField": "custom_value",
        "ExperimentalCondition": "A",
        "Temperature": 22.5,
        "CaptureVolume": "8m x 6m x 3m"
    }
)
```

### Accessing Schema Information

For advanced users, schema utilities are available:

```python
from motion2bids import schema_utils

# Get required fields from BIDS schema
required = schema_utils.get_required_fields()

# Get recommended fields
recommended = schema_utils.get_recommended_fields()

# Get metadata field definitions
metadata = schema_utils.get_motion_metadata_fields()
```

---

## Development

### Setup with `uv`

```bash
# Clone repository
git clone https://github.com/juliuswelzel/motion2bids.git
cd motion2bids

# Install in development mode with dev dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=motion2bids --cov-report=html

# Run specific test file
uv run pytest tests/test_datamodel.py
```

### Building the Package

```bash
# Build distribution
uv build

# Install locally
uv pip install .
```

---

## Dependencies

### Core Dependencies
- **`bidsschematools`** (≥0.8.0): BIDS schema definitions
- **`dataclasses-json`** (≥0.6.0): JSON serialization for dataclasses
- **`numpy`** (≥1.20.0): Array operations for time series data

### Development Dependencies
- **`pytest`** (≥7.0.0): Testing framework
- **`pytest-cov`** (≥4.0.0): Coverage reporting

---

## Project Structure

```
motion2bids/
├── motion2bids/
│   ├── __init__.py          # Public API
│   ├── datamodel.py         # MotionData dataclass
│   ├── validator.py         # Validation logic
│   ├── exporter.py          # BIDS file export
│   └── schema_utils.py      # Schema extraction utilities
├── tests/
│   ├── test_datamodel.py    # Dataclass tests
│   ├── test_validator.py    # Validation tests
│   └── test_exporter.py     # Export tests
├── pyproject.toml           # Package configuration
├── README.md                # This file
└── LICENSE                  # MIT License
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run tests (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built on the [BIDS specification](https://bids-specification.readthedocs.io/)
- Uses [`bidsschematools`](https://github.com/bids-standard/bids-specification) for schema access
- Inspired by the BIDS community's work on standardizing neuroimaging data

---

## Citation

If you use `motion2bids` in your research, please cite:

```bibtex
@software{motion2bids,
  author = {Julius Welzel},
  title = {motion2bids: Lightweight BIDS converter for motion capture data},
  year = {2025},
  url = {https://github.com/juliuswelzel/motion2bids}
}
```

---

## Support

- **Issues**: [GitHub Issues](https://github.com/juliuswelzel/motion2bids/issues)
- **Discussions**: [GitHub Discussions](https://github.com/juliuswelzel/motion2bids/discussions)
- **BIDS Specification**: [https://bids-specification.readthedocs.io/](https://bids-specification.readthedocs.io/)

---

