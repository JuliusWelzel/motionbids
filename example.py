"""
Example usage of motionbids package.

Demonstrates BIDS-compliant motion data export following the specification at:
https://bids-specification.readthedocs.io/en/stable/modality-specific-files/motion.html
"""
import numpy as np
from pathlib import Path
from motionbids import (
    MotionData,
    validate_motion_data,
    export_bids_motion,
    create_bids_directory_structure,
    export_dataset_description
)


def main():    
    # =========================================================================
    # 1. Prepare motion capture data
    # =========================================================================
    # Simulate 10 tracked points with x, y, z coordinates (30 channels)
    n_markers = 10
    n_timepoints = 1200  # 10 seconds at 120 Hz
    n_channels = n_markers * 3
    sampling_freq = 120.0
    
    # Generate sample data (rows=timepoints, columns=channels)
    data = np.random.randn(n_timepoints, n_channels) * 10 + 100
    
    # Define channel names and units
    columns = [f"marker{i}_{axis}" for i in range(n_markers) for axis in ['x', 'y', 'z']]
    units = ["mm"] * n_channels
    # Define channel names and units
    columns = [f"marker{i}_{axis}" for i in range(n_markers) for axis in ['x', 'y', 'z']]
    units = ["mm"] * n_channels
    
    # =========================================================================
    # 2. Create BIDS-compliant MotionData object
    # =========================================================================
    
    motion = MotionData(
        # Required BIDS fields
        subject_id="01",
        task_name="walk",
        tracksys="optical",
        sampling_frequency=sampling_freq,
        tracked_points_count=n_markers,
        
        # Recommended fields
        manufacturer="Vicon",
        manufacturers_model_name="Vantage V5",
        software_versions="Nexus 2.12",
        motion_channel_count=n_channels,
        recording_duration=n_timepoints / sampling_freq,
        recording_type="continuous",
        
        # Optional BIDS entities
        session_id="01",
        acquisition="indoor",
        run=1,
        acq_time="2025-11-04T14:30:00",  # Triggers scans.tsv creation
        
        # Data arrays
        data=data,
        columns=columns,
        units=units,
        
        # Additional metadata (optional)
        additional_metadata={
            "CaptureVolume": "8m x 6m x 3m",
            "CalibrationDate": "2025-11-01"
        }
    )
    
    # =========================================================================
    # 3. Validate BIDS compliance
    # =========================================================================
    validate_motion_data(motion)
    print("  ✓ Passed")
    
    # =========================================================================
    # 4. Export to BIDS format
    # =========================================================================
    print("\nExporting to BIDS format...")
    
    bids_root = Path("example_bids_dataset")
    
    # Create directory structure
    motion_dir = create_bids_directory_structure(
        base_dir=bids_root,
        subject_id="01",
        session_id="01"
    )
    
    # Export dataset description
    export_dataset_description(
        bids_root=bids_root,
        name="Example Motion Capture Study",
        authors=["Jane Doe", "John Smith"],
        dataset_type="raw"
    )
    
    # Export motion data files
    files = export_bids_motion(
        data=motion,
        out_dir=motion_dir,
        validate=True,
        overwrite=True
    )
    
    # =========================================================================
    # 5. Summary
    # =========================================================================
    print("\nBIDS filename:")
    print(f"  {motion.get_bids_filename()}")
    
    print("\nExported files:")
    print(f"  dataset_description.json")
    if 'scans' in files:
        print(f"  sub-01/sub-01_ses-01_scans.tsv")
    print(f"  sub-01/ses-01/motion/")
    for file_type in ['json', 'tsv', 'channels']:
        if file_type in files:
            print(f"    └─ {files[file_type].name}")
    
    print("\nKey metadata:")
    metadata = motion.to_metadata_dict()
    for key in ["TaskName", "SamplingFrequency", "TrackedPointsCount", "TrackingSystem"]:
        if key in metadata:
            print(f"  {key}: {metadata[key]}")
    
    print(f"\n✓ Successfully created BIDS dataset at: {bids_root.absolute()}")
    print("-" * 60)


if __name__ == "__main__":
    main()
