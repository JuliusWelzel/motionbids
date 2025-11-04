"""
Example usage of motion2bids package.

This script demonstrates how to:
1. Create a MotionData object
2. Validate it
3. Export to BIDS format
"""
import numpy as np
from pathlib import Path
from motion2bids import (
    MotionData,
    validate_motion_data,
    export_bids_motion,
    create_bids_directory_structure,
    export_dataset_description
)


def main():
    print("=" * 60)
    print("motion2bids Example")
    print("=" * 60)
    
    # 1. Create sample motion data
    print("\n1. Creating sample motion data...")
    
    # Simulate 10 markers with x, y, z coordinates (30 channels total)
    n_markers = 10
    n_timepoints = 1200  # 10 seconds at 120 Hz
    n_channels = n_markers * 3  # x, y, z for each marker
    sampling_freq = 120.0
    
    # Generate random motion data
    # IMPORTANT: Data format is rows=timepoints, columns=channels
    data = np.random.randn(n_timepoints, n_channels) * 10 + 100  # Random positions
    
    print(f"   ✓ Data shape: {data.shape} (rows=timepoints, columns=channels)")
    print(f"   ✓ Timepoints: {n_timepoints}, Channels: {n_channels}")
    
    # Create column names: marker0_x, marker0_y, marker0_z, marker1_x, ...
    # These will define the structure of the channels.tsv file
    columns = []
    for i in range(n_markers):
        columns.extend([f"marker{i}_x", f"marker{i}_y", f"marker{i}_z"])
    
    print(f"   ✓ Column names (first 5): {columns[:5]}")
    
    # All in millimeters - must match the number of columns
    units = ["mm"] * n_channels
    
    print(f"   ✓ Units: {len(units)} entries (must match {n_channels} columns)")
    
    motion = MotionData(
        subject_id="01",
        session_id="01",
        task_name="walk",
        acquisition="indoor",
        run=1,
        tracksys="optical",
        sampling_frequency=sampling_freq,
        tracked_points_count=n_markers,
        manufacturer="Vicon",
        manufacturers_model_name="Vantage V5",
        software_versions="Nexus 2.12",
        motion_channel_count=n_channels,
        recording_duration=n_timepoints / sampling_freq,
        recording_type="continuous",
        data=data,          # rows=timepoints, columns=channels
        columns=columns,    # Must match data.shape[1]
        units=units,        # Must match len(columns)
        additional_metadata={
            "CaptureVolume": "8m x 6m x 3m",
            "CalibrationDate": "2025-11-01"
        }
    )
    
    print(f"   ✓ Created MotionData with {n_timepoints} timepoints and {n_markers} markers")
    print(f"   ✓ Sampling frequency: {sampling_freq} Hz")
    print(f"   ✓ Duration: {motion.recording_duration:.2f} seconds")
    
    # 2. Validate the data
    print("\n2. Validating motion data...")
    try:
        validate_motion_data(motion)
        print("   ✓ Validation passed!")
    except Exception as e:
        print(f"   ✗ Validation failed: {e}")
        return
    
    # 3. Create BIDS directory structure
    print("\n3. Creating BIDS directory structure...")
    bids_root = Path("example_bids_dataset")
    
    motion_dir = create_bids_directory_structure(
        base_dir=bids_root,
        subject_id="01",
        session_id="01"
    )
    print(f"   ✓ Created directory: {motion_dir}")
    
    # 4. Export dataset description
    print("\n4. Creating dataset_description.json...")
    desc_path = export_dataset_description(
        bids_root=bids_root,
        name="Example Motion Capture Study",
        authors=["Jane Doe", "John Smith"],
        dataset_type="raw"
    )
    print(f"   ✓ Created: {desc_path}")
    
    # 5. Export motion data to BIDS format
    print("\n5. Exporting motion data to BIDS format...")
    files = export_bids_motion(
        data=motion,
        out_dir=motion_dir,
        validate=True,
        create_dirs=True,
        overwrite=True
    )
    
    print("   ✓ Created files:")
    for file_type, file_path in files.items():
        print(f"      - {file_type}: {file_path.name}")
    
    # 6. Show BIDS filename
    print("\n6. BIDS filename convention:")
    print(f"   {motion.get_bids_filename()}")
    
    # 7. Display metadata summary
    print("\n7. Metadata summary:")
    metadata = motion.to_metadata_dict()
    for key in ["TaskName", "SamplingFrequency", "Manufacturer", "TrackedPointsCount"]:
        if key in metadata:
            print(f"   {key}: {metadata[key]}")
    
    print("\n8. Data format information:")
    print(f"   Data shape: {motion.data.shape}")
    print(f"   └─ rows (timepoints): {motion.data.shape[0]}")
    print(f"   └─ columns (channels): {motion.data.shape[1]}")
    print(f"   Columns defined: {len(motion.columns)}")
    print(f"   Units defined: {len(motion.units)}")
    print(f"   ✓ All dimensions match - channels.tsv will have {len(motion.columns)} rows")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print(f"Output directory: {bids_root.absolute()}")
    print("=" * 60)
    
    # Print file structure
    print("\nCreated BIDS structure:")
    print(f"{bids_root}/")
    print(f"├── dataset_description.json")
    print(f"└── sub-01/")
    print(f"    └── ses-01/")
    print(f"        └── motion/")
    for file_path in files.values():
        print(f"            ├── {file_path.name}")
    print()


if __name__ == "__main__":
    main()
