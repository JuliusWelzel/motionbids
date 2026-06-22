"""
motionbids: Lightweight converter for motion data to BIDS format.

This package provides tools to define, validate, and export BIDS-compliant
motion capture data.

Example usage:
    >>> from motionbids import MotionData, Channel, validate_motion_data, export_bids_motion
    >>> import numpy as np
    >>>
    >>> data = np.random.randn(1000, 3)
    >>> channels = [
    ...     Channel(channel_name=f"marker0_{axis}", channel_component=axis,
    ...             channel_type="POS", channel_tracked_point="marker0",
    ...             channel_units="mm")
    ...     for axis in ["x", "y", "z"]
    ... ]
    >>> motion = MotionData(
    ...     subject="01",
    ...     task_name="rest",
    ...     tracksys="optical",
    ...     sampling_frequency=100,
    ...     tracked_points_count=1,
    ...     manufacturer="Vicon",
    ...     data=data,
    ...     channels=channels,
    ... )
    >>> validate_motion_data(motion)
    True
    >>> files = export_bids_motion(motion, out_dir="bids_out/")
"""

__version__ = "0.4.0"
__author__ = "Julius Welzel"
__email__ = "julius.welzel@gmail.com"

# Import main classes and functions
from .channel import Channel
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
    export_participants_tsv,
)

# Optional: Schema utilities (users typically won't need these directly)
from . import schema_utils


def __getattr__(name: str):
    # ``MotionData`` is built dynamically from the BIDS schema; defer that
    # work until the class is actually requested so callers that only need
    # the export helpers don't pay the schema-parse cost on ``import``.
    if name == "MotionData":
        from .datamodel_dynamic import MotionData as _MotionData
        return _MotionData
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# Define public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Core data model
    "MotionData",
    "Channel",
    
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
    "export_participants_tsv",
    
    # Schema utilities module (advanced usage)
    "schema_utils",
]
