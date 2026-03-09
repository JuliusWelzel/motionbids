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
from .datautils import _is_pascal_case
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
        if data.channels is None or len(data.channels) == 0:
            raise ValueError(
                "data array is present but channels are not defined. "
                "Please specify channels in the MotionData.channels field."
            )
        
        tsv_path = export_tsv_data(data, tsv_path)
        created_files['tsv'] = tsv_path
        
        # Export channels.tsv (always create it if we have channels)
        if data.channels is not None and len(data.channels) > 0:
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
        ValueError: If data is not defined
    """
    output_path = Path(output_path)
    
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
    
    And optionally:
    - placement, reference_frame, description, sampling_frequency, status, status_description
    
    The MotionData instance MUST have a channels list with Channel objects.
    
    Args:
        data: MotionData instance with channels defined
        output_path: Path where channels TSV file will be written
    
    Returns:
        Path to the created channels.tsv file
    
    Raises:
        ValueError: If channels list is empty
    """
    output_path = Path(output_path)
    
    if not data.channels:
        raise ValueError("Channels list must be defined to export channels.tsv")
    
    # Define required and optional fields
    required_fields = ['name', 'component', 'type', 'tracked_point', 'units']
    optional_fields = ['placement', 'reference_frame', 'description', 
                      'sampling_frequency', 'status', 'status_description']
    all_known_fields = set(required_fields + optional_fields)
    
    # Validate channels before writing
    for i, channel in enumerate(data.channels):
        row_dict = channel.to_tsv_row()
        
        # Check if all required fields are present
        missing_required = [f for f in required_fields if f not in row_dict or row_dict[f] is None]
        if missing_required:
            raise ValueError(
                f"Channel {i} is missing required fields: {missing_required}. "
                f"All channels.tsv files MUST have: {required_fields}"
            )
        
        # Warn about unknown fields
        unknown_fields = [f for f in row_dict.keys() if f not in all_known_fields]
        if unknown_fields:
            warnings.warn(
                f"Channel {i} contains unknown fields: {unknown_fields}. "
                f"These fields are not in the required ({required_fields}) or "
                f"optional ({optional_fields}) BIDS fields.",
                ValidationWarning
            )
    
    # Write channels.tsv with BIDS-required columns
    with open(output_path, 'w', encoding='utf-8') as f:
        # Start with required fields
        fields = required_fields.copy()
        
        # Check if any channel has optional fields using Channel.to_tsv_row()
        for field in optional_fields:
            if any(field in ch.to_tsv_row() for ch in data.channels):
                fields.append(field)
        
        # Write header
        f.write('\t'.join(fields) + '\n')
        
        # Write each channel as a row using Channel.to_tsv_row()
        for channel in data.channels:
            row_dict = channel.to_tsv_row()
            row_values = []
            for field in fields:
                value = row_dict.get(field)
                # Convert None to 'n/a' for TSV
                row_values.append(str(value) if value is not None else 'n/a')
            f.write('\t'.join(row_values) + '\n')
    
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


