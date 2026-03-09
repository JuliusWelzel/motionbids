# MotionData Class Reference

The `MotionData` class is the core of motionbids, representing a single motion capture recording with BIDS-compliant metadata.

## Class Overview

```python
from motionbids import MotionData, Channel
import numpy as np

# Example: 10 markers, each with x, y, z components
n_markers = 10
n_channels = n_markers * 3

# Create channel metadata following BIDS schema
channels = [
    Channel(
        channel_name=f"marker{i}_{axis}",
        channel_component=axis,
        channel_type="POS",
        channel_tracked_point=f"marker{i}",
        channel_units="mm"
    )
    for i in range(n_markers)
    for axis in ['x', 'y', 'z']
]

motion = MotionData(
    # Required fields
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    
    # Data and channels (REQUIRED)
    data=np.random.randn(1200, n_channels),
    channels=channels
)
```

## Field Categories

### Required Fields

Must be provided for all motion data:

| Field | Type | BIDS Name | Description |
|-------|------|-----------|-------------|
| `subject_id` | `str` | `sub` | Subject identifier |
| `task_name` | `str` | `TaskName` | Task performed (e.g., "walk") |
| `tracksys` | `str` | `tracksys` | Tracking system (e.g., "optical") |
| `sampling_frequency` | `float` | `SamplingFrequency` | Sampling rate in Hz |
| `tracked_points_count` | `int` | `TrackedPointsCount` | Number of markers/points |

### Recommended Fields

Should be provided when available:

| Field | Type | BIDS Name | Description |
|-------|------|-----------|-------------|
| `manufacturer` | `str` | `Manufacturer` | System manufacturer |
| `manufacturers_model_name` | `str` | `ManufacturersModelName` | System model |
| `software_versions` | `str` | `SoftwareVersions` | Acquisition software |
| `motion_channel_count` | `int` | `MotionChannelCount` | Total channels |
| `recording_duration` | `float` | `RecordingDuration` | Duration in seconds |
| `recording_type` | `str` | `RecordingType` | Type (default: "continuous") |

### Optional Entity Fields

For organizing multi-session/run studies:

| Field | Type | BIDS Name | Description |
|-------|------|-----------|-------------|
| `session_id` | `str` | `ses` | Session identifier |
| `acquisition` | `str` | `acq` | Acquisition label |
| `run` | `int` | `run` | Run index (1-indexed) |
| `acq_time` | `str` | - | ISO 8601 timestamp |

### Data Fields

Time series data and channel configuration:

| Field | Type | Description |
|-------|------|-------------|
| `data` | `np.ndarray` | Motion data (rows=time, cols=channels) - **REQUIRED** |
| `channels` | `List[Channel]` | Channel metadata objects - **REQUIRED** |
| `additional_metadata` | `Dict` | Custom metadata fields |

!!! info "Channel Objects Required"
    The `channels` field is **required** when providing data. It must be a list of `Channel` objects, and the length must match the number of columns in the data array. Each Channel object contains: `name`, `component`, `type`, `tracked_point`, `units` (all required), plus optional fields like `placement`, `reference_frame`, `description`, `sampling_frequency`, `status`, and `status_description`. Channel validation happens during Channel construction following BIDS schema.

## Relations to BIDS

### Filename Mapping

Entity fields appear in the BIDS filename in this order:

```python
motion = MotionData(
    subject_id="01",
    session_id="01",
    task_name="walk",
    tracksys="optical",
    acquisition="indoor",
    run=1
)

filename = motion.get_bids_filename()
# Result: sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-01_motion.json
```

**Entity order (required by BIDS):**
1. `sub` (always first)
2. `ses` (if provided)
3. `task` (required)
4. `tracksys` (required for motion)
5. `acq` (if provided)
6. `run` (if provided)

### JSON Metadata Mapping

Metadata fields are written to the `*_motion.json` file with BIDS-compliant names:

