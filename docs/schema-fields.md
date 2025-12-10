# Motion Schema Fields

This page lists all BIDS-compliant fields for motion capture data, extracted from the BIDS schema.

## Field Organization

Fields are categorized by:
- **Requirement Level**: Required, Recommended, Optional
- **Field Type**: Entity (filename), Metadata (JSON), Data (arrays)

## Entity Fields

Entity fields appear in the BIDS filename and organize the dataset hierarchy.

### Required Entities

| Field | Python Name | BIDS Label | Description | Example |
|-------|-------------|------------|-------------|---------|
| Subject | `subject_id` | `sub` | Subject identifier | `"01"`, `"control01"` |
| Task | `task_name` | `task` | Task performed | `"walk"`, `"reach"` |
| Tracking System | `tracksys` | `tracksys` | Tracking technology | `"optical"`, `"imu"` |

### Optional Entities

| Field | Python Name | BIDS Label | Description | Example |
|-------|-------------|------------|-------------|---------|
| Session | `session_id` | `ses` | Session identifier | `"01"`, `"baseline"` |
| Acquisition | `acquisition` | `acq` | Acquisition parameters | `"indoor"`, `"outdoor"` |
| Run | `run` | `run` | Run index (1-indexed) | `1`, `2`, `3` |

**Entity order in filenames:**
```
sub-<label>_ses-<label>_task-<label>_tracksys-<label>_acq-<label>_run-<index>_motion.json
```

## Metadata Fields

Metadata fields appear in the `*_motion.json` sidecar file.

### Required Metadata

| Field | Python Name | BIDS Name | Type | Description |
|-------|-------------|-----------|------|-------------|
| Sampling Frequency | `sampling_frequency` | `SamplingFrequency` | `float` | Sampling rate in Hz (must be > 0) |
| Tracked Points Count | `tracked_points_count` | `TrackedPointsCount` | `int` | Number of markers/points tracked |

### Recommended Metadata

| Field | Python Name | BIDS Name | Type | Description |
|-------|-------------|-----------|------|-------------|
| Manufacturer | `manufacturer` | `Manufacturer` | `str` | System manufacturer name |
| Model Name | `manufacturers_model_name` | `ManufacturersModelName` | `str` | System model name |
| Software Version | `software_versions` | `SoftwareVersions` | `str` | Acquisition software version |
| Channel Count | `motion_channel_count` | `MotionChannelCount` | `int` | Total number of channels |
| Recording Duration | `recording_duration` | `RecordingDuration` | `float` | Duration in seconds |
| Recording Type | `recording_type` | `RecordingType` | `str` | Type of recording |

### Optional Metadata

| Field | Python Name | Description |
|-------|-------------|-------------|
| Custom Fields | `additional_metadata` | Dictionary of custom metadata fields |

**Example JSON output:**
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

## Tracking System Labels

The `tracksys` entity identifies the motion capture technology:

| Label | Technology | Common Systems |
|-------|------------|----------------|
| `optical` | Optical/camera-based | Vicon, Optitrack, Qualisys, PhaseSpace |
| `imu` | Inertial measurement units | Xsens, APDM, Movella, Noraxon |
| `video` | Video-based tracking | OpenPose, MediaPipe, DeepLabCut, Kinovea |
| `electromagnetic` | Electromagnetic tracking | Polhemus, NDI Aurora |
| `other` | Other tracking systems | Custom systems |

**Example usage:**
```python
# Optical motion capture
tracksys="optical"

# IMU sensors
tracksys="imu"

# Markerless video tracking
tracksys="video"
```

## Recording Types

The `recording_type` field specifies the data acquisition mode:

| Type | Description | Use Case |
|------|-------------|----------|
| `continuous` | Continuous recording | Most motion capture (default) |
| `discontinuous` | Multiple separate recordings | Interrupted sessions |
| `epoched` | Time-locked epochs | Event-related analyses |

## Data Array Fields

### Motion Data Array

