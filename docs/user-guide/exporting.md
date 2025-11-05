# Exporting to BIDS Format

This guide explains how motionbids exports your data to BIDS-compliant files and directories.

## Overview

The export process creates a complete BIDS-compliant dataset structure with:

- **JSON metadata file** - Acquisition parameters and equipment info
- **TSV data file** - Motion time series (numeric data only, no headers)
- **Channels TSV file** - Channel descriptions and metadata
- **Scans TSV file** (optional) - Acquisition timestamps

## Basic Export

### Single Function Export

The simplest way to export is using `export_bids_motion()`:

```python
from motionbids import MotionData, export_bids_motion
import numpy as np

# Create your motion data
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    data=np.random.randn(1200, 30),
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x','y','z']],
    units=["mm"] * 30
)

# Export to BIDS format
files = export_bids_motion(
    data=motion,
    out_dir="my_study/sub-01/ses-01/motion/",
    validate=True,
    overwrite=True
)

print(f"Created files: {list(files.keys())}")
# Output: ['json', 'tsv', 'channels']
```

### Export Parameters

```python
export_bids_motion(
    data: MotionData,           # Your motion data object
    out_dir: str | Path,        # Output directory
    validate: bool = True,      # Validate before export
    create_dirs: bool = True,   # Create directories if missing
    overwrite: bool = False     # Overwrite existing files
)
```

#### Parameters Explained

- **`data`**: The `MotionData` object to export
- **`out_dir`**: Directory where files will be created
- **`validate`**: Whether to validate BIDS compliance before export (recommended: `True`)
- **`create_dirs`**: Whether to create output directories if they don't exist
- **`overwrite`**: Whether to overwrite existing files (default: `False` for safety)

## Understanding the Output

### File Structure

After exporting, you'll have this structure:

```
my_study/
└── sub-01/
    ├── sub-01_ses-01_scans.tsv                                          # Optional
    └── ses-01/
        └── motion/
            ├── sub-01_ses-01_task-walk_tracksys-optical_motion.json     # Metadata
            ├── sub-01_ses-01_task-walk_tracksys-optical_motion.tsv      # Data
            └── sub-01_ses-01_task-walk_tracksys-optical_channels.tsv    # Channels
```

### File Types

#### 1. JSON Metadata File (`*_motion.json`)

Contains acquisition parameters and equipment information.

**Example content:**

```json
{
  "TaskName": "walk",
  "SamplingFrequency": 120.0,
  "TrackedPointsCount": 10,
  "Manufacturer": "Vicon",
  "ManufacturersModelName": "Vantage V5",
  "SoftwareVersions": "Nexus 2.12",
  "MotionChannelCount": 30,
  "RecordingDuration": 10.0,
  "RecordingType": "continuous"
}
```

**What's included:**

- All BIDS metadata fields (PascalCase names)
- Recommended fields when provided
- Custom metadata from `additional_metadata`

**What's excluded:**