def _parse_channel_name(channel_name: str) -> tuple[str, str, str]:
    """
    Parse a channel name to extract component, tracked_point, and type.

    This is a best-effort parser used when explicit channel metadata is not
    provided. It supports common naming patterns such as:
    - marker0_x, point1_y -> position components
    - marker0_quat_w -> quaternion orientation
    - sensor1_roll -> Euler angles
    - marker0_vx, marker0_ax -> velocity/acceleration

    Returns (component, tracked_point, channel_type).
    """
    # Default values
    component = "n/a"
    tracked_point = channel_name
    channel_type = "POS"

    parts = channel_name.split('_')

    if len(parts) >= 2:
        last_part = parts[-1].lower()

        # Position axes
        if last_part in ['x', 'y', 'z']:
            component = last_part
            channel_type = "POS"
            tracked_point = '_'.join(parts[:-1])

        # Quaternion components (e.g., quat_w)
        elif len(parts) >= 2 and parts[-2].lower() == 'quat' and last_part in ['x', 'y', 'z', 'w']:
            component = f"quat_{last_part}"
            channel_type = "ORNT"
            tracked_point = '_'.join(parts[:-2])

        # Euler angles (roll/pitch/yaw)
        elif last_part in ['roll', 'pitch', 'yaw']:
            component = last_part
            channel_type = "ORNT"
            tracked_point = '_'.join(parts[:-1])

        # Velocity (vx, vy, vz) -> component 'vx' etc.
        elif len(last_part) == 2 and last_part[0] == 'v' and last_part[1] in ['x', 'y', 'z']:
            component = last_part
            channel_type = "VEL"
            tracked_point = '_'.join(parts[:-1])

        # Acceleration (ax, ay, az)
        elif len(last_part) == 2 and last_part[0] == 'a' and last_part[1] in ['x', 'y', 'z']:
            component = last_part
            channel_type = "ACCEL"
            tracked_point = '_'.join(parts[:-1])

        # Gyroscope (gx, gy, gz)
        elif len(last_part) == 2 and last_part[0] == 'g' and last_part[1] in ['x', 'y', 'z']:
            component = last_part
            channel_type = "GYRO"
            tracked_point = '_'.join(parts[:-1])

        # Magnetometer (mx, my, mz)
        elif len(last_part) == 2 and last_part[0] == 'm' and last_part[1] in ['x', 'y', 'z']:
            component = last_part
            channel_type = "MAGN"
            tracked_point = '_'.join(parts[:-1])

    return component, tracked_point, channel_type

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
    bids_version: str = "1.9.0",
    authors: Optional[list] = None,
    **kwargs
) -> Path:
    """
    Create a dataset_description.json file for the BIDS dataset.
    
    This file is required at the root of every BIDS dataset.
    
    Args:
        bids_root: Root directory of the BIDS dataset
        name: Name of the dataset
        bids_version: BIDS version (default: "1.9.0")
        authors: List of dataset authors (optional)
        **kwargs: Additional fields to include in the dataset description
                  (e.g., License, Acknowledgements, HowToAcknowledge,
                  Funding, EthicsApprovals, ReferencesAndLinks, DatasetDOI)
    
    Returns:
        Path to the created dataset_description.json file
    
    Example:
        >>> export_dataset_description(
        ...     "bids_root",
        ...     name="My Motion Study",
        ...     authors=["Jane Doe", "John Smith"],
        ...     License="CC0",
        ...     Acknowledgements="Thanks to our participants"
        ... )
    """
    bids_root = Path(bids_root)
    output_path = bids_root / "dataset_description.json"
    
    # Check if kwargs keys are in PascalCase and warn if not
    for key in kwargs.keys():
        if not _is_pascal_case(key):
            warnings.warn(
                f"Key '{key}' in dataset_description is not in PascalCase. "
                f"BIDS recommends PascalCase for metadata keys (e.g., 'License', 'Funding').",
                UserWarning
            )
    
    description = {
        "Name": name,
        "BIDSVersion": bids_version,
    }
    
    if authors:
        description["Authors"] = authors
    
    # Add any additional fields from kwargs
    for key, value in kwargs.items():
        if value is not None:
            description[key] = value
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(description, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    return output_path


def export_participants_tsv(
    bids_root: Union[str, Path],
    participant_id: str,
    age: Optional[str] = None,
    sex: Optional[str] = None,
    handedness: Optional[str] = None,
    **kwargs
) -> Path:
    """
    Export or update a participants.tsv file in the BIDS dataset root.

    If participants.tsv already exists, the participant entry is appended
    or updated (matched by participant_id). If the file does not exist, it
    is created with a header row.

    The ``participant_id`` value is stored in the ``participant_id`` column
    and is automatically prefixed with ``sub-`` if not already present.

    Args:
        bids_root: Root directory of the BIDS dataset
        participant_id: Subject identifier (e.g., "01" or "sub-01")
        age: Age of the participant (string, e.g., "25" or "25-30")
        sex: Sex of the participant ("M", "F", or "O")
        handedness: Handedness ("L", "R", "A" for ambidextrous)
        **kwargs: Additional columns to include (e.g., group="control")

    Returns:
        Path to the created/updated participants.tsv file

    Reference:
        https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/participant-key-records.html

    Example:
        >>> export_participants_tsv(
        ...     "bids_root", participant_id="01",
        ...     age="25", sex="F", handedness="R", group="control"
        ... )
    """
    bids_root = Path(bids_root)
    output_path = bids_root / "participants.tsv"

    # Normalise participant_id to include "sub-" prefix
    if not participant_id.startswith("sub-"):
        participant_id = f"sub-{participant_id}"

    # Build the ordered set of columns.
    # "participant_id" is always first (BIDS requirement).
    base_columns = ["participant_id"]
    base_values: dict[str, str] = {"participant_id": participant_id}

    for col, val in [("age", age), ("sex", sex), ("handedness", handedness)]:
        if val is not None:
            base_columns.append(col)
            base_values[col] = val

    for col, val in kwargs.items():
        if val is not None:
            base_columns.append(col)
            base_values[col] = str(val)

    file_exists = output_path.exists()

    if file_exists:
        warnings.warn(
            f"participants.tsv already exists at '{output_path}'. "
            "Existing entries for other participants will be preserved; "
            "an entry for this participant will be added or updated.",
            UserWarning,
        )

        with open(output_path, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()

        # Parse existing header
        header_cols = existing_lines[0].strip().split("\t")

        # Merge any new columns that don't already exist
        for col in base_columns:
            if col not in header_cols:
                header_cols.append(col)

        # Rebuild rows as list-of-dicts
        rows: list[dict[str, str]] = []
        entry_found = False
        for line in existing_lines[1:]:
            if not line.strip():
                continue
            parts = line.strip().split("\t")
            row = {header_cols[i]: (parts[i] if i < len(parts) else "n/a")
                   for i in range(len(header_cols))}
            if row.get("participant_id") == participant_id:
                # Update existing entry
                for col in base_columns:
                    row[col] = base_values.get(col, "n/a")
                entry_found = True
            rows.append(row)

        if not entry_found:
            new_row = {col: "n/a" for col in header_cols}
            new_row.update(base_values)
            rows.append(new_row)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\t".join(header_cols) + "\n")
            for row in rows:
                f.write("\t".join(row.get(col, "n/a") for col in header_cols) + "\n")
    else:
        bids_root.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\t".join(base_columns) + "\n")
            f.write("\t".join(base_values.get(col, "n/a") for col in base_columns) + "\n")

    return output_path
