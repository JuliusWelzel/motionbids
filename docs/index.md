# motionbids

A lightweight Python package for creating **BIDS-compliant motion capture data**.

## Quick Start

```python
from motionbids import MotionData, export_bids_motion
import numpy as np

# Your motion data (rows=timepoints, columns=channels)
data = np.random.randn(1200, 30)

# Create BIDS motion object
motion = MotionData(
    subject_id="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    data=data,
    columns=[f"marker{i}_{axis}" for i in range(10) for axis in ['x','y','z']],
    units=["mm"] * 30
)

# Export to BIDS format
export_bids_motion(motion, out_dir="bids_dataset/")
```

## Installation

!!! note "Not on PyPI"
    This package is not yet published on PyPI. Install from source:

```bash
git clone https://github.com/JuliusWelzel/motionbids.git
cd motionbids
uv pip install -e .
```

## Features

✅ **Schema-driven** - Auto-syncs with BIDS specification  
✅ **Convenience validation** - Basic checks (use [official BIDS Validator](https://bids-standard.github.io/bids-validator/) for compliance)  
✅ **Simple API** - Create BIDS datasets with minimal code  
✅ **Complete export** - JSON metadata, TSV data, channels, scans files  
✅ **Lightweight** - Minimal dependencies  

## Supported Systems

Works with any motion tracking technology:

- **Optical**: Vicon, Optitrack, Qualisys
- **IMU**: Xsens, APDM, Movella
- **Video**: OpenPose, MediaPipe, DeepLabCut
- **Other**: Custom tracking systems

## Output Structure

```
your-study/
├── dataset_description.json
└── sub-01/
    ├── sub-01_ses-01_scans.tsv
    └── ses-01/
        └── motion/
            ├── *_motion.json      # Metadata
            ├── *_motion.tsv       # Time series
            └── *_channels.tsv     # Channel info
```

## Documentation

<div class="grid cards" markdown>

-   :material-lightbulb:{ .lg .middle } **Motivation**

    ---

    Why BIDS for motion data?

    [:octicons-arrow-right-24: Read more](motivation.md)

-   :material-play-circle:{ .lg .middle } **Workflow**

    ---

    Complete workflow from data to BIDS

    [:octicons-arrow-right-24: Start here](workflow.md)

-   :material-code-braces:{ .lg .middle } **Class Reference**

    ---

    MotionData class and BIDS relations

    [:octicons-arrow-right-24: API docs](class-reference.md)

-   :material-format-list-bulleted:{ .lg .middle } **Schema Fields**

    ---

    All BIDS motion fields explained

    [:octicons-arrow-right-24: Field reference](schema-fields.md)

</div>

## Citation

```bibtex
@software{welzel2025motionbids,
  title = {motionbids: BIDS-compliant motion capture data converter},
  author = {Welzel, Julius},
  year = {2025},
  url = {https://github.com/JuliusWelzel/motionbids}
}
```

## Links

- 📖 [Full Documentation](https://juliuswelzel.github.io/motionbids/)
- 🐛 [Issue Tracker](https://github.com/JuliusWelzel/motionbids/issues)
- 💬 [Discussions](https://github.com/JuliusWelzel/motionbids/discussions)
- 📜 [BIDS Specification](https://bids-specification.readthedocs.io/)

---

**License**: MIT | **Python**: 3.8+ | **Dependencies**: NumPy, bidsschematools, dataclasses-json