| Field | Python Name | Type | Description |
|-------|-------------|------|-------------|
| Data | `data` | `np.ndarray` | Motion time series (rows=time, cols=channels) |
| Columns | `columns` | `List[str]` | Channel names (must match data columns) |
| Units | `units` | `List[str]` | Units per channel (must match columns) |

**Data format requirements:**
```python
# Correct format
data.shape = (n_timepoints, n_channels)
len(columns) = n_channels
len(units) = n_channels

# Example: 10 seconds at 120 Hz, 30 channels
data = np.random.randn(1200, 30)
columns = [f"marker{i}_{axis}" for i in range(10) for axis in ['x','y','z']]
units = ["mm"] * 30
```

## Channel Metadata

Channels are described in `*_channels.tsv` with these **required** fields:

| Column | Required | Description | Example Values |
|--------|----------|-------------|----------------|
| `name` | ✅ Yes | Full channel name | `marker0_x`, `LFHD_y`, `pelvis_quat_w` |
| `component` | ✅ Yes | Measurement component (validated) | `x`, `y`, `z`, `quat_x`, `quat_y`, `quat_z`, `quat_w`, `n/a` |
| `type` | ✅ Yes | Data type (validated, uppercase required) | `POS`, `ORNT`, `VEL`, `ACCEL`, `GYRO` |
| `tracked_point` | ✅ Yes | Point/marker label | `marker0`, `LFHD`, `pelvis` |
| `units` | ✅ Yes | Physical units | `mm`, `m`, `deg`, `rad`, `m/s` |

!!! important "Channel Validation"
    All five fields are **required** for each channel. The `component` and `type` values are validated against the BIDS schema to ensure compliance. Type values MUST be uppercase.

### Channel Components

Allowed values for the `component` column (from BIDS schema):

| Component | Description |
|-----------|-------------|
| `x` | Position along X-axis, rotation about X-axis, or magnetic field strength along X-axis |
| `y` | Position along Y-axis, rotation about Y-axis, or magnetic field strength along Y-axis |
| `z` | Position along Z-axis, rotation about Z-axis, or magnetic field strength along Z-axis |
| `quat_x` | Quaternion component associated with X-axis |
| `quat_y` | Quaternion component associated with Y-axis |
| `quat_z` | Quaternion component associated with Z-axis |
| `quat_w` | Non-axial quaternion component |
| `n/a` | Channels with no corresponding spatial axis |

!!! note "Quaternion Convention"
    When using quaternions for orientation, axial components MUST be specified as `quat_x`, `quat_y`, `quat_z`, and the non-axial component as `quat_w`.

### Channel Types

| Type | Description | Required Component |
|------|-------------|-------------------|
| `POS` | Position in space | `x`, `y`, or `z` |
| `ORNT` | Orientation | `x`, `y`, `z`, `quat_x`, `quat_y`, `quat_z`, or `quat_w` |
| `VEL` | Velocity | `x`, `y`, or `z` |
| `ACCEL` | Accelerometer | `x`, `y`, or `z` |
| `GYRO` | Gyrometer | `x`, `y`, or `z` |
| `ANGACCEL` | Angular acceleration | `x`, `y`, or `z` |
| `MAGN` | Magnetic field strength | `x`, `y`, or `z` |
| `JNTANG` | Joint angle between bodyparts | Angle in degrees |
| `LATENCY` | Sample latency from recording onset | In seconds (s[.000000]) |
| `MISC` | Miscellaneous channels | Any |

!!! warning "Uppercase Required"
    Channel type values MUST be uppercase (e.g., `POS`, not `pos`).

!!! note "Schema Validation"
    The package validates channel types and components against the BIDS schema. Only these values are allowed in the `*_channels.tsv` file.

**Example channels file:**
```tsv
name          component  type    tracked_point  units
marker0_x     x          POS     marker0        mm
marker0_y     y          POS     marker0        mm
marker0_z     z          POS     marker0        mm
pelvis_quat_w quat_w     ORNT    pelvis         n/a
pelvis_quat_x quat_x     ORNT    pelvis         n/a
pelvis_quat_y quat_y     ORNT    pelvis         n/a
pelvis_quat_z quat_z     ORNT    pelvis         n/a
COM_x         x          VEL     COM            m/s
head_x        x          ACCEL   head           m/s²
```

