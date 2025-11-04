"""
Data model for BIDS-compliant motion data.

This module defines the MotionData dataclass that represents motion capture
data with BIDS-compliant metadata fields.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class MotionData:
    """
    Dataclass representing BIDS-compliant motion capture data.
    
    This class includes both required and optional metadata fields for motion data,
    along with the actual motion time series data.
    
    **Data Format:**
    - `data`: NumPy array where **rows = timepoints** and **columns = channels**
    - `columns`: List of channel names that **must match** the number of data columns
    - `units`: List of units per channel that **must match** the length of `columns`
    - The `columns` and `units` define the structure of the `*_channels.tsv` file
    
    Required Fields (must be provided):
        subject_id: Subject identifier (BIDS entity 'sub')
        task_name: Name of the task (BIDS metadata 'TaskName')
        sampling_frequency: Sampling frequency in Hz (BIDS metadata 'SamplingFrequency')
        tracked_points_count: Number of tracked points (BIDS metadata 'TrackedPointsCount')
        tracksys: Tracking system label (BIDS entity 'tracksys') - REQUIRED for filenames
    
    Recommended Fields (should be provided when available):
        manufacturer: Manufacturer of the motion capture system
        manufacturers_model_name: Model name of the motion capture system
        software_versions: Software version used for acquisition
        motion_channel_count: Total number of motion channels
        recording_duration: Duration of the recording in seconds
        recording_type: Type of recording (e.g., 'continuous')
    
    Optional Fields:
        session_id: Session identifier (BIDS entity 'ses')
        acquisition: Acquisition label (BIDS entity 'acq')
        run: Run index (BIDS entity 'run')
        acq_time: Acquisition time in ISO 8601 format with optional fractional seconds
                  (e.g., '2023-06-15T14:30:00' or '2023-06-15T14:30:00.123456')
                  Supports sub-millisecond precision. If provided, a scans.tsv file will be generated
        data: NumPy array containing motion time series data (shape: n_timepoints × n_channels)
        columns: List of column names for the TSV file (length must equal data.shape[1])
        units: Units for each column (length must equal len(columns))
        additional_metadata: Dictionary for any additional custom metadata
    
    Example:
        >>> import numpy as np
        >>> data = np.random.randn(1000, 30)  # 1000 timepoints, 30 channels
        >>> motion = MotionData(
        ...     subject_id="01",
        ...     task_name="walk",
        ...     sampling_frequency=120.0,
        ...     tracked_points_count=10,
        ...     data=data,
        ...     columns=[f"ch{i}" for i in range(30)],
        ...     units=["mm"] * 30
        ... )
    """
    
    # Required fields
    subject_id: str
    task_name: str
    sampling_frequency: float
    tracked_points_count: int
    tracksys: str  # REQUIRED for BIDS motion data filenames
    
    # Recommended fields
    manufacturer: Optional[str] = None
    manufacturers_model_name: Optional[str] = None
    software_versions: Optional[str] = None
    motion_channel_count: Optional[int] = None
    recording_duration: Optional[float] = None
    recording_type: Optional[str] = "continuous"
    
    # Optional BIDS entities
    session_id: Optional[str] = None
    acquisition: Optional[str] = None
    run: Optional[int] = None
    acq_time: Optional[str] = None  # ISO 8601 with optional fractional seconds (e.g., '2023-06-15T14:30:00.123456')
    
    # Motion data
    data: Optional[np.ndarray] = field(default=None, repr=False)
    columns: Optional[List[str]] = None
    units: Optional[List[str]] = None
    
    # Additional metadata
    additional_metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
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
        
        Example:
            >>> motion = MotionData(subject_id="01", task_name="rest", tracksys="optical", ...)
            >>> motion.get_bids_filename()
            'sub-01_task-rest_tracksys-optical_motion.json'
        
        Note:
            Entity order follows BIDS specification:
            sub-<label>[_ses-<label>]_task-<label>_tracksys-<label>[_acq-<label>][_run-<index>]
            The tracksys entity is REQUIRED for motion data.
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
    
    def to_metadata_dict(self) -> Dict[str, Any]:
        """
        Convert MotionData to a dictionary suitable for JSON export.
        
        Returns:
            Dictionary containing all metadata fields (excluding data array, columns, and units)
        """
        metadata = {
            "TaskName": self.task_name,
            "SamplingFrequency": self.sampling_frequency,
            "TrackedPointsCount": self.tracked_points_count,
        }
        
        # Add recommended fields if present
        if self.manufacturer:
            metadata["Manufacturer"] = self.manufacturer
        if self.manufacturers_model_name:
            metadata["ManufacturersModelName"] = self.manufacturers_model_name
        if self.software_versions:
            metadata["SoftwareVersions"] = self.software_versions
        if self.motion_channel_count:
            metadata["MotionChannelCount"] = self.motion_channel_count
        if self.recording_duration:
            metadata["RecordingDuration"] = self.recording_duration
        if self.recording_type:
            metadata["RecordingType"] = self.recording_type
        
        # Note: columns and units are NOT exported to JSON - they go in channels.tsv
        
        # Add any additional metadata
        if self.additional_metadata:
            metadata.update(self.additional_metadata)
        
        return metadata
