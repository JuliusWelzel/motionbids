"""
Export utilities for writing BIDS-compliant motion data files.

This module provides functions to export MotionData instances to
BIDS-formatted JSON and TSV files.
"""
import json
from pathlib import Path
from typing import Optional, Union
import warnings

from .datamodel import MotionData
from .validator import validate_motion_data, ValidationWarning


def export_bids_motion(
    data: MotionData,
    out_dir: Union[str, Path],
    validate: bool = True,
    create_dirs: bool = True,
    overwrite: bool = False
) -> dict:
    """
    Export MotionData to BIDS-compliant files.
    
    This function writes:
    1. A JSON sidecar file with metadata
    2. A TSV file with motion time series data (if data is present)
    3. A channels.tsv file (if units are specified)
    4. A scans.tsv file (if acq_time is provided)
    
    Args:
        data: MotionData instance to export
        out_dir: Output directory path
        validate: Whether to validate data before export (default: True)
        create_dirs: Whether to create output directory if it doesn't exist (default: True)
        overwrite: Whether to overwrite existing files (default: False)
    
    Returns:
        Dictionary with paths to created files:
        {
            'json': Path to JSON metadata file,
            'tsv': Path to TSV data file (if data was present),
            'channels': Path to channels.tsv file (if applicable),
            'scans': Path to scans.tsv file (if acq_time was provided)
        }
    
    Raises:
        ValidationError: If validation is enabled and fails
        FileExistsError: If files exist and overwrite=False
        ValueError: If data array is present but columns are not defined
    
    Example:
        >>> motion = MotionData(subject_id="01", task_name="rest", ...)
        >>> files = export_bids_motion(motion, "bids_out/")
        >>> print(files['json'])
        bids_out/sub-01_task-rest_motion.json
    """
    # Validate if requested
    if validate:
        validate_motion_data(data)
    
    # Convert to Path object
    out_dir = Path(out_dir)
    
    # Create output directory if needed
    if create_dirs:
        out_dir.mkdir(parents=True, exist_ok=True)
    elif not out_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {out_dir}")
    
    # Generate BIDS-compliant filenames
    json_filename = data.get_bids_filename(suffix="motion", extension="json")
    tsv_filename = data.get_bids_filename(suffix="motion", extension="tsv")
    channels_filename = data.get_bids_filename(suffix="channels", extension="tsv")
    
    json_path = out_dir / json_filename
    tsv_path = out_dir / tsv_filename
    channels_path = out_dir / channels_filename
    
    # Check for existing files
    if not overwrite:
        if json_path.exists():
            raise FileExistsError(f"File already exists: {json_path}")
        if data.data is not None and tsv_path.exists():
            raise FileExistsError(f"File already exists: {tsv_path}")
    
    created_files = {}
    
    # Export JSON metadata
    json_path = export_json_metadata(data, json_path)
    created_files['json'] = json_path
    
    # Export TSV data if present
    if data.data is not None:
        if data.columns is None:
            raise ValueError(
                "data array is present but columns are not defined. "
                "Please specify column names in the MotionData.columns field."
            )
        
        tsv_path = export_tsv_data(data, tsv_path)
        created_files['tsv'] = tsv_path
        
        # Export channels.tsv if units are specified
        if data.units is not None:
            channels_path = export_channels_tsv(data, channels_path)
            created_files['channels'] = channels_path
    
    # Export scans.tsv if acq_time is provided
    if data.acq_time is not None:
        # scans.tsv goes in the subject (or session) directory, not motion subdirectory
        if data.session_id:
            scans_dir = out_dir.parent  # Go up from motion/ to ses-XX/
            scans_filename = f"sub-{data.subject_id}_ses-{data.session_id}_scans.tsv"
        else:
            scans_dir = out_dir.parent  # Go up from motion/ to sub-XX/
            scans_filename = f"sub-{data.subject_id}_scans.tsv"
        
        scans_path = scans_dir / scans_filename
        scans_path = export_scans_tsv(data, scans_path)
        created_files['scans'] = scans_path
    
    return created_files


