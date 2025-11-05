# BIDS Motion Fields Reference

This page describes all BIDS-compliant fields used in motion capture data, organized by requirement level and type.

## Understanding BIDS Motion Data

Motion capture data in BIDS follows the specification defined in the [BIDS motion extension](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/motion.html).

### Field Categories

Fields are organized into three categories:

- **Required**: Must always be provided (errors if missing)
- **Recommended**: Should be provided when available (warnings if missing)
- **Optional**: Additional fields for more detailed metadata

## Required Fields

These fields **must** be provided for BIDS compliance. The package will raise an error if any are missing.

### Entity Fields (Filename Components)

These fields appear in the BIDS filename and identify the data:

#### `subject_id`

- **Type**: `str`
- **BIDS Name**: `sub`
- **Description**: Subject identifier
- **Example**: `"01"`, `"control01"`, `"patient001"`
- **Filename**: `sub-01_...`

```python
subject_id="01"  # Creates "sub-01" in filename
```

!!! warning "Naming Rules"
    - Use only alphanumeric characters and hyphens
    - No spaces or special characters
    - Should be unique within your dataset

#### `task_name`

- **Type**: `str`
- **BIDS Name**: `TaskName`
- **Description**: Name of the task performed during recording
- **Example**: `"walk"`, `"reach"`, `"balance"`, `"rest"`
- **Filename**: `task-walk_...`

```python
task_name="walk"  # Describes what the subject was doing
```

#### `tracksys`

- **Type**: `str`
- **BIDS Name**: `tracksys`
- **Description**: Tracking system label identifying the technology used
- **Required**: Yes (always required in motion BIDS)
- **Filename**: `tracksys-optical_...`

**Common Values**:

| Value | Description | Examples |
|-------|-------------|----------|
| `optical` | Optical/camera-based | Vicon, Optitrack, Qualisys |
| `imu` | Inertial measurement units | Xsens, APDM, Movella |
| `video` | Video-based tracking | OpenPose, MediaPipe, DeepLabCut |
| `electromagnetic` | EM tracking | Polhemus, NDI Aurora |
| `other` | Other tracking systems | Custom systems |

```python
tracksys="optical"  # For camera-based systems like Vicon
tracksys="imu"      # For inertial sensors like Xsens
tracksys="video"    # For markerless video tracking
```

!!! note "Entity Order"
    In BIDS filenames, entities appear in a specific order:
    `sub-<label>_ses-<label>_task-<label>_tracksys-<label>_acq-<label>_run-<index>`

### Metadata Fields (JSON File)

These required fields appear in the `*_motion.json` metadata file:

#### `sampling_frequency`

- **Type**: `float`
- **BIDS Name**: `SamplingFrequency`
- **Description**: Sampling frequency in Hz
- **Units**: Hertz (Hz)
- **Example**: `120.0`, `100.0`, `240.0`

```python
sampling_frequency=120.0  # 120 samples per second
```

!!! warning "Validation"
    Must be a positive number > 0

#### `tracked_points_count`

- **Type**: `float` (can be integer)
- **BIDS Name**: `TrackedPointsCount`
- **Description**: Number of tracked points/markers in the recording
- **Example**: `10`, `41`, `53`

```python
tracked_points_count=10  # 10 markers tracked
```

!!! note "Channels vs Points"
    If you track 10 markers in 3D (x, y, z), you have:
    
    - `tracked_points_count=10` (10 markers)
    - `motion_channel_count=30` (10 × 3 coordinates)

## Recommended Fields

These fields **should** be provided when available. The validator will issue warnings (not errors) if missing.

#### `manufacturer`

- **Type**: `str`
- **BIDS Name**: `Manufacturer`
- **Description**: Manufacturer of the motion capture system
- **Example**: `"Vicon"`, `"Optitrack"`, `"Xsens"`, `"Qualisys"`

```python
manufacturer="Vicon"
```

#### `manufacturers_model_name`

- **Type**: `str`
- **BIDS Name**: `ManufacturersModelName`
- **Description**: Model name of the motion capture system
- **Example**: `"Vantage V5"`, `"Flex 13"`, `"MVN Awinda"`

```python
manufacturers_model_name="Vantage V5"
```

#### `software_versions`

- **Type**: `str`
- **BIDS Name**: `SoftwareVersions`
- **Description**: Software version used for data acquisition
- **Example**: `"Nexus 2.12"`, `"Motive 3.1"`, `"QTM 2023.1"`

