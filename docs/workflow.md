# Complete Workflow

This guide demonstrates a full workflow from raw motion data to a BIDS-compliant dataset.

## Installation

```bash
pip install motionbids
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install motionbids
```

For development:

```bash
git clone https://github.com/JuliusWelzel/motionbids.git
cd motionbids
pip install -e ".[dev]"
```

## Basic Workflow

### Step 1: Prepare Your Data

Motion data should be a NumPy array with:
- **Rows**: timepoints (samples)
- **Columns**: channels (e.g., marker positions)

```python
import numpy as np
from motionbids import MotionData, Channel, validate_motion_data, export_bids_motion

# Example: 10 markers tracked at 120 Hz for 10 seconds
n_timepoints = 1200  # 10 seconds × 120 Hz
n_markers = 10
n_channels = n_markers * 3  # x, y, z for each marker

# Load or generate your data (rows=time, columns=channels)
data = np.random.randn(n_timepoints, n_channels)

# Define channel metadata (REQUIRED for BIDS compliance)
# Each channel needs: channel_name, channel_component, channel_type, channel_tracked_point, channel_units
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
```

### Step 2: Create MotionData Object

```python
motion = MotionData(
    # Required fields
    subject_id="01",
    task_name="walk",
    tracksys="optical",  # optical, imu, video, etc.
    sampling_frequency=120.0,
    tracked_points_count=10,
    
    # Recommended fields
    manufacturer="Vicon",
    manufacturers_model_name="Vantage V5",
    recording_type="continuous",
    
    # Optional session/run info
    session_id="01",
    run=1,
    acquisition="indoor",
    acq_time="2025-11-05T14:30:00",
    
    # Data and channels (REQUIRED)
    data=data,
    channels=channels  # List of Channel objects
)
```

### Step 3: Validate and Export

```python
# Validate BIDS compliance
validate_motion_data(motion)
print("✓ Data is BIDS compliant!")

# Export to BIDS format
files = export_bids_motion(
    motion,
    out_dir="bids_dataset/sub-01/ses-01/motion/",
    validate=True,
    overwrite=True
)

print(f"Created: {list(files.keys())}")
# Output: ['json', 'tsv', 'channels', 'scans']
```

## Complete Dataset Example

### Full BIDS Dataset Creation

```python
from pathlib import Path
from motionbids import (
    MotionData,
    export_bids_motion,
    create_bids_directory_structure,
    export_dataset_description,
    export_participants_tsv,
)

# 1. Setup BIDS root directory
bids_root = Path("my_motion_study")

# 2. Create dataset description
export_dataset_description(
    bids_root=bids_root,
    name="Motion Capture Study",
    authors=["Your Name"],
    dataset_channel_type="raw"
)

# 3. Process each subject
for subject_id in ["01", "02", "03"]:
    # Record participant demographics
    export_participants_tsv(bids_root, participant_id=subject_id, age="25", sex="F")

    for session_id in ["01", "02"]:
        # Create directory structure
        motion_dir = create_bids_directory_structure(
            base_dir=bids_root,
            subject_id=subject_id,
            session_id=session_id
        )
        
        # Create motion data
        data = load_subject_data(subject_id, session_id)  # Your function
        
        motion = MotionData(
            subject_id=subject_id,
            session_id=session_id,
            task_name="walk",
            tracksys="optical",
            sampling_frequency=120.0,
            tracked_points_count=10,
            manufacturer="Vicon",
            data=data,
            channels=channels,  # List of Channel objects
            acq_time=get_timestamp(subject_id, session_id)  # Your function
        )
        
        # Export
        export_bids_motion(motion, out_dir=motion_dir, validate=True)

print(f"✓ Dataset created at {bids_root}")
```

### Output Structure

```
my_motion_study/
├── dataset_description.json
├── participants.tsv
├── sub-01/
│   ├── sub-01_ses-01_scans.tsv
│   ├── sub-01_ses-02_scans.tsv
│   ├── ses-01/
│   │   └── motion/
│   │       ├── sub-01_ses-01_task-walk_tracksys-optical_motion.json
│   │       ├── sub-01_ses-01_task-walk_tracksys-optical_motion.tsv
│   │       └── sub-01_ses-01_task-walk_tracksys-optical_channels.tsv
│   └── ses-02/
│       └── motion/
│           └── ...
├── sub-02/
│   └── ...
└── sub-03/
    └── ...
```

## Output Files Explained