def export_json_metadata(data: MotionData, output_path: Union[str, Path]) -> Path:
    """
    Export metadata to a BIDS-compliant JSON file.
    
    Args:
        data: MotionData instance
        output_path: Path where JSON file will be written
    
    Returns:
        Path to the created JSON file
    """
    output_path = Path(output_path)
    
    # Get metadata dictionary
    metadata = data.to_metadata_dict()
    
    # Write JSON with proper formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline (BIDS convention)
    
    return output_path


def export_tsv_data(data: MotionData, output_path: Union[str, Path]) -> Path:
    """
    Export motion time series data to a BIDS-compliant TSV file.
    
    Note: BIDS motion.tsv files should NOT include a header row.
    Column descriptions are provided in the accompanying channels.tsv file.
    
    Args:
        data: MotionData instance with data array
        output_path: Path where TSV file will be written
    
    Returns:
        Path to the created TSV file
    
    Raises:
        ValueError: If data or columns are not defined
    """
    output_path = Path(output_path)
    
    if data.data is None:
        raise ValueError("No data array to export")
    
    if data.columns is None:
        raise ValueError("Column names must be defined to export TSV")
    
    # Import numpy here to avoid requiring it if not using data export
    import numpy as np
    
    # Ensure data is 2D
    if data.data.ndim == 1:
        data_array = data.data.reshape(-1, 1)
    else:
        data_array = data.data
    
    # Write TSV file WITHOUT header (per BIDS specification for motion data)
    np.savetxt(output_path, data_array, delimiter='\t', fmt='%.6f')
    
    return output_path


def export_channels_tsv(data: MotionData, output_path: Union[str, Path]) -> Path:
    """
    Export channel information to a BIDS-compliant channels.tsv file.
    
    This file describes the channels/columns in the main motion data TSV.
    According to BIDS specification for motion data, channels.tsv must include:
    - name: REQUIRED
    - component: REQUIRED (e.g., x, y, z, quat_x, etc.)
    - type: REQUIRED (e.g., POS, ORNT, LATENCY, etc.)
    - tracked_point: REQUIRED (label of the tracked point)
    - units: REQUIRED (e.g., mm, rad, s)
    
    The MotionData instance MUST have channel_component, channel_type, and 
    channel_tracked_point fields provided explicitly.
    
    Args:
        data: MotionData instance with columns, units, and channel metadata defined
        output_path: Path where channels TSV file will be written
    
    Returns:
        Path to the created channels.tsv file
    
    Raises:
        ValueError: If columns, units, or channel metadata are not defined
    """
    output_path = Path(output_path)
    
    if data.columns is None:
        raise ValueError("Column names must be defined to export channels.tsv")
    
    if data.units is None:
        raise ValueError("Units must be defined to export channels.tsv")
    
    # Require explicit channel metadata
    if (data.channel_component is None or 
        data.channel_type is None or 
        data.channel_tracked_point is None):
        raise ValueError(
            "Channel metadata (channel_component, channel_type, channel_tracked_point) "
            "must be explicitly provided to create BIDS-compliant channels.tsv file. "
            "These fields are validated against the BIDS schema during MotionData construction."
        )
    
    # Write channels.tsv with BIDS-required columns
    with open(output_path, 'w', encoding='utf-8') as f:
        # Header - column order is important!
        f.write('name\tcomponent\ttype\ttracked_point\tunits\n')
        
        # Use explicit metadata
        for col_name, component, ch_type, tracked_point, unit in zip(
            data.columns, 
            data.channel_component, 
            data.channel_type, 
            data.channel_tracked_point, 
            data.units
        ):
            f.write(f'{col_name}\t{component}\t{ch_type}\t{tracked_point}\t{unit}\n')
    
    return output_path


