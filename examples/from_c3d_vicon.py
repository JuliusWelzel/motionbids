"""
Example: Convert Vicon marker data from a .c3d file to BIDS format

This example demonstrates:
- Loading a Vicon C3D recording with ezc3d
- Reading 3D marker trajectories and the capture frame rate
- Converting marker units from millimetres (C3D default) to metres (BIDS)
- Building consistent BIDS Channel metadata for position (POS) data
- Validating and exporting the recording as BIDS motion files
- Plotting a single marker trajectory to sanity-check the export

Requirements:
    pip install motionbids ezc3d numpy pandas matplotlib

Example data:
    A sample Vicon recording is downloaded automatically into a `data/` folder
    next to this script on first run, from:
    https://github.com/JuliusWelzel/motionbids/blob/main/examples/data/example_vicon.c3d
"""

import urllib.request
from pathlib import Path

import pandas as pd
import ezc3d
from matplotlib import pyplot as plt

from motionbids import (
    MotionData,
    Channel,
    validate_motion_data,
    export_bids_motion,
    create_bids_directory_structure,
    export_dataset_description,
)

# Raw download URL for the bundled example recording
EXAMPLE_DATA_URL = (
    "https://raw.githubusercontent.com/JuliusWelzel/motionbids/main/"
    "examples/data/example_vicon.c3d"
)

# The three spatial axes a Vicon marker is sampled on. Defined once and reused
# everywhere below so the DataFrame columns, the Channel metadata, and the plot
# can never drift apart.
AXES = ("x", "y", "z")

# Configuration
bids_root = Path(__file__).parent / "bids_dataset"
data_folder = Path(__file__).parent / "data"
subject = "ID001"
session = "01"  # Optional: set to None if no sessions
task_name = "calibration"
tracksys = "vicon"


def clean_marker_label(label: str, index: int) -> str:
    """Return a clean, BIDS-friendly marker name.

    Vicon names *unlabeled* trajectories "*0", "*1", ... The leading "*" is an
    awkward character for a BIDS channel label, so those are renamed to
    "marker0", "marker1", ... Real marker labels (e.g. "LASI") are kept as-is,
    minus any stray surrounding whitespace.
    """
    label = label.strip()
    if not label or label.startswith("*"):
        return f"marker{index}"
    return label


def channel_name(marker: str, axis: str) -> str:
    """Build the canonical channel name for a marker/axis pair (e.g. "LASI_x").

    Using a single helper for naming guarantees the DataFrame column, the
    Channel object, and any later lookup (plotting, validation) all agree.
    """
    return f"{marker}_{axis}"


# =========================================================================
# 1) Make sure the example recording is available locally
# =========================================================================
data_folder.mkdir(exist_ok=True)
example_file = data_folder / "example_vicon.c3d"
if example_file.exists():
    print(f"Example data already present: {example_file}")
else:
    print(f"Downloading example data from {EXAMPLE_DATA_URL}")
    urllib.request.urlretrieve(EXAMPLE_DATA_URL, example_file)
    print(f"Saved to {example_file}")


# =========================================================================
# 2) Load the C3D file
# =========================================================================
print("\n1. Loading C3D data")
c3d = ezc3d.c3d(str(example_file))

# Marker positions, shape = (4, n_markers, n_frames):
#   axis 0 -> [X, Y, Z, residual]   (residual is a tracking-quality value)
#   axis 1 -> marker index
#   axis 2 -> frame index
points = c3d["data"]["points"]

# Marker labels (one per marker) and the capture rate in Hz.
# Labels are cleaned so unlabeled Vicon trajectories ("*0", ...) become valid,
# readable channel names ("marker0", ...) and stay consistent everywhere.
raw_marker_labels = c3d["parameters"]["POINT"]["LABELS"]["value"]
marker_labels = [clean_marker_label(label, i) for i, label in enumerate(raw_marker_labels)]
sampling_frequency = c3d["parameters"]["POINT"]["RATE"]["value"][0]
n_frames = points.shape[2]