```python
software_versions="Nexus 2.12"
```

#### `motion_channel_count`

- **Type**: `int`
- **BIDS Name**: `MotionChannelCount`
- **Description**: Total number of motion channels (typically tracked_points × dimensions)
- **Example**: `30` (10 markers × 3 dimensions), `246` (41 markers × 6 DOF)

```python
motion_channel_count=30  # 10 markers with x, y, z each
```

#### `recording_duration`

- **Type**: `float`
- **BIDS Name**: `RecordingDuration`
- **Description**: Duration of the recording in seconds
- **Units**: Seconds
- **Example**: `10.0`, `30.5`, `120.0`

```python
recording_duration=10.0  # 10 seconds
# Can be calculated: n_timepoints / sampling_frequency
```

#### `recording_type`

- **Type**: `str`
- **BIDS Name**: `RecordingType`
- **Description**: Type of recording
- **Default**: `"continuous"`
- **Values**: `"continuous"`, `"discontinuous"`, `"epoched"`

```python
recording_type="continuous"  # Most common for motion data
```

## Optional Fields

These fields provide additional context and are not required.

### Optional Entity Fields

#### `session_id`

- **Type**: `str`
- **BIDS Name**: `ses`
- **Description**: Session identifier for multi-session studies
- **Example**: `"01"`, `"baseline"`, `"postop"`
- **Filename**: `ses-01_...`

```python
session_id="01"  # First session
session_id="baseline"  # Baseline measurement
```

#### `acquisition`

- **Type**: `str`
- **BIDS Name**: `acq`
- **Description**: Acquisition label to distinguish different acquisition parameters
- **Example**: `"indoor"`, `"outdoor"`, `"highspeed"`, `"calibrated"`
- **Filename**: `acq-indoor_...`

```python
acquisition="indoor"  # Indoor capture
acquisition="outdoor"  # Outdoor capture
```

#### `run`

- **Type**: `int`
- **BIDS Name**: `run`
- **Description**: Run index for repeated measurements
- **Example**: `1`, `2`, `3`
- **Filename**: `run-01_...`

```python
run=1  # First run
run=2  # Second run
```

!!! note "Run Numbering"
    Runs are 1-indexed (start at 1, not 0)

### Optional Metadata Fields

#### `acq_time`

- **Type**: `str`
- **BIDS Name**: (not in JSON, used for scans.tsv)
- **Description**: Acquisition timestamp in ISO 8601 format
- **Format**: `YYYY-MM-DDTHH:MM:SS[.ffffff]`
- **Example**: `"2025-11-05T14:30:00"`, `"2025-11-05T14:30:00.123456"`

```python
acq_time="2025-11-05T14:30:00"  # Without fractional seconds
acq_time="2025-11-05T14:30:00.123456"  # With microseconds
```

!!! info "Triggers scans.tsv"
    When `acq_time` is provided, a `scans.tsv` file is automatically created with the acquisition timestamp.

### Data Arrays

#### `data`

- **Type**: `numpy.ndarray`
- **Description**: Motion time series data
- **Shape**: `(n_timepoints, n_channels)`
- **Format**: Rows = timepoints, Columns = channels

```python
import numpy as np
data = np.random.randn(1200, 30)  # 1200 timepoints, 30 channels
```

!!! warning "Data Format"
    - Rows must be timepoints (samples)
    - Columns must be channels
    - Shape: `(n_timepoints, n_channels)`

#### `columns`

- **Type**: `List[str]`
- **Description**: Names of channels/columns in the data
- **Length**: Must match `data.shape[1]`
- **Example**: `["marker0_x", "marker0_y", "marker0_z", ...]`

```python
columns = [f"marker{i}_{axis}" for i in range(10) for axis in ['x', 'y', 'z']]
# Creates: ['marker0_x', 'marker0_y', 'marker0_z', 'marker1_x', ...]
```

!!! tip "Channel Naming"
    Use descriptive names that include:
    
    - Tracked point identifier (e.g., `marker0`, `LFHD`, `pelvis`)
    - Component/axis (e.g., `_x`, `_y`, `_z`, `_qw`, `_qx`)

#### `units`

- **Type**: `List[str]`
- **Description**: Units for each channel
- **Length**: Must match `len(columns)`
- **Common Values**: `"mm"`, `"m"`, `"deg"`, `"rad"`, `"a.u."`