def export_scans_tsv(
    data: MotionData,
    output_path: Union[str, Path],
    relative_path: Optional[str] = None
) -> Path:
    """
    Export scans.tsv file for tracking acquisition times.
    
    The scans.tsv file provides metadata about when each file was acquired.
    This is created when acq_time is specified in the MotionData.
    Supports sub-millisecond precision in ISO 8601 format.
    
    Args:
        data: MotionData instance with acq_time field
        output_path: Path where scans.tsv will be written
        relative_path: Optional relative path to the motion file from subject/session directory.
                       If None, it will be auto-generated from the data.
    
    Returns:
        Path to the created scans.tsv file
    
    Reference:
        https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/data-summary-files.html#scans-file
    
    Example:
        >>> motion = MotionData(subject_id="01", task_name="walk", 
        ...                     acq_time="2023-06-15T14:30:00.123456", ...)
        >>> export_scans_tsv(motion, "bids_root/sub-01/sub-01_scans.tsv")
    """
    output_path = Path(output_path)
    
    if data.acq_time is None:
        raise ValueError("acq_time must be defined to export scans.tsv")
    
    # Generate relative path to motion file if not provided
    if relative_path is None:
        # Construct the relative path from the scans.tsv file location
        # The path should be relative to where scans.tsv is stored
        motion_filename = data.get_bids_filename(suffix="motion", extension="json")
        # scans.tsv is always in subject or session directory
        # So the path is always just motion/filename (never includes ses-XX/)
        relative_path = f"motion/{motion_filename}"
    
    # Check if file exists - if so, append; otherwise create with header
    file_exists = output_path.exists()
    
    if file_exists:
        # Read existing file to check if this entry already exists
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
        
        # Check if this filename already exists
        entry_exists = any(relative_path in line for line in existing_lines[1:])  # Skip header
        
        if entry_exists:
            # Update existing entry
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(existing_lines[0])  # Write header
                for line in existing_lines[1:]:
                    if relative_path in line:
                        # Replace with new entry
                        f.write(f'{relative_path}\t{data.acq_time}\n')
                    else:
                        f.write(line)
        else:
            # Append new entry
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(f'{relative_path}\t{data.acq_time}\n')
    else:
        # Create new file with header
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('filename\tacq_time\n')
            f.write(f'{relative_path}\t{data.acq_time}\n')
    
    return output_path


def create_bids_directory_structure(
    base_dir: Union[str, Path],
    subject_id: str,
    session_id: Optional[str] = None
) -> Path:
    """
    Create BIDS-compliant directory structure for motion data.
    
    Creates:
        base_dir/sub-<subject_id>/[ses-<session_id>/]motion/
    
    Args:
        base_dir: Base BIDS directory
        subject_id: Subject identifier
        session_id: Optional session identifier
    
    Returns:
        Path to the motion data directory
    
    Example:
        >>> motion_dir = create_bids_directory_structure("bids_root", "01", "01")
        >>> print(motion_dir)
        bids_root/sub-01/ses-01/motion
    """
    base_dir = Path(base_dir)
    
    # Build directory path
    subject_dir = base_dir / f"sub-{subject_id}"
    
    if session_id:
        motion_dir = subject_dir / f"ses-{session_id}" / "motion"
    else:
        motion_dir = subject_dir / "motion"
    
    # Create directories
    motion_dir.mkdir(parents=True, exist_ok=True)
    
    return motion_dir


def export_dataset_description(
    bids_root: Union[str, Path],
    name: str,
    authors: Optional[list] = None,
    dataset_type: str = "raw",
    bids_version: str = "1.9.0"
) -> Path:
    """
    Create a dataset_description.json file for the BIDS dataset.
    
    This file is required at the root of every BIDS dataset.
    
    Args:
        bids_root: Root directory of the BIDS dataset
        name: Name of the dataset
        authors: List of dataset authors (optional)
        dataset_type: Type of dataset (default: "raw")
        bids_version: BIDS version (default: "1.9.0")
    
    Returns:
        Path to the created dataset_description.json file
    
    Example:
        >>> export_dataset_description(
        ...     "bids_root",
        ...     name="My Motion Study",
        ...     authors=["Jane Doe", "John Smith"]
        ... )
    """
    bids_root = Path(bids_root)
    output_path = bids_root / "dataset_description.json"
    
    description = {
        "Name": name,
        "BIDSVersion": bids_version,
        "DatasetType": dataset_type,
    }
    
    if authors:
        description["Authors"] = authors
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(description, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    return output_path
