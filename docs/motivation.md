# Motivation

## Goal

**Export motion capture data to BIDS format.**

[BIDS (Brain Imaging Data Structure)](https://bids-specification.readthedocs.io/) is a standardized format for organizing scientific data. The BIDS motion extension provides a consistent structure for motion capture datasets.

## Example

```python
from motionbids import MotionData, Channel, export_bids_motion
import numpy as np

# Your motion data (1200 timepoints, 30 channels)
data = np.random.randn(1200, 30)

# Create BIDS motion object
motion = MotionData(
    subject="01",
    task_name="walk",
    tracksys="optical",
    sampling_frequency=120.0,
    tracked_points_count=10,
    manufacturer="Vicon",
    data=data,
    channels=[
        Channel(channel_name=f"marker{i}_{axis}", channel_component=axis, channel_type="POS",
                channel_tracked_point=f"marker{i}", channel_units="mm")
        for i in range(10) for axis in ['x', 'y', 'z']
    ]
)

# Export to BIDS format
export_bids_motion(motion, out_dir="bids_dataset/")
```

**Output:**
```
bids_dataset/
└── sub-01_task-walk_tracksys-optical_motion.json      # Metadata
    sub-01_task-walk_tracksys-optical_motion.tsv       # Time series
    sub-01_task-walk_tracksys-optical_channels.tsv     # Channel info
```

## What It Does

✅ Generates correct BIDS filenames  
✅ Validates required metadata  
✅ Creates JSON/TSV/channels files  
✅ Ensures schema compliance  

Ready to start? See the [Workflow Guide](workflow.md).