- Entity fields (they're in the filename)
- `columns` and `units` (they're in the channels file)
- `data` array (it's in the TSV file)

!!! note "Field Name Conversion"
    Python fields use `snake_case`, but JSON uses BIDS-compliant `PascalCase`:
    
    - `sampling_frequency` → `SamplingFrequency`
    - `tracked_points_count` → `TrackedPointsCount`

#### 2. TSV Data File (`*_motion.tsv`)

Contains the motion time series data.

**Format:**

- **No headers** (per BIDS specification)
- Tab-separated values
- Rows = timepoints
- Columns = channels

**Example content:**

```tsv
100.234	150.123	75.456	...
100.567	150.234	75.567	...
100.678	150.345	75.678	...
...
```

!!! warning "No Headers"
    The TSV file contains **only numeric data**, no column headers. Channel information is in the separate `*_channels.tsv` file.

**Why no headers?**

The BIDS specification requires motion data TSV files to contain only numeric values. Channel metadata (names, types, units) is stored in the companion `*_channels.tsv` file.

#### 3. Channels TSV File (`*_channels.tsv`)

Describes each channel in the data.

**Required columns (in order):**

1. `name` - Channel name
2. `component` - Component/axis (x, y, z, etc.)
3. `type` - Data type (POS, ORNT, VEL, ACCEL, etc.)
4. `tracked_point` - Which point/marker this channel belongs to
5. `units` - Measurement units

**Example content:**

```tsv
name          component  type  tracked_point  units
marker0_x     x          POS   marker0        mm
marker0_y     y          POS   marker0        mm
marker0_z     z          POS   marker0        mm
marker1_x     x          POS   marker1        mm
marker1_y     y          POS   marker1        mm
marker1_z     z          POS   marker1        mm
```

**Automatic Channel Parsing:**

The exporter automatically parses channel names to extract metadata:

```python
# Channel name patterns recognized:
"marker0_x"     → component: x, tracked_point: marker0, type: POS
"LFHD_y"        → component: y, tracked_point: LFHD, type: POS
"pelvis_qw"     → component: qw, tracked_point: pelvis, type: ORNT
"COM_vx"        → component: vx, tracked_point: COM, type: VEL
"head_ax"       → component: ax, tracked_point: head, type: ACCEL
```

**Supported channel types:**

| Type | Description | Component Examples |
|------|-------------|-------------------|
| `POS` | Position | x, y, z |
| `ORNT` | Orientation (quaternion) | qw, qx, qy, qz |
| `VEL` | Velocity | vx, vy, vz |
| `ACCEL` | Acceleration | ax, ay, az |
| `ANGVEL` | Angular velocity | wx, wy, wz |
| `OTHER` | Other/unknown | (any) |

#### 4. Scans TSV File (`*_scans.tsv`)

Created automatically when `acq_time` is provided.

**Location:** Subject level (e.g., `sub-01/sub-01_ses-01_scans.tsv`)

**Columns:**

- `filename` - Relative path to the motion files
- `acq_time` - Acquisition timestamp in ISO 8601 format

**Example content:**

```tsv
filename                                                         acq_time
motion/sub-01_ses-01_task-walk_tracksys-optical_motion.json     2025-11-05T14:30:00
motion/sub-01_ses-01_task-walk_tracksys-optical_motion.tsv      2025-11-05T14:30:00
```

!!! info "Automatic Creation"
    The scans file is created automatically when you provide `acq_time` in your `MotionData` object.

**Scans file behavior:**

- **Append mode**: Multiple exports to the same subject/session append to the same scans file
- **Update mode**: If the same filename exists, its timestamp is updated
- **Relative paths**: Paths are relative to the scans.tsv location

## Advanced Export Options

### Exporting Individual File Types

You can export files individually if needed:

```python
from motionbids import (
    export_json_metadata,
    export_tsv_data,
    export_channels_tsv,
    export_scans_tsv
)

# Export JSON only
json_path = export_json_metadata(
    motion,
    out_dir="my_study/sub-01/ses-01/motion/"
)

# Export TSV data only
tsv_path = export_tsv_data(
    motion,
    out_dir="my_study/sub-01/ses-01/motion/"
)

# Export channels file only
channels_path = export_channels_tsv(
    motion,
    out_dir="my_study/sub-01/ses-01/motion/"
)

# Export scans file (if acq_time provided)
if motion.acq_time:
    scans_path = export_scans_tsv(
        motion,
        out_dir="my_study/sub-01/ses-01/motion/",
        subject_dir="my_study/sub-01/"
    )
```

### Creating Directory Structure

Create the full BIDS directory structure before exporting:

```python
from motionbids import create_bids_directory_structure

# Creates: base_dir/sub-{subject_id}/ses-{session_id}/motion/
motion_dir = create_bids_directory_structure(
    base_dir="my_study",
    subject_id="01",
    session_id="01"  # Optional
)

# Returns Path object pointing to the motion directory
print(motion_dir)
# Output: my_study/sub-01/ses-01/motion
```

### Exporting Dataset Description

Create a BIDS dataset description file:

```python
from motionbids import export_dataset_description

desc_path = export_dataset_description(
    bids_root="my_study",
    name="My Motion Study",
    authors=["Jane Doe", "John Smith"],
    dataset_type="raw",
    bids_version="1.9.0"  # Optional, defaults to "1.9.0"
)
```

**Creates:** `my_study/dataset_description.json`

**Content:**

```json
{
  "Name": "My Motion Study",
  "BIDSVersion": "1.9.0",
  "DatasetType": "raw",
  "Authors": [
    "Jane Doe",
    "John Smith"
  ]
}
```

## Complete Export Workflow

Here's a complete example showing the full export workflow:

```python
import numpy as np
from pathlib import Path
from motionbids import (
    MotionData,
    validate_motion_data,
    export_bids_motion,
    create_bids_directory_structure,
    export_dataset_description
)

# 1. Create motion data
motion = MotionData(
    subject_id="01",
    session_id="01",
    task_name="walk",
    tracksys="optical",
    acquisition="indoor",
    run=1,
    sampling_frequency=120.0,
    tracked_points_count=10,
    acq_time="2025-11-05T14:30:00",
    manufacturer="Vicon",
    data=np.random.randn(1200, 30),
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x','y','z']],
    units=["mm"] * 30
)

# 2. Validate
validate_motion_data(motion)
print("✓ Data validated")

# 3. Create directory structure
bids_root = Path("my_motion_study")
motion_dir = create_bids_directory_structure(
    base_dir=bids_root,
    subject_id="01",
    session_id="01"
)
print(f"✓ Created directory: {motion_dir}")

# 4. Export dataset description (once per dataset)
export_dataset_description(
    bids_root=bids_root,
    name="My Motion Study",
    authors=["Your Name"],
    dataset_type="raw"
)
print("✓ Created dataset_description.json")

# 5. Export motion data
files = export_bids_motion(
    data=motion,
    out_dir=motion_dir,
    validate=True,
    overwrite=True
)
print(f"✓ Exported files: {list(files.keys())}")

# Result:
# my_motion_study/
# ├── dataset_description.json
# └── sub-01/
#     ├── sub-01_ses-01_scans.tsv
#     └── ses-01/
#         └── motion/
#             ├── sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-01_motion.json
#             ├── sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-01_motion.tsv
#             └── sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-01_channels.tsv
```

## Export for Multiple Files

### Multiple Runs

```python
for run_num in [1, 2, 3]:
    motion = MotionData(
        subject_id="01",
        task_name="walk",
        tracksys="optical",
        run=run_num,
        sampling_frequency=120.0,
        tracked_points_count=10,
        acq_time=f"2025-11-05T{14+run_num}:00:00",  # Different times
        data=load_run_data(run_num),
        columns=columns,
        units=units
    )
    
    export_bids_motion(motion, out_dir=motion_dir, overwrite=True)

# Creates:
# sub-01_..._run-01_motion.json
# sub-01_..._run-02_motion.json
# sub-01_..._run-03_motion.json
```

### Multiple Sessions

```python
for session in ["01", "02"]:
    motion_dir = create_bids_directory_structure(
        base_dir=bids_root,
        subject_id="01",
        session_id=session
    )
    
    motion = MotionData(
        subject_id="01",
        session_id=session,
        task_name="walk",
        tracksys="optical",
        sampling_frequency=120.0,
        tracked_points_count=10,
        data=load_session_data(session),
        columns=columns,
        units=units
    )
    
    export_bids_motion(motion, out_dir=motion_dir, overwrite=True)

# Creates:
# sub-01/ses-01/motion/...
# sub-01/ses-02/motion/...
```

## File Naming Convention

BIDS filenames follow a strict entity order:

```
sub-<label>_ses-<label>_task-<label>_tracksys-<label>_acq-<label>_run-<index>_<suffix>.<extension>
```

**Entity order (required):**

1. `sub` - Subject ID (always first)
2. `ses` - Session ID (if provided)
3. `task` - Task name (always required)
4. `tracksys` - Tracking system (always required)
5. `acq` - Acquisition label (if provided)
6. `run` - Run index (if provided)

**Examples:**

```python
# Minimal
motion = MotionData(subject_id="01", task_name="walk", tracksys="optical", ...)
# Filename: sub-01_task-walk_tracksys-optical_motion.json

# With session
motion = MotionData(subject_id="01", session_id="01", task_name="walk", tracksys="optical", ...)
# Filename: sub-01_ses-01_task-walk_tracksys-optical_motion.json

# With all entities
motion = MotionData(
    subject_id="01", session_id="01", task_name="walk",
    tracksys="optical", acquisition="indoor", run=1, ...
)
# Filename: sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-01_motion.json
```

## Validation During Export

### Automatic Validation

By default, `export_bids_motion()` validates before exporting:

```python
# Validation enabled (default)
files = export_bids_motion(motion, out_dir="...", validate=True)

# Skip validation (not recommended)
files = export_bids_motion(motion, out_dir="...", validate=False)
```

### Validation Checks

The validator checks:

- ✅ All required fields present
- ✅ Field types correct
- ✅ Numeric values valid (positive sampling frequency, etc.)
- ✅ Data dimensions match (columns, units, data shape)
- ⚠️ Recommended fields present (warnings only)

### Handling Validation Errors

```python
from motionbids import ValidationError

try:
    files = export_bids_motion(motion, out_dir="...", validate=True)
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Fix the issue and try again
```

## Best Practices

### 1. Always Validate

```python
# ✓ Good: Validate before export
validate_motion_data(motion)
files = export_bids_motion(motion, out_dir="...", validate=True)

# ✗ Bad: Skip validation
files = export_bids_motion(motion, out_dir="...", validate=False)
```

### 2. Use Descriptive Channel Names

```python
# ✓ Good: Clear, parseable names
columns = ["LFHD_x", "LFHD_y", "LFHD_z", "RFHD_x", ...]

# ✗ Bad: Unclear names
columns = ["ch0", "ch1", "ch2", ...]
```

### 3. Provide Recommended Fields

```python
# ✓ Good: Include manufacturer info
motion = MotionData(
    ...,
    manufacturer="Vicon",
    manufacturers_model_name="Vantage V5",
    software_versions="Nexus 2.12"
)

# ⚠️ Okay but incomplete: Missing recommended fields
motion = MotionData(...)  # Will trigger warnings
```

### 4. Use Acquisition Timestamps

```python
# ✓ Good: Include acquisition time
motion = MotionData(
    ...,
    acq_time="2025-11-05T14:30:00"
)
# Creates scans.tsv automatically

# ✗ Missing: No temporal information
motion = MotionData(...)  # No acq_time
```

### 5. Organize by Session and Run

```python
# ✓ Good: Clear organization
motion = MotionData(
    subject_id="01",
    session_id="01",
    task_name="walk",
    run=1,
    ...
)

# ✓ Also good: Multiple runs per session
for run in [1, 2, 3]:
    motion = MotionData(subject_id="01", session_id="01", run=run, ...)
```

## Troubleshooting

### "File already exists"

Set `overwrite=True` to replace existing files:

```python
files = export_bids_motion(motion, out_dir="...", overwrite=True)
```

### "Directory does not exist"

Set `create_dirs=True` to create directories:

```python
files = export_bids_motion(motion, out_dir="...", create_dirs=True)
```

### "Cannot export data without columns"

Ensure `columns` are provided when `data` is present:

```python
motion = MotionData(
    ...,
    data=data,
    columns=column_names,  # Required when data is provided
    units=unit_names
)
```

## Next Steps

- [Validation Guide](validation.md) - Learn about validation rules
- [API Reference: Exporter](../api/exporter.md) - Complete API documentation
- [Data Format](../advanced/data-format.md) - Understanding data array format
