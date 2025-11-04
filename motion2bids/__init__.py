"""
motion2bids: Lightweight converter for motion data to BIDS format.

This package provides tools to define, validate, and export BIDS-compliant
motion capture data.

Example usage:
    >>> from motion2bids import MotionData, validate_motion_data, export_bids_motion
    >>> import numpy as np
    >>> 
    >>> # Create motion data object
    >>> motion = MotionData(
    ...     subject_id="01",
    ...     task_name="rest",
    ...     sampling_frequency=100,
    ...     tracked_points_count=10,
    ...     manufacturer="Vicon",
    ...     data=np.random.randn(1000, 10),
    ...     columns=[f"marker{i}" for i in range(10)],
    ...     units=["mm"] * 10
    ... )
    >>> 
    >>> # Validate
    >>> validate_motion_data(motion)
    True
    >>> 
    >>> # Export to BIDS format
    >>> files = export_bids_motion(motion, out_dir="bids_out/")
    >>> print(files)
    {'json': ..., 'tsv': ..., 'channels': ...}
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main classes and functions
from .datamodel import MotionData
from .validator import (
    validate_motion_data,
    validate_bids_compliance,
    ValidationError,
    ValidationWarning,
    check_required_fields,
    check_recommended_fields,
)
from .exporter import (
    export_bids_motion,
    export_json_metadata,
    export_tsv_data,
    export_channels_tsv,
    export_scans_tsv,
    create_bids_directory_structure,
    export_dataset_description,
)

# Optional: Schema utilities (users typically won't need these directly)
from . import schema_utils

# Define public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Core data model
    "MotionData",
    
    # Validation
    "validate_motion_data",
    "validate_bids_compliance",
    "ValidationError",
    "ValidationWarning",
    "check_required_fields",
    "check_recommended_fields",
    
    # Export functions
    "export_bids_motion",
    "export_json_metadata",
    "export_tsv_data",
    "export_channels_tsv",
    "export_scans_tsv",
    "create_bids_directory_structure",
    "export_dataset_description",
    
    # Schema utilities module (advanced usage)
    "schema_utils",
]
