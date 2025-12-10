"""
Data model for BIDS-compliant motion data.

This module defines the MotionData dataclass that represents motion capture
data with BIDS-compliant metadata fields.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np
from dataclasses_json import dataclass_json
from .channel import Channel


@dataclass_json
@dataclass
class MotionData:
    """
    Dataclass representing BIDS-compliant motion capture data.
    
    This class includes both required and optional metadata fields for motion data,
    along with the actual motion time series data.
    
    **Data Format:**
    - `data`: NumPy array where **rows = timepoints** and **columns = channels** (REQUIRED)
    - `channels`: List of Channel objects defining channel metadata (REQUIRED)
    
    The `channels` list follows the BIDS specification for channels.tsv files.
    Each Channel object contains: name, component, type, tracked_point, units (all required),
    plus optional fields like placement, reference_frame, description, sampling_frequency, status.
    
    The number of Channel objects MUST match the number of columns in the data array.
    Channel metadata is validated against BIDS schema during Channel construction.
    
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
        additional_metadata: Dictionary for any additional custom metadata
    
    Example:
        >>> import numpy as np
        >>> from motionbids.channel import Channel
        >>> data = np.random.randn(1000, 30)  # 1000 timepoints, 30 channels
        >>> channels = [
        ...     Channel(name=f"marker{i//3}_{ax}", component=ax, type="POS",
        ...             tracked_point=f"marker{i//3}", units="mm")
        ...     for i in range(30) for ax in ['x', 'y', 'z'] if i % 3 == ['x', 'y', 'z'].index(ax)
        ... ]
        >>> motion = MotionData(
        ...     subject_id="01",
        ...     task_name="walk",
        ...     sampling_frequency=120.0,
        ...     tracked_points_count=10,
        ...     tracksys="optical",
        ...     data=data,
        ...     channels=channels
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
    
    # Motion data (REQUIRED - have defaults to avoid field ordering issues, validated in __post_init__)
    data: Optional[np.ndarray] = field(default=None, repr=False)
    channels: Optional[List[Channel]] = None
    
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
            
            # Validate data and channels together - both required if either is provided
            if self.data is not None or self.channels is not None:
                if self.data is None:
                    raise ValueError("data is required when channels are provided")
                
                if self.channels is None:
                    raise ValueError("channels is required when data is provided")
                
                if not isinstance(self.data, np.ndarray):
                    raise TypeError("data must be a numpy array")
                
                if self.data.ndim not in [1, 2]:
                    raise ValueError("data must be 1D or 2D array")
                
                # Determine expected number of channels
                if self.data.ndim == 1:
                    expected_channels = 1
                else:
                    expected_channels = self.data.shape[1]
                
                # Validate channels list length matches data dimensions
                if len(self.channels) != expected_channels:
                    raise ValueError(
                        f"Number of channels ({len(self.channels)}) must match "
                        f"data columns ({expected_channels})"
                    )
                
                # Channel validation happens in Channel.__post_init__
    
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