| Python Field | JSON Field |
|--------------|------------|
| `task_name` | `TaskName` |
| `sampling_frequency` | `SamplingFrequency` |
| `tracked_points_count` | `TrackedPointsCount` |
| `manufacturer` | `Manufacturer` |
| `manufacturers_model_name` | `ManufacturersModelName` |
| `software_versions` | `SoftwareVersions` |
| `motion_channel_count` | `MotionChannelCount` |
| `recording_duration` | `RecordingDuration` |
| `recording_type` | `RecordingType` |

**Example JSON output:**
```json
{
  "TaskName": "walk",
  "SamplingFrequency": 120.0,
  "TrackedPointsCount": 10,
  "Manufacturer": "Vicon",
  "ManufacturersModelName": "Vantage V5",
  "RecordingType": "continuous"
}
```

### TSV Data Mapping

The `data` array is written to `*_motion.tsv`:
- **Rows**: timepoints (samples)
- **Columns**: channels
- **Format**: Tab-separated, no headers (per BIDS spec)

```python
data = np.array([
    [100.23, 150.45, 75.12],  # timepoint 0
    [100.25, 150.48, 75.15],  # timepoint 1
    [100.27, 150.51, 75.18]   # timepoint 2
])
```

### Channels File Mapping

The `columns`, `units`, and channel metadata lists define the `*_channels.tsv` structure:

```python
columns = ["marker0_x", "marker0_y", "marker0_z"]
units = ["mm", "mm", "mm"]
channel_component = ["x", "y", "z"]
channel_type = ["POS", "POS", "POS"]
channel_tracked_point = ["marker0", "marker0", "marker0"]
```

**Generates:**
```
name         component  type  tracked_point  units
marker0_x    x          POS   marker0        mm
marker0_y    y          POS   marker0        mm
marker0_z    z          POS   marker0        mm
```

**Valid component values:**
- `x`, `y`, `z` - Spatial axes
- `quat_w`, `quat_x`, `quat_y`, `quat_z` - Quaternion components
- `n/a` - Not applicable

**Valid type values (uppercase required):**
- `POS` - Position
- `ORNT` - Orientation
- `VEL` - Velocity
- `ACCEL` - Acceleration
- `GYRO` - Gyroscope
- `ANGACCEL` - Angular acceleration
- `MAGN` - Magnetometer
- `JNTANG` - Joint angle
- `LATENCY` - Latency
- `MISC` - Miscellaneous

**Component-type compatibility is validated:**
- Quaternion components (`quat_*`) can only be used with `ORNT` type
- Spatial components (`x`, `y`, `z`) can be used with `POS`, `VEL`, `ACCEL`, `GYRO`, `MAGN`, `ANGACCEL` types

### Scans File Mapping

When `acq_time` is provided, a `*_scans.tsv` file is created:

```python
motion = MotionData(
    subject_id="01",
    session_id="01",
    task_name="walk",
    acq_time="2025-11-05T14:30:00",
    ...
)
```

**Creates: `sub-01/sub-01_ses-01_scans.tsv`**
```
filename                                                  acq_time
motion/sub-01_ses-01_task-walk_tracksys-optical_motion.json  2025-11-05T14:30:00
```

### Participants File

Use `export_participants_tsv` to create or update a `participants.tsv` at the
dataset root. Existing entries for other participants are preserved.

```python
from motionbids import export_participants_tsv

export_participants_tsv(
    bids_root="my_study",
    participant_id="01",   # "sub-" prefix added automatically
    age="25",
    sex="F",
    handedness="R",
    group="control"        # extra columns via **kwargs
)
```

**Creates / updates: `participants.tsv`**
```
participant_id	age	sex	handedness	group
sub-01	25	F	R	control
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `bids_root` | `str \| Path` | Dataset root directory |
| `participant_id` | `str` | Subject ID (auto-prefixed with `sub-`) |
| `age` | `str` (optional) | Participant age |
| `sex` | `str` (optional) | `"M"`, `"F"`, or `"O"` |
| `handedness` | `str` (optional) | `"L"`, `"R"`, or `"A"` |
| `**kwargs` | | Additional columns (e.g., `group="control"`) |

**Behaviour:**

- If `participants.tsv` does not exist → creates file with header + row.
- If it exists and the participant is new → appends a row.
- If it exists and the participant already has a row → updates that row.
- A `UserWarning` is emitted when the file already exists.

## Class Methods

### `get_bids_filename(suffix, extension)`

Generate BIDS-compliant filename.

```python
motion.get_bids_filename()
# 'sub-01_task-walk_tracksys-optical_motion.json'