### 1. JSON Metadata (`*_motion.json`)
Contains acquisition parameters:
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

### 2. TSV Data (`*_motion.tsv`)
Time series data (no headers, per BIDS spec):
```
100.23  150.45  75.12  ...
100.25  150.48  75.15  ...
100.27  150.51  75.18  ...
```

### 3. Channels File (`*_channels.tsv`)
Channel descriptions:
```
name             component  type  tracked_point  units
marker0_x        x          POS   marker0        mm
marker0_y        y          POS   marker0        mm
marker0_z        z          POS   marker0        mm
pelvis_quat_w    quat_w     ORNT  pelvis         n/a
```

### 4. Scans File (`*_scans.tsv`)
Acquisition timestamps (when `acq_time` provided):
```
filename                                                  acq_time
motion/sub-01_ses-01_task-walk_tracksys-optical_motion.json  2025-11-05T14:30:00
```

### 5. Dataset Description (`dataset_description.json`)
Create a dataset description with additional fields:
```python
from motionbids import export_dataset_description

export_dataset_description(
    bids_root="my_motion_study",
    name="Motion Capture Study",
    authors=["Jane Doe", "John Smith"],
    License="CC0",
    Acknowledgements="Thanks to our participants",
    Funding=["NIH Grant 12345"]
)
```

### 6. Participants File (`participants.tsv`)
Store participant information. The file is created or updated automatically —
existing entries for other participants are preserved:
```python
from motionbids import export_participants_tsv

# Create / append participant entries
export_participants_tsv(
    bids_root="my_motion_study",
    participant_id="01",
    age="25",
    sex="F",
    handedness="R",
    group="control"        # extra columns are supported via **kwargs
)

# A second call appends a new row (or updates if the participant already exists)
export_participants_tsv(
    bids_root="my_motion_study",
    participant_id="02",
    age="30",
    sex="M",
    handedness="L",
    group="patient"
)
```

Output (`participants.tsv`):
```
participant_id	age	sex	handedness	group
sub-01	25	F	R	control
sub-02	30	M	L	patient
```

!!! note
    If `participants.tsv` already exists (e.g., from a prior EEG conversion),
    a `UserWarning` is emitted. Existing rows are preserved; only the row for
    the given `participant_id` is added or updated.

## Common Patterns

### Multiple Runs
```python
for run_num in [1, 2, 3]:
    motion = MotionData(
        subject_id="01",
        task_name="walk",
        tracksys="optical",
        run=run_num,  # Increment run
        sampling_frequency=120.0,
        tracked_points_count=10,
        data=load_run(run_num),
        channels=channels  # List of Channel objects
    )
    export_bids_motion(motion, out_dir=motion_dir)
```

### Loading from CSV
```python
import pandas as pd

# Load motion data from CSV
df = pd.read_csv("motion_capture.csv")
data = df.values  # Convert to NumPy array
columns = df.columns.tolist()

# Define channel metadata based on your data structure
n_markers = 10
channels = [
    Channel(
        channel_name=columns[i],
        channel_component=['x', 'y', 'z'][i % 3],
        channel_type='POS',
        channel_tracked_point=f'marker{i // 3}',
        channel_units='mm'
    )
    for i in range(len(columns))
]

motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    data=data,
    channels=channels
)
```

### Loading from C3D (requires ezc3d)

```python
import ezc3d
import numpy as np
from motionbids import MotionData, Channel

c3d = ezc3d.c3d("recording.c3d")
points = c3d["data"]["points"]  # (4, n_markers, n_frames)
labels = c3d["parameters"]["POINT"]["LABELS"]["value"]
freq = c3d["parameters"]["POINT"]["RATE"]["value"][0]

# Reshape to (n_frames, n_channels)
data = points[:3, :, :].transpose(2, 1, 0).reshape(-1, len(labels) * 3)

channels = [
    Channel(
        channel_name=f"{label}_{axis}",
        channel_component=axis,
        channel_type="POS",
        channel_tracked_point=label,
        channel_units="mm"
    )
    for label in labels
    for axis in ["x", "y", "z"]
]

motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=freq,
    tracked_points_count=len(labels),
    data=data,
    channels=channels
)
```

### Loading IMU Data