```python
units = ["mm"] * 30  # All channels in millimeters
units = ["mm"] * 24 + ["deg"] * 6  # Mixed units: position + orientation
```

### Custom Metadata

#### `additional_metadata`

- **Type**: `Dict[str, Any]`
- **Description**: Dictionary for custom metadata not covered by BIDS fields
- **Example**: Calibration info, environment details, etc.

```python
additional_metadata={
    "CaptureVolume": "8m x 6m x 3m",
    "CalibrationDate": "2025-11-01",
    "CalibrationError": 0.5,
    "AmbientTemperature": 22.5
}
```

## Field Validation Rules

### Required Field Validation

```python
# ✓ Valid: All required fields provided
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10
)

# ✗ Invalid: Missing tracksys (raises ValueError)
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
sampling_frequency=120.0  # Positive number

# ✗ Invalid (raises ValueError)
sampling_frequency=-120.0  # Negative number
sampling_frequency=0.0     # Zero
```

### Array Dimension Validation

```python
# ✓ Valid: Dimensions match
data = np.random.randn(1000, 30)
columns = ["ch0", "ch1", ..., "ch29"]  # 30 names
units = ["mm"] * 30  # 30 units

# ✗ Invalid: Dimension mismatch (raises ValueError)
data = np.random.randn(1000, 30)
columns = ["ch0", "ch1", ..., "ch19"]  # Only 20 names (should be 30)
```

## Complete Field Example

Here's a complete example using all field types:

```python
import numpy as np
from motionbids import MotionData

# Generate sample data
n_timepoints = 1200  # 10 seconds at 120 Hz
n_markers = 10
n_channels = n_markers * 3

data = np.random.randn(n_timepoints, n_channels) * 10 + 100

motion = MotionData(
    # ===== REQUIRED FIELDS =====
    # Required entities (in filename)
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    
    # Required metadata (in JSON)
    sampling_frequency=120.0,
    tracked_points_count=10,
    
    # ===== RECOMMENDED FIELDS =====
    manufacturer="Vicon",
    manufacturers_model_name="Vantage V5",
    software_versions="Nexus 2.12",
    motion_channel_count=30,
    recording_duration=10.0,
    recording_type="continuous",
    
    # ===== OPTIONAL ENTITY FIELDS =====
    session_id="01",
    acquisition="indoor",
    run=1,
    
    # ===== OPTIONAL METADATA =====
    acq_time="2025-11-05T14:30:00",
    
    # ===== DATA ARRAYS =====
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x', 'y', 'z']],
    units=["mm"] * 30,
    
    # ===== CUSTOM METADATA =====
    additional_metadata={
        "CaptureVolume": "8m x 6m x 3m",
        "CalibrationDate": "2025-11-01",
        "CalibrationError": 0.5
    }
)
```

## Field Mapping to BIDS Files

### Filename (`*_motion.json`, `*_motion.tsv`)

Entity fields appear in the filename in this order:

```
sub-<subject_id>_ses-<session_id>_task-<task_name>_tracksys-<tracksys>_acq-<acquisition>_run-<run>_motion.json
```

Example:
```
sub-01_ses-01_task-walk_tracksys-optical_acq-indoor_run-01_motion.json
```

### JSON Metadata File (`*_motion.json`)

Metadata fields appear in the JSON file:

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
  "RecordingType": "continuous",
  "CaptureVolume": "8m x 6m x 3m",
  "CalibrationDate": "2025-11-01"
}
```

!!! note "Field Names"
    - Python fields use `snake_case`: `sampling_frequency`
    - BIDS JSON uses `PascalCase`: `SamplingFrequency`
    - The package handles conversion automatically

### Channels File (`*_channels.tsv`)

Channel information is stored separately:

```tsv
name          component  type  tracked_point  units
marker0_x     x          POS   marker0        mm
marker0_y     y          POS   marker0        mm
marker0_z     z          POS   marker0        mm
...
```

### Scans File (`*_scans.tsv`)

When `acq_time` is provided, a scans file is created at the subject level:

```tsv
filename                                                          acq_time
motion/sub-01_ses-01_task-walk_tracksys-optical_motion.json      2025-11-05T14:30:00
```

## Next Steps

- [Creating Motion Data](creating-data.md) - Detailed guide on data preparation
- [Exporting to BIDS](exporting.md) - Understanding the export process
- [Validation](validation.md) - Learn about validation rules