motion.get_bids_filename(suffix="channels", extension="tsv")
# 'sub-01_task-walk_tracksys-optical_channels.tsv'
```

**Parameters:**
- `suffix` (str): BIDS suffix (default: "motion")
- `extension` (str): File extension without dot (default: "json")

**Returns:** BIDS filename string

**Raises:** `ValueError` if `tracksys` is not provided

### `to_metadata_dict()`

Convert to dictionary for JSON export.

```python
metadata = motion.to_metadata_dict()
# {
#   "TaskName": "walk",
#   "SamplingFrequency": 120.0,
#   "TrackedPointsCount": 10,
#   ...
# }
```

**Returns:** Dictionary with BIDS-compliant field names (PascalCase)

**Excludes:**
- Entity fields (in filename)
- `data`, `columns`, `units` (in separate files)

## Data Format Requirements

### Array Shape
```python
# ✓ Correct: rows=time, columns=channels
data = np.random.randn(1000, 30)  # 1000 timepoints, 30 channels

# ✗ Wrong: transposed
data = np.random.randn(30, 1000)  # Would interpret as 30 timepoints!
```

### Dimension Matching
```python
# All must match:
data.shape[1] == len(columns) == len(units)

# Example:
data = np.random.randn(1200, 30)  # 30 channels
columns = [f"ch{i}" for i in range(30)]  # 30 names
units = ["mm"] * 30  # 30 units
```

## Validation Rules

### Required Field Validation
```python
# ✓ Valid
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10
)

# ✗ Missing tracksys → ValueError
motion = MotionData(
    subject_id="01",
    task_name="walk",
    sampling_frequency=120.0,
    tracked_points_count=10
)
```

### Numeric Validation
```python
# ✓ Valid
sampling_frequency = 120.0  # Positive

# ✗ Invalid → ValueError
sampling_frequency = 0.0     # Zero
sampling_frequency = -120.0  # Negative
```

### Run Validation
```python
# ✓ Valid
run = 1  # 1-indexed

# ✗ Invalid → ValueError
run = 0  # Must be >= 1
```

## Complete Example

```python
import numpy as np
from motionbids import MotionData

# Generate sample data
n_timepoints = 1200
n_markers = 10
data = np.random.randn(n_timepoints, n_markers * 3)

# Create motion object with all field types
motion = MotionData(
    # Required
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    
    # Recommended
    manufacturer="Vicon",
    manufacturers_model_name="Vantage V5",
    software_versions="Nexus 2.12",
    motion_channel_count=30,
    recording_duration=10.0,
    recording_type="continuous",
    
    # Optional entities
    session_id="01",
    acquisition="indoor",
    run=1,
    acq_time="2025-11-05T14:30:00",
    
    # Data and channels
    data=data,
    channels=channels,
    
    # Custom
    additional_metadata={
        "CaptureVolume": "8m x 6m x 3m",
        "CalibrationDate": "2025-11-01"
    }
)

# Access fields
print(motion.subject_id)  # "01"
print(motion.task_name)   # "walk"
print(motion.data.shape)  # (1200, 30)
print(len(motion.channels))  # 30

# Generate filename
filename = motion.get_bids_filename()
# "sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-01_motion.json"

# Export metadata
metadata = motion.to_metadata_dict()
# {"TaskName": "walk", "SamplingFrequency": 120.0, ...}
```

## BIDS Compliance Summary

| Python Component | BIDS File/Field | Purpose |
|-----------------|-----------------|---------|
| Entity fields | Filename entities | Organize dataset hierarchy |
| Metadata fields | `*_motion.json` | Acquisition parameters |
| `data` array | `*_motion.tsv` | Time series data |
| `columns` + `units` | `*_channels.tsv` | Channel descriptions |
| `acq_time` | `*_scans.tsv` | Acquisition timestamps |

**Key principle:** Python uses `snake_case`, BIDS uses `PascalCase`. The package handles all conversions automatically.
