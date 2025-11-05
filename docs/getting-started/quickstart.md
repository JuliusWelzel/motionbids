# Quick Start

This guide will walk you through creating your first BIDS motion dataset in under 5 minutes.

## Basic Workflow

The typical workflow with motionbids involves three steps:

1. **Create** a `MotionData` object with your data and metadata
2. **Validate** the data for BIDS compliance
3. **Export** to BIDS format

## Your First BIDS Motion Dataset

### Step 1: Import and Prepare Data

```python
import numpy as np
from motionbids import MotionData, validate_motion_data, export_bids_motion

# Example: 10 markers tracked at 120 Hz for 10 seconds
n_timepoints = 1200  # 10 seconds at 120 Hz
n_markers = 10
n_channels = n_markers * 3  # x, y, z for each marker

# Generate or load your motion data
# Format: rows = timepoints, columns = channels
data = np.random.randn(n_timepoints, n_channels) * 10 + 100
```

!!! note "Data Format"
    Motion data arrays should have:
    
    - **Rows**: timepoints (samples)
    - **Columns**: channels (e.g., marker0_x, marker0_y, marker0_z, ...)

### Step 2: Create MotionData Object

```python
motion = MotionData(
    # Required BIDS fields (must always be provided)
    subject_id="01",
    task_name="walk",
    tracksys="optical",  # Tracking system: optical, imu, video, etc.
    sampling_frequency=120.0,  # Hz
    tracked_points_count=10,  # Number of tracked markers/points
    
    # Data arrays
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x', 'y', 'z']],
    units=["mm"] * 30,
    
    # Recommended fields (should be provided when available)
    manufacturer="Vicon",
    recording_type="continuous"
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
    out_dir="my_study/sub-01/ses-01/motion/",
    validate=True,
    overwrite=True
)

print(f"Created files: {list(files.keys())}")
# Output: ['json', 'tsv', 'channels']
```

## Understanding the Output

After export, you'll have these files:

```
my_study/
└── sub-01/
    └── ses-01/
        └── motion/
            ├── sub-01_ses-01_task-walk_tracksys-optical_motion.json
            ├── sub-01_ses-01_task-walk_tracksys-optical_motion.tsv
            └── sub-01_ses-01_task-walk_tracksys-optical_channels.tsv
```

### File Descriptions

| File | Content | Description |
|------|---------|-------------|
| `*_motion.json` | Metadata | Acquisition parameters, equipment info |
| `*_motion.tsv` | Time series | Numeric data only (no headers) |
| `*_channels.tsv` | Channel info | Names, types, tracked points, units |

## Complete Example

Here's a complete working example:

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

# 1. Prepare your data
n_timepoints = 1200
n_markers = 10
data = np.random.randn(n_timepoints, n_markers * 3) * 10 + 100

# 2. Create MotionData object
motion = MotionData(
    # Required fields
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    
    # Recommended fields
    manufacturer="Vicon",
    manufacturers_model_name="Vantage V5",
    software_versions="Nexus 2.12",
    motion_channel_count=30,
    recording_duration=10.0,
    recording_type="continuous",
    
    # Optional entity labels
    session_id="01",
    acquisition="indoor",
    run=1,
    
    # Data
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x', 'y', 'z']],
    units=["mm"] * 30
)

# 3. Validate
validate_motion_data(motion)

# 4. Create BIDS structure
bids_root = Path("my_motion_study")
motion_dir = create_bids_directory_structure(
    base_dir=bids_root,
    subject_id="01",
    session_id="01"
)

# 5. Export dataset description
export_dataset_description(
    bids_root=bids_root,
    name="My Motion Study",
    authors=["Your Name"],
    dataset_type="raw"
)

# 6. Export motion data
files = export_bids_motion(
    data=motion,
    out_dir=motion_dir,
    validate=True,
    overwrite=True
)

print("✓ BIDS dataset created successfully!")
print(f"Location: {bids_root.absolute()}")
```

## Adding Multiple Subjects or Sessions

### Multiple Runs

For multiple runs of the same task:

```python
for run_number in [1, 2, 3]:
    motion = MotionData(
        subject_id="01",
        task_name="walk",
        tracksys="optical",
        run=run_number,  # Increment run number
        sampling_frequency=120.0,
        tracked_points_count=10,
        data=load_run_data(run_number),  # Your data loading function
        columns=columns,
        units=units
    )
    
    export_bids_motion(motion, out_dir=f"study/sub-01/ses-01/motion/")
```

### Multiple Sessions

For multiple sessions:

```python
for session in ["01", "02", "03"]:
    motion = MotionData(
        subject_id="01",
        session_id=session,  # Change session
        task_name="walk",
        tracksys="optical",
        sampling_frequency=120.0,
        tracked_points_count=10,
        data=load_session_data(session),
        columns=columns,
        units=units
    )
    
    motion_dir = create_bids_directory_structure(
        base_dir="study",
        subject_id="01",
        session_id=session
    )
    
    export_bids_motion(motion, out_dir=motion_dir)
```

### Multiple Subjects

For multiple subjects:

```python
for subject in ["01", "02", "03"]:
    motion = MotionData(
        subject_id=subject,  # Change subject
        task_name="walk",
        tracksys="optical",
        sampling_frequency=120.0,
        tracked_points_count=10,
        data=load_subject_data(subject),
        columns=columns,
        units=units
    )
    
    motion_dir = create_bids_directory_structure(
        base_dir="study",
        subject_id=subject,
        session_id="01"
    )
    
    export_bids_motion(motion, out_dir=motion_dir)
```

## Common Patterns

### Loading Data from Files

```python
# Example: Loading from CSV
import pandas as pd

# Load your motion data
df = pd.read_csv("motion_capture_data.csv")
data = df.values  # Convert to NumPy array

# Get column names from CSV
columns = df.columns.tolist()

motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    data=data,
    columns=columns,
    units=["mm"] * len(columns)
)
```

### Adding Acquisition Timestamps

If you have acquisition timestamps, add them to create a `scans.tsv` file:

```python
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    acq_time="2025-11-05T14:30:00.123",  # ISO 8601 format
    data=data,
    columns=columns,
    units=units
)

# This automatically creates a scans.tsv file during export
files = export_bids_motion(motion, out_dir="study/sub-01/ses-01/motion/")
# files will include: ['json', 'tsv', 'channels', 'scans']
```

## Next Steps

Now that you've created your first BIDS motion dataset, learn more about:

- [BIDS Motion Fields](../user-guide/bids-fields.md) - Detailed field reference
- [Exporting to BIDS](../user-guide/exporting.md) - Advanced export options
- [Validation](../user-guide/validation.md) - Understanding validation rules
- [API Reference](../api/motiondata.md) - Complete API documentation

## Troubleshooting

### "sampling_frequency must be positive"

Ensure sampling frequency is a positive number:

```python
sampling_frequency=120.0  # ✓ Good
sampling_frequency=-120.0  # ✗ Bad
```

### "Number of columns must match data dimensions"

Make sure the number of column names equals the number of data columns:

```python
data.shape[1] == len(columns)  # Must be True
```

### "Missing required fields"

Ensure all required fields are provided:

- `subject_id`
- `task_name`
- `tracksys`
- `sampling_frequency`
- `tracked_points_count`

### "tracksys label is not optional"

The `tracksys` field is always required per BIDS specification:

```python
tracksys="optical"  # Must be provided
```