```python
import numpy as np
from motionbids import MotionData, Channel

# Example: 2 IMU sensors with accelerometer + gyroscope
sensors = ["left_wrist", "right_wrist"]
acc_axes = ["x", "y", "z"]
gyro_axes = ["x", "y", "z"]

# Load your IMU data (rows=time, cols=channels)
# Expected column order: sensor1_acc_x, sensor1_acc_y, sensor1_acc_z,
#                        sensor1_gyro_x, ..., sensor2_acc_x, ...
data = np.random.randn(6000, len(sensors) * 6)  # 60s at 100 Hz

channels = []
for sensor in sensors:
    for axis in acc_axes:
        channels.append(Channel(
            channel_name=f"{sensor}_ACCEL_{axis}",
            channel_component=axis,
            channel_type="ACCEL",
            channel_tracked_point=sensor,
            channel_units="m/s^2"
        ))
    for axis in gyro_axes:
        channels.append(Channel(
            channel_name=f"{sensor}_GYRO_{axis}",
            channel_component=axis,
            channel_type="GYRO",
            channel_tracked_point=sensor,
            channel_units="rad/s"
        ))

motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="imu",
    sampling_frequency=100.0,
    tracked_points_count=len(sensors),
    manufacturer="Xsens",
    data=data,
    channels=channels
)
```

### Custom Metadata
```python
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    data=data,
    channels=channels,
    additional_metadata={
        "CaptureVolume": "8m x 6m x 3m",
        "CalibrationDate": "2025-11-01",
        "AmbientTemperature": 22.5
    }
)
```

## Validation

!!! warning "Important"
    The validation provided by this package is for convenience only and is **not officially supported by BIDS**. Always validate your dataset with the official [BIDS Validator](https://bids-standard.github.io/bids-validator/) before sharing or publishing.

### Package Validation (Convenience)

```python
from motionbids import validate_motion_data, ValidationError

try:
    validate_motion_data(motion)
    print("✓ Valid")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
```

### What Gets Validated

#### Required Fields
- ✅ Required fields present (`subject_id`, `task_name`, `tracksys`, etc.)
- ✅ Positive numeric values (`sampling_frequency > 0`)
- ⚠️ Recommended fields present (warnings only)

#### Data Consistency
- ✅ Array dimensions match (`data.shape[1] == len(columns)`)
- ✅ Units match columns (`len(units) == len(columns)`)

#### Channel Information
- ✅ Channel metadata validated against BIDS schema during construction
- ✅ All three channel metadata fields required together: `channel_component`, `channel_type`, `channel_tracked_point`
- ✅ Component values validated: `x`, `y`, `z`, `quat_x`, `quat_y`, `quat_z`, `quat_w`, `n/a`
- ✅ Type values validated (uppercase): `POS`, `ORNT`, `VEL`, `ACCEL`, `GYRO`, `ANGACCEL`, `MAGN`, `JNTANG`, `LATENCY`, `MISC`
- ✅ Component-type compatibility checked (e.g., quaternion components only allowed with `ORNT` type)

#### Channel Export Validation
- ✅ **Required fields check**: On export, channels are validated to have all required BIDS fields (`name`, `component`, `type`, `tracked_point`, `units`). Export will fail with a `ValueError` if any required field is missing.
- ⚠️ **Unknown fields warning**: If a channel contains fields not in the required or optional BIDS specification, a `ValidationWarning` is raised.

!!! info "Channel Metadata Required"
    You **must** provide explicit channel metadata (`channel_component`, `channel_type`, `channel_tracked_point`) when creating a MotionData object with data. These are validated during construction to ensure BIDS compliance. All three fields must be provided together and match the length of your `columns` list.

### Official BIDS Validation

!!! warning "Important"
    After exporting your dataset, **always validate with the official BIDS Validator**:

    - **Web version**: [https://bids-standard.github.io/bids-validator/](https://bids-standard.github.io/bids-validator/)

    The official validator is the authoritative source for BIDS compliance.

## Troubleshooting

### "Missing required field: tracksys"
```python
# ✗ Missing tracksys
motion = MotionData(subject_id="01", task_name="walk", ...)

# ✓ Include tracksys
motion = MotionData(
    subject_id="01", 
    task_name="walk",
    tracksys="optical",  # Required!
    ...
)
```

### "Number of columns must match data dimensions"
```python
# ✗ Mismatch
data = np.random.randn(1000, 30)
columns = ["ch0", "ch1"]  # Only 2 names for 30 columns

# ✓ Match dimensions
columns = [f"ch{i}" for i in range(30)]  # 30 names for 30 columns
```

## Next Steps

- [MotionData Class Reference](class-reference.md) - Detailed class documentation
- [Schema Fields](schema-fields.md) - All available BIDS fields