print(f"   Found {len(marker_labels)} markers, {n_frames} frames at {sampling_frequency:.1f} Hz")


# =========================================================================
# 3) Build the data table and matching channel metadata
# =========================================================================
print("\n2. Building data table and BIDS channel metadata")

# `data` holds one column per marker/axis; `channels` holds the BIDS metadata
# describing each of those columns. They are built together in the same loop so
# every column has exactly one matching Channel, in the same order.
data = {}
channels = []

for i, marker in enumerate(marker_labels):
    # points[axis, marker, :] -> trajectory for one axis of this marker.
    # C3D stores positions in millimetres; BIDS expects metres, so divide by 1000.
    xyz = points[:3, i, :] / 1000.0

    for axis_idx, axis in enumerate(AXES):
        name = channel_name(marker, axis)

        # Column in the data table...
        data[name] = xyz[axis_idx]

        # ...and the BIDS Channel that describes it (POS = position data).
        channels.append(
            Channel(
                channel_name=name,
                channel_component=axis,
                channel_type="POS",
                channel_tracked_point=marker,
                channel_units="m",
            )
        )

df = pd.DataFrame(data)
print(f"   Built {df.shape[1]} channels ({len(marker_labels)} markers x {len(AXES)} axes)")
print(df.head())


# =========================================================================
# 4) Assemble the MotionData object
# =========================================================================
print("\n3. Creating MotionData object")

# Each unique tracked point (marker) counts once, regardless of its 3 axes.
tracked_points_count = len({c.channel_tracked_point for c in channels})

motion = MotionData(
    subject=subject,
    session=session,
    task_name=task_name,
    tracksys=tracksys,
    tracked_points_count=tracked_points_count,
    data=df.to_numpy(),
    sampling_frequency=sampling_frequency,
    channels=channels,
)

# Run the package's internal consistency checks (e.g. data columns vs channels).
validate_motion_data(motion)
print("   Package internal validation passed")


# =========================================================================
# 5) Export to BIDS
# =========================================================================
print(f"\n4. Exporting to BIDS format at {bids_root}")

# Create the sub-/ses-/motion directory tree and the top-level dataset metadata.
motion_dir = create_bids_directory_structure(
    base_dir=bids_root,
    subject=subject,
    session=session,
)

export_dataset_description(
    bids_root=bids_root,
    name="Vicon Motion Dataset",
    authors=["Ilaria D'Ascanio"],
    dataset_type="raw",
    task_description="Static posture, Vicon calibration task",
)

# Write the *_motion.tsv / *_channels.tsv / *_motion.json files.
export_bids_motion(
    data=motion,
    out_dir=motion_dir,
    validate=True,
    overwrite=True,
)
print("   Export completed")


# =========================================================================
# 6) Sanity-check plot: read the exported TSV back and plot one marker
# =========================================================================
print("\n5. Plotting exported data for a quick visual check")

bids_file = (
    motion_dir
    / f"sub-{subject}_ses-{session}_task-{task_name}_tracksys-{tracksys}_motion.tsv"
)

# Reload from disk to confirm the file round-trips correctly.
# IMPORTANT: BIDS motion.tsv files are written WITHOUT a header row (the column
# descriptions live in the companion channels.tsv). So we read with
# `header=None` and re-attach the channel names ourselves, in the same order
# they were exported.
column_names = [c.channel_name for c in channels]
exported = pd.read_csv(bids_file, sep="\t", header=None, names=column_names)

# Plot the first marker so the example works regardless of which markers exist.
# `channel_name` is reused here, so the columns we look up are guaranteed to
# match the ones written above.
marker = marker_labels[0]
plt.figure(figsize=(12, 6))
for axis in AXES:
    name = channel_name(marker, axis)
    plt.plot(exported[name], label=name)

plt.title(f"Marker {marker} trajectory")
plt.xlabel("Frame")
plt.ylabel("Position (m)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
