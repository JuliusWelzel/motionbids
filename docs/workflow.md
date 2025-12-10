# Complete Workflow

This guide demonstrates a full workflow from raw motion data to a BIDS-compliant dataset.

## Installation

> **Note**: This package is not yet published on PyPI. Install from source:

```bash
git clone https://github.com/JuliusWelzel/motionbids.git
cd motionbids

# With uv (recommended)
uv venv  # Create virtual environment first
uv pip install -e .

# Or with pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
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
# Each channel needs: name, component, type, tracked_point, units
channels = [
    Channel(
        name=f"marker{i}_{axis}",
        component=axis,
        type="POS",
        tracked_point=f"marker{i}",
        units="mm"
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
    export_dataset_description
)

# 1. Setup BIDS root directory
bids_root = Path("my_motion_study")

# 2. Create dataset description
export_dataset_description(
    bids_root=bids_root,
    name="Motion Capture Study",
    authors=["Your Name"],
    dataset_type="raw"
)

# 3. Process each subject
for subject_id in ["01", "02", "03"]:
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
        name=columns[i],
        component=['x', 'y', 'z'][i % 3],
        type='POS',
        tracked_point=f'marker{i // 3}',
        units='mm'
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
