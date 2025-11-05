# motionbids

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/JuliusWelzel/motionbids/actions/workflows/tests.yml/badge.svg)](https://github.com/JuliusWelzel/motionbids/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/JuliusWelzel/motionbids/branch/main/graph/badge.svg)](https://codecov.io/gh/JuliusWelzel/motionbids)

A **lightweight** Python package for exporting motion capture data to **BIDS format**.

## Quick Start

```python
from motionbids import MotionData, export_bids_motion
import numpy as np

# Your motion data (1200 timepoints, 30 channels)
data = np.random.randn(1200, 30)

# Create BIDS motion object
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    manufacturer="Vicon",
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x','y','z']],
    units=["mm"] * 30
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

**📦 Not on PyPI**: This package is not yet published on PyPI. Install from source:

```bash
# Clone the repository
git clone https://github.com/JuliusWelzel/motionbids.git
cd motionbids

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Features

✅ **Schema-driven** - Auto-syncs with BIDS specification  
✅ **Automatic validation** - Catches errors before export  
✅ **Simple API** - Minimal code needed  
✅ **Complete export** - JSON, TSV, channels files  
✅ **Cross-platform** - Tested on Linux, macOS, Windows  

## Documentation

📖 **[Full Documentation](https://juliuswelzel.github.io/motionbids/)**

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
    columns=columns,              # Channel names
    units=units                   # Units per channel
)
```

## Validation

**⚠️ Important**: Package validation is for convenience only and is **not officially supported by BIDS**. Always use the official [BIDS Validator](https://bids-standard.github.io/bids-validator/) before sharing your dataset.

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

## Development

```bash
# Clone and install
git clone https://github.com/juliuswelzel/motionbids.git
cd motionbids
uv pip install -e ".[dev]"

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
