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

Channels are described in `*_channels.tsv` with these fields:

| Column | Description | Example Values |
|--------|-------------|----------------|
| `name` | Full channel name | `marker0_x`, `LFHD_y`, `pelvis_qw` |
| `component` | Measurement component | `x`, `y`, `z`, `qw`, `qx`, `qy`, `qz` |
| `type` | Data type | `POS`, `ORNT`, `VEL`, `ACCEL`, `ANGVEL` |
| `tracked_point` | Point/marker label | `marker0`, `LFHD`, `pelvis` |
| `units` | Physical units | `mm`, `m`, `deg`, `rad`, `m/s` |

### Channel Types

| Type | Full Name | Description | Common Components |
|------|-----------|-------------|-------------------|
| `POS` | Position | 3D position | `x`, `y`, `z` |
| `ORNT` | Orientation | Quaternion orientation | `qw`, `qx`, `qy`, `qz` |
| `VEL` | Velocity | Linear velocity | `vx`, `vy`, `vz` |
| `ACCEL` | Acceleration | Linear acceleration | `ax`, `ay`, `az` |
| `ANGVEL` | Angular Velocity | Angular velocity | `wx`, `wy`, `wz` |
| `OTHER` | Other | Other measurements | (any) |

**Example channels file:**
```tsv
name          component  type    tracked_point  units
marker0_x     x          POS     marker0        mm
marker0_y     y          POS     marker0        mm
marker0_z     z          POS     marker0        mm
pelvis_qw     qw         ORNT    pelvis         n/a
pelvis_qx     qx         ORNT    pelvis         n/a
COM_vx        vx         VEL     COM            m/s
head_ax       ax         ACCEL   head           m/s²
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
from motionbids import MotionData
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
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x','y','z']],
    units=["mm"] * 30,
    
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
