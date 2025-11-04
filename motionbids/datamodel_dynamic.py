"""
Dynamic datamodel generation from BIDS schema.

This module generates the MotionData dataclass dynamically from the BIDS schema
using bidsschematools, ensuring automatic synchronization with BIDS updates.
"""
from dataclasses import dataclass, field, fields as dataclass_fields
from typing import Optional, List, Dict, Any
import numpy as np
from dataclasses_json import dataclass_json

from .schema_utils import (
    get_motion_metadata_fields,
    get_required_fields,
    get_recommended_fields,
    get_motion_entities,
)


def _snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())
    return ''.join(result)


def _get_python_type(schema_type: str, schema_format: Optional[str] = None) -> type:
    """
    Convert BIDS schema type to Python type.
    
    Args:
        schema_type: BIDS schema type (e.g., 'string', 'number', 'integer', 'array')
        schema_format: Optional format specifier
    
    Returns:
        Python type
    """
    type_mapping = {
        'string': str,
        'number': float,
        'integer': int,
        'boolean': bool,
        'array': List[str],  # Default to List[str], can be specialized
    }
    
    return type_mapping.get(schema_type, str)


def _create_motion_data_class():
    """
    Dynamically create MotionData dataclass from BIDS schema.
    
    Returns:
        Dynamically generated MotionData class
    """
    # Get schema information
    metadata_fields = get_motion_metadata_fields()
    required_schema = get_required_fields()
    recommended_schema = get_recommended_fields()
    
    # Build field definitions
    class_fields = {}
    field_docs = {}
    
    # Add required BIDS entities (not from schema metadata)
    class_fields['subject_id'] = (str, field(metadata={'bids_name': 'sub', 'required': True}))
    field_docs['subject_id'] = "Subject identifier (BIDS entity 'sub')"
    
    class_fields['task_name'] = (str, field(metadata={'bids_name': 'TaskName', 'required': True}))
    field_docs['task_name'] = "Name of the task (BIDS metadata 'TaskName')"
    
    # Add tracksys as required (per BIDS motion spec)
    class_fields['tracksys'] = (str, field(metadata={'bids_name': 'tracksys', 'required': True}))
    field_docs['tracksys'] = "Tracking system label (BIDS entity 'tracksys') - REQUIRED for filenames"
    
    # Add required metadata fields from schema
    for schema_name in required_schema:
        if schema_name in metadata_fields:
            field_info = metadata_fields[schema_name]
            python_name = _snake_case(schema_name)
            python_type = _get_python_type(field_info.get('type', 'string'))
            
            # Skip if already added (like task_name)
            if python_name not in class_fields:
                class_fields[python_name] = (
                    python_type,
                    field(metadata={'bids_name': schema_name, 'required': True})
                )
                field_docs[python_name] = field_info.get('description', '').strip()
    
    # Add recommended metadata fields from schema
    for schema_name in recommended_schema:
        if schema_name in metadata_fields:
            field_info = metadata_fields[schema_name]
            python_name = _snake_case(schema_name)
            python_type = _get_python_type(field_info.get('type', 'string'))
            
            class_fields[python_name] = (
                Optional[python_type],
                field(default=None, metadata={'bids_name': schema_name, 'recommended': True})
            )
            field_docs[python_name] = field_info.get('description', '').strip()
    
    # RecordingType has a default value
    if 'recording_type' in class_fields:
        class_fields['recording_type'] = (
            Optional[str],
            field(default="continuous", metadata={'bids_name': 'RecordingType', 'recommended': True})
        )
    
    # Add optional BIDS entities
    class_fields['session_id'] = (
        Optional[str],
        field(default=None, metadata={'bids_name': 'ses', 'optional': True})
    )
    field_docs['session_id'] = "Session identifier (BIDS entity 'ses')"
    
    class_fields['acquisition'] = (
        Optional[str],
        field(default=None, metadata={'bids_name': 'acq', 'optional': True})
    )
    field_docs['acquisition'] = "Acquisition label (BIDS entity 'acq')"
    
    class_fields['run'] = (
        Optional[int],
        field(default=None, metadata={'bids_name': 'run', 'optional': True})
    )
    field_docs['run'] = "Run index (BIDS entity 'run')"
    
    class_fields['acq_time'] = (
        Optional[str],
        field(default=None, metadata={'optional': True})
    )
    field_docs['acq_time'] = "Acquisition time in ISO 8601 format with optional fractional seconds"
    
    # Add motion data fields
    class_fields['data'] = (
        Optional[np.ndarray],
        field(default=None, repr=False, metadata={'motion_data': True})
    )
    field_docs['data'] = "NumPy array containing motion time series data (shape: n_timepoints × n_channels)"
    
    class_fields['columns'] = (
        Optional[List[str]],
        field(default=None, metadata={'motion_data': True})
    )
    field_docs['columns'] = "List of column names for the TSV file (length must equal data.shape[1])"
    
    class_fields['units'] = (
        Optional[List[str]],
        field(default=None, metadata={'motion_data': True})
    )
    field_docs['units'] = "Units for each column (length must equal len(columns))"
    
    class_fields['additional_metadata'] = (
        Optional[Dict[str, Any]],
        field(default_factory=dict, metadata={'optional': True})
    )
    field_docs['additional_metadata'] = "Dictionary for any additional custom metadata"
    
    # Create docstring
    docstring = """
    Dataclass representing BIDS-compliant motion capture data.
    
    This class is dynamically generated from the BIDS schema using bidsschematools.
    
    **Data Format:**
    - `data`: NumPy array where **rows = timepoints** and **columns = channels**
    - `columns`: List of channel names that **must match** the number of data columns
    - `units`: List of units per channel that **must match** the length of `columns`
    - The `columns` and `units` define the structure of the `*_channels.tsv` file
    
    Required Fields (must be provided):
"""
    
    for name, (typ, fld) in class_fields.items():
        if fld.metadata.get('required'):
            docstring += f"        {name}: {field_docs.get(name, '')}\n"
    
    docstring += "\n    Recommended Fields (should be provided when available):\n"
    for name, (typ, fld) in class_fields.items():
        if fld.metadata.get('recommended'):
            docstring += f"        {name}: {field_docs.get(name, '')}\n"
    
    docstring += "\n    Optional Fields:\n"
    for name, (typ, fld) in class_fields.items():
        if fld.metadata.get('optional') or fld.metadata.get('motion_data'):
            docstring += f"        {name}: {field_docs.get(name, '')}\n"
    
    docstring += """
    Example:
        >>> import numpy as np
        >>> data = np.random.randn(1000, 30)  # 1000 timepoints, 30 channels
        >>> motion = MotionData(
        ...     subject_id="01",
        ...     task_name="walk",
        ...     tracksys="optical",
        ...     sampling_frequency=120.0,
        ...     tracked_points_count=10,
        ...     data=data,
        ...     columns=[f"ch{i}" for i in range(30)],
        ...     units=["mm"] * 30
        ... )
    """
    
    # Create the base class with annotations and validation
    class MotionDataBase:
        __doc__ = docstring
        __annotations__ = {}
        
        def __post_init__(self):
            """Validate basic field types and constraints."""
            if self.sampling_frequency <= 0:
                raise ValueError("sampling_frequency must be positive")
            
            if self.tracked_points_count <= 0:
                raise ValueError("tracked_points_count must be positive")
            
            if self.run is not None and self.run < 1:
                raise ValueError("run must be >= 1")
            
            if self.data is not None:
                if not isinstance(self.data, np.ndarray):
                    raise TypeError("data must be a numpy array")
                
                # Check if columns match data dimensions
                if self.columns is not None:
                    if self.data.ndim == 1:
                        expected_cols = 1
                    elif self.data.ndim == 2:
                        expected_cols = self.data.shape[1]
                    else:
                        raise ValueError("data must be 1D or 2D array")
                    
                    if len(self.columns) != expected_cols:
                        raise ValueError(
                            f"Number of columns ({len(self.columns)}) must match "
                            f"data dimensions ({expected_cols})"
                        )
                
                # Check if units match columns
                if self.units is not None and self.columns is not None:
                    if len(self.units) != len(self.columns):
                        raise ValueError(
                            f"Number of units ({len(self.units)}) must match "
                            f"number of columns ({len(self.columns)})"
                        )
    
    # Add fields to the class
    for field_name, (field_type, field_def) in class_fields.items():
        MotionDataBase.__annotations__[field_name] = field_type
        setattr(MotionDataBase, field_name, field_def)
    
    # Apply dataclass decorators
    MotionData = dataclass(MotionDataBase)
    MotionData = dataclass_json(MotionData)
    
    # Add helper methods
    def get_bids_filename(self, suffix: str = "motion", extension: str = "json") -> str:
        """
        Generate BIDS-compliant filename for this motion data.
        
        Args:
            suffix: BIDS suffix (default: 'motion')
            extension: File extension without dot (default: 'json')
        
        Returns:
            BIDS-compliant filename string
        
        Raises:
            ValueError: If tracksys is not provided (required for motion data)
        """
        if not self.tracksys:
            raise ValueError(
                "tracksys entity is required for BIDS motion data filenames. "
                "Please provide a tracking system label (e.g., 'optical', 'imu', 'video')."
            )
        
        parts = [f"sub-{self.subject_id}"]
        
        if self.session_id:
            parts.append(f"ses-{self.session_id}")
        
        parts.append(f"task-{self.task_name}")
        
        # tracksys is REQUIRED and comes before acq
        parts.append(f"tracksys-{self.tracksys}")
        
        if self.acquisition:
            parts.append(f"acq-{self.acquisition}")
        
        if self.run:
            parts.append(f"run-{self.run:02d}")
        
        parts.append(suffix)
        
        filename = "_".join(parts) + f".{extension}"
        return filename
    
    MotionData.get_bids_filename = get_bids_filename
    
    def to_metadata_dict(self) -> Dict[str, Any]:
        """
        Convert MotionData to a dictionary suitable for JSON export.
        
        Returns:
            Dictionary containing all metadata fields (excluding data array, columns, and units)
        """
        metadata = {}
        
        # Iterate through all fields and export based on BIDS names
        for fld in dataclass_fields(self):
            value = getattr(self, fld.name)
            
            # Skip None values, data fields, and entity fields
            if value is None:
                continue
            if fld.metadata.get('motion_data'):
                continue
            if fld.name in ['subject_id', 'session_id', 'acquisition', 'run', 'tracksys', 'acq_time', 'additional_metadata']:
                continue
            
            # Get BIDS name from metadata
            bids_name = fld.metadata.get('bids_name', fld.name)
            
            # Convert snake_case back to PascalCase if no BIDS name
            if bids_name == fld.name and '_' in fld.name:
                bids_name = ''.join(word.capitalize() for word in fld.name.split('_'))
            
            metadata[bids_name] = value
        
        # Add any additional metadata
        if self.additional_metadata:
            metadata.update(self.additional_metadata)
        
        return metadata
    
    MotionData.to_metadata_dict = to_metadata_dict
    
    return MotionData


# Generate the class at module import time
MotionData = _create_motion_data_class()

# Export for type checking
__all__ = ['MotionData']
