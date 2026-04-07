# motionbids

[![PyPI](https://img.shields.io/pypi/v/motionbids.svg)](https://pypi.org/project/motionbids/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/JuliusWelzel/motionbids/actions/workflows/tests.yml/badge.svg)](https://github.com/JuliusWelzel/motionbids/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/JuliusWelzel/motionbids/branch/main/graph/badge.svg)](https://codecov.io/gh/JuliusWelzel/motionbids)

A **lightweight** Python package for exporting motion capture data to **BIDS format**.

## Quick Start

```python
from motionbids import MotionData, Channel, export_bids_motion
import numpy as np

# Your motion data (1200 timepoints, 32 channels)
data = np.random.randn(1200, 32)

# Define channels following BIDS schema
channels = [
    Channel(
        channel_name=f"marker{i}_{axis}",
        channel_component=axis,
        channel_type="POS",
        channel_tracked_point=f"marker{i}",
        channel_units="mm"
    )
    for i in range(10)
    for axis in ['x', 'y', 'z']
]

# Create BIDS motion object
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    manufacturer="Vicon",
    data=data,
    channels=channels
)

# Export to BIDS format
export_bids_motion(motion, out_dir="bids_dataset/")
```

**Output:**
```
bids_dataset/
├── sub-01_task-walk_tracksys-optical_motion.json      # Metadata
├── sub-01_task-walk_tracksys-optical_motion.tsv       # Time series
└── sub-01_task-walk_tracksys-optical_channels.tsv     # Channel info
```

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

## Features

✅ **Schema-driven** - Auto-syncs with BIDS specification  
✅ **Automatic validation** - Catches errors before export  
✅ **Simple API** - Minimal code needed  
✅ **Complete export** - JSON, TSV, channels files  
✅ **Cross-platform** - Tested on Linux, macOS, Windows  

## Documentation

**[Full Documentation](https://juliuswelzel.github.io/motionbids/)**

- [Motivation](https://juliuswelzel.github.io/motionbids/motivation/) - Why BIDS for motion?
- [Workflow](https://juliuswelzel.github.io/motionbids/workflow/) - Complete workflow guide
- [Class Reference](https://juliuswelzel.github.io/motionbids/class-reference/) - MotionData API
- [Schema Fields](https://juliuswelzel.github.io/motionbids/schema-fields/) - All BIDS fields

## Required Fields

```python
motion = MotionData(
    subject_id="01",              # Subject identifier
    task_name="walk",             # Task name
    tracksys="optical",           # Tracking system (optical/imu/video)
    sampling_frequency=120.0,     # Sampling rate in Hz
    tracked_points_count=10,      # Number of markers
    data=data,                    # NumPy array (rows=time, cols=channels)
    channels=channels             # List of Channel objects (BIDS-compliant)
)
```

### Channel Metadata

Each channel requires BIDS-compliant metadata:

```python
from motionbids import Channel

channel = Channel(
    channel_name="marker0_x",           # Channel name
    channel_component="x",              # x, y, z, quat_x, quat_y, quat_z, quat_w, n/a
    channel_type="POS",                 # POS, ORNT, VEL, ACCEL, GYRO, MAGN, etc.
    channel_tracked_point="marker0",    # Label of tracked point
    channel_units="mm"                  # Units (mm, m, rad, deg, etc.)
)
```

## Validation

**Important**: Package validation is for convenience only and is **not officially supported by BIDS**. Always use the official [BIDS Validator](https://bids-standard.github.io/bids-validator/) before sharing your dataset.

```python
from motionbids import validate_motion_data

# Convenience validation (checks basic requirements)
validate_motion_data(motion)

# Then validate with official BIDS Validator:
# https://bids-standard.github.io/bids-validator/
```

## Complete Workflow

```python
from motionbids import (
    MotionData,
    export_bids_motion,
    create_bids_directory_structure,
    export_dataset_description
)

# 1. Create directory structure
motion_dir = create_bids_directory_structure(
    base_dir="my_study",
    subject_id="01",
    session_id="01"
)

# 2. Create dataset description
export_dataset_description(
    bids_root="my_study",
    name="Motion Study",
    authors=["Your Name"]
)

# 3. Export motion data
motion = MotionData(...)
export_bids_motion(motion, out_dir=motion_dir)
```

## Supported Systems

Works with any motion tracking technology:
- **Optical**: Vicon, Optitrack, Qualisys
- **IMU**: Xsens, APDM, Movella  
- **Video**: OpenPose, MediaPipe, DeepLabCut
- **Other**: Custom systems

## Importing Data

`motionbids` focuses on **exporting** to BIDS format. Importing raw data is left
to the user since motion capture systems vary widely. Here are common patterns:

### From CSV / TSV

```python
import pandas as pd
import numpy as np
from motionbids import MotionData, Channel

# Load your data
df = pd.read_csv("recording.csv")
data = df.values

# Map columns to BIDS channels
channels = [
    Channel(
        channel_name=col,
        channel_component=col.split("_")[-1],  # e.g. "x", "y", "z"
        channel_type="POS",
        channel_tracked_point=col.rsplit("_", 1)[0],
        channel_units="mm"
    )
    for col in df.columns
]

motion = MotionData(
    subject_id="01", task_name="walk", tracksys="optical",
    sampling_frequency=120.0, tracked_points_count=10,
    data=data, channels=channels
)
```

### From C3D (requires ezc3d)

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
    subject_id="01", task_name="walk", tracksys="optical",
    sampling_frequency=freq, tracked_points_count=len(labels),
    data=data, channels=channels
)
```

See the [Workflow Guide](https://juliuswelzel.github.io/motionbids/workflow/) for more patterns.

## Development

```bash
git clone https://github.com/juliuswelzel/motionbids.git
cd motionbids
pip install -e ".[dev]"

# Run tests
pytest --cov=motionbids
```

## Citation

```bibtex
@software{motionbids,
  author = {Welzel, Julius},
  title = {motion2bids: BIDS converter for motion capture data},
  year = {2025},
  url = {https://github.com/JuliusWelzel/motionbids}
}
```

## Links

- 📖 [Documentation](https://juliuswelzel.github.io/motionbids/)
- 🐛 [Issues](https://github.com/JuliusWelzel/motionbids/issues)
- 📜 [BIDS Spec](https://bids-specification.readthedocs.io/)

## License

MIT License - see [LICENSE](LICENSE) for details.
