"""
Example: Batch convert Movella DOT IMU data from XDF to BIDS format

This example demonstrates:
- Loading XDF files with multiple streams
- Detecting Movella DOT IMU streams automatically
- Handling zero nominal sample rates (calculate from timestamps)
- Batch processing multiple subjects
- Creating proper BIDS Channel metadata for IMU data (accel + gyro)

Requirements:
    pip install motionbids pyxdf numpy

Example data:
    A sample XDF recording is downloaded automatically into a `data/` folder
    next to this script on first run, from:
    https://github.com/JuliusWelzel/motionbids/blob/main/examples/data/EXAMPLE01.xdf

Real-world tested with:
- 17 subjects, ~60 minute recordings each
- Movella DOT sensors (6 channels: 3 accel + 3 gyro)
- LabStreamingLayer (LSL) XDF format
"""

import urllib.request
import numpy as np
import pyxdf
from pathlib import Path
from motionbids import (
    MotionData,
    Channel,
    export_bids_motion,
    create_bids_directory_structure,
    export_dataset_description,
)

# Raw download URL for the bundled example recording
EXAMPLE_DATA_URL = (
    "https://raw.githubusercontent.com/JuliusWelzel/motionbids/main/"
    "examples/data/example_movella.xdf"
)

# Configuration
base_dir = Path(__file__).parent / "bids_dataset"
data_folder = Path(__file__).parent / "data"
session = "01"  # Optional: set to None if no sessions

# Ensure the example recording is available locally
data_folder.mkdir(exist_ok=True)
example_file = data_folder / "example_movella.xdf"
if example_file.exists():
    print(f"Example data already present: {example_file}")
else:
    print(f"Downloading example data from {EXAMPLE_DATA_URL}")
    urllib.request.urlretrieve(EXAMPLE_DATA_URL, example_file)
    print(f"Saved to {example_file}")

# Get all XDF files
xdf_files = sorted(data_folder.glob("*.xdf"))

# Create base directory and dataset description once
base_dir.mkdir(exist_ok=True)
print(f"\nCreating dataset_description.json")
export_dataset_description(
    bids_root=base_dir,
    name="Gait Study - Movella DOT Sensors",
    authors=["Your Name"],
    dataset_type="raw"
)
print("✓ Dataset description created")

# Process each XDF file
successful = 0
failed = 0

for i, xdf_file in enumerate(xdf_files, 1):
    print(f"\n[{i}/{len(xdf_files)}] Processing {xdf_file.name}")
    try:
        # Extract subject ID from filename (use full filename stem as subject ID)
        subject = xdf_file.stem.replace("_", "")  # Replace spaces with underscores if any

        # Step 1: Create BIDS directory structure
        # Passing session creates a ses-<label> level; passing None keeps files
        # directly under the subject. Either way it stays consistent with the
        # filenames generated below.
        print(f"\n1. Creating BIDS directory structure for sub-{subject}")
        motion_dir = create_bids_directory_structure(
            base_dir=base_dir,
            subject=subject,
            session=session
        )
        print(f"   Created: {motion_dir}")

        # Step 2: Load XDF data (CRITICAL: Follow this exact sequence!)
        print("\n2. Loading XDF data")
        streams, header = pyxdf.load_xdf(str(xdf_file))

        print(f"   Found {len(streams)} streams:")
        for idx, stream in enumerate(streams):
            stream_name = stream['info']['name'][0]
            stream_type = stream['info']['type'][0]
            n_channels = int(stream['info']['channel_count'][0])
            print(f"   [{idx}] {stream_name} ({stream_type}): {n_channels} channels")

        # Step 3: Detect IMU stream (look for Movella DOT)
        imu_stream = None
        for stream in streams:
            if 'misc' in stream['info']['type'][0]:
                imu_stream = stream
                break

        if imu_stream is None:
            print("   ✗ Error: No Movella stream found!")
            failed += 1
            continue

        print(f"   ✓ Found: {imu_stream['info']['name'][0]}")

        # Step 4: Load data with CORRECT sequence (critical!)
        # DO NOT convert to numpy array yet - keep as-is for timestamp processing
        raw_data = imu_stream['time_series']
        timestamps = imu_stream['time_stamps']

        # Calculate actual sampling rate from timestamps
        # (Movella DOT reports nominal_srate = 0.0 in XDF metadata)
        sampling_rate = len(timestamps) / (timestamps[-1] - timestamps[0])

        # NOW convert to numpy
        raw_data = np.array(raw_data)

        duration_min = (timestamps[-1] - timestamps[0]) / 60
        print(f"   ✓ Loaded: {raw_data.shape[0]} samples at {sampling_rate:.2f} Hz ({duration_min:.1f} min)")

        # Step 5: Prepare motion data for BIDS export
        print("\n3. Preparing BIDS metadata")

        # Movella DOT format: [acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z]
        acc_data = raw_data[:, :3]   # First 3 channels
        gyro_data = raw_data[:, 3:6] if raw_data.shape[1] >= 6 else None

        # Analyze gravity to understand sensor orientation
        acc_mean = np.mean(acc_data, axis=0)
        vertical_axis_idx = np.argmax(np.abs(acc_mean))
        vertical_axis = ['X', 'Y', 'Z'][vertical_axis_idx]
        print(f"   Gravity detected on {vertical_axis}-axis: {acc_mean[vertical_axis_idx]:.3f} m/s²")

        # Create BIDS Channel objects
        tracked_point = "LowerBack"  # Adjust based on your sensor placement
        channels = []

        # Accelerometer channels
        for axis in ['x', 'y', 'z']:
            channels.append(Channel(
                channel_name=f"acc_{axis}",
                channel_component=axis,
                channel_type="ACCEL",
                channel_tracked_point=tracked_point,
                channel_units="m/s^2"
            ))

        # Gyroscope channels (if available)
        if gyro_data is not None:
            for axis in ['x', 'y', 'z']:
                channels.append(Channel(
                    channel_name=f"gyro_{axis}",
                    channel_component=axis,
                    channel_type="GYRO",
                    channel_tracked_point=tracked_point,
                    channel_units="rad/s"
                ))

            motion_data = np.hstack([acc_data, gyro_data])
            print(f"   Combined data: {motion_data.shape} (3 accel + 3 gyro)")
        else:
            motion_data = acc_data
            print(f"   Data: {motion_data.shape} (accel only)")

        # Create MotionData object
        motion = MotionData(
            subject=subject,
            session=session,  # Drives both the ses-<label> dir and the filename
            task_name="walking",
            tracksys="imu",
            sampling_frequency=sampling_rate,
            tracked_points_count=1,
            data=motion_data,
            channels=channels,
            manufacturer="Movella",
            manufacturers_model_name="DOT",
            recording_type="continuous"
        )

        # Step 6: Export to BIDS format
        print("\n4. Exporting to BIDS format")
        export_bids_motion(motion, out_dir=motion_dir)
        # validate export
        print(f"   ✓ Exported successfully")
        successful += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

# Summary
print("CONVERSION COMPLETE")
print(f"\nSuccessful: {successful} files")
print(f"Failed: {failed} files")
print(f"\nBIDS dataset: {base_dir.absolute()}/")