## Acquisition Time

The `acq_time` field enables temporal tracking via `*_scans.tsv`:

| Field | Format | Description | Example |
|-------|--------|-------------|---------|
| `acq_time` | ISO 8601 | Acquisition timestamp | `"2025-11-05T14:30:00"` |

**Format specifications:**
- **Date**: `YYYY-MM-DD`
- **Time**: `HH:MM:SS`
- **Optional**: Fractional seconds (`.ffffff`)
- **Full format**: `YYYY-MM-DDTHH:MM:SS[.ffffff]`

**Example scans file:**
```tsv
filename                                                  acq_time
motion/sub-01_ses-01_task-walk_tracksys-optical_motion.json  2025-11-05T14:30:00
motion/sub-01_ses-01_task-walk_tracksys-optical_motion.tsv   2025-11-05T14:30:00
```

## Units

Common units for motion data:

### Position
- `mm` - millimeters
- `m` - meters
- `cm` - centimeters

### Orientation
- `rad` - radians
- `deg` - degrees
- `n/a` - dimensionless (quaternions)

### Velocity
- `m/s` - meters per second
- `mm/s` - millimeters per second

### Acceleration
- `m/s²` - meters per second squared
- `g` - gravitational units

### Time
- `s` - seconds
- `ms` - milliseconds

### Other
- `a.u.` - arbitrary units

## Field Validation

### Required Field Checks
```python
✓ subject_id must be provided
✓ task_name must be provided
✓ tracksys must be provided
✓ sampling_frequency must be provided and > 0
✓ tracked_points_count must be provided and > 0
```

### Recommended Field Warnings
```python
⚠ manufacturer should be provided
⚠ manufacturers_model_name should be provided
⚠ software_versions should be provided
⚠ recording_type should be provided
```

### Data Consistency Checks
```python
✓ data.shape[1] == len(columns)
✓ len(units) == len(columns)
✓ run >= 1 (if provided)
✓ acq_time in ISO 8601 format (if provided)
```

## Complete Field Example

```python
from motionbids import MotionData, Channel
import numpy as np

# All field types demonstrated
motion = MotionData(
    # === REQUIRED ===
    # Entity fields
    subject_id="01",              # sub-01
    task_name="walk",             # task-walk
    tracksys="optical",           # tracksys-optical
    
    # Metadata fields
    sampling_frequency=120.0,     # SamplingFrequency
    tracked_points_count=10,      # TrackedPointsCount
    
    # === RECOMMENDED ===
    manufacturer="Vicon",                      # Manufacturer
    manufacturers_model_name="Vantage V5",    # ManufacturersModelName
    software_versions="Nexus 2.12",           # SoftwareVersions
    motion_channel_count=30,                  # MotionChannelCount
    recording_duration=10.0,                  # RecordingDuration
    recording_type="continuous",              # RecordingType
    
    # === OPTIONAL ===
    # Entity fields
    session_id="01",              # ses-01
    acquisition="indoor",         # acq-indoor
    run=1,                        # run-01
    
    # Timestamp
    acq_time="2025-11-05T14:30:00",  # ISO 8601
    
    # === DATA ===
    data=np.random.randn(1200, 30),  # Time series
    channels=[
        Channel(name=f"marker{i}_{axis}", component=axis, type="POS",
                tracked_point=f"marker{i}", units="mm")
        for i in range(10) for axis in ['x', 'y', 'z']
    ],
    
    # === CUSTOM ===
    additional_metadata={
        "CaptureVolume": "8m x 6m x 3m",
        "CalibrationDate": "2025-11-01",
        "AmbientTemperature": 22.5
    }
)
```

## Schema Source

These fields are defined in the [BIDS specification](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/motion.html) and automatically extracted using `bidsschematools`.

The `motionbids` package dynamically syncs with the BIDS schema to ensure compliance with specification updates.
