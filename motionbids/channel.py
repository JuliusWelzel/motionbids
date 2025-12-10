"""
Channel model for BIDS-compliant motion data.

This module defines the Channel dataclass that represents a single channel
in motion capture data, following the BIDS specification.
"""
from dataclasses import dataclass
from typing import Optional
from .bids_constants import (
    ALLOWED_CHANNEL_COMPONENTS,
    ALLOWED_CHANNEL_TYPES,
    CHANNEL_TYPE_COMPONENT_REQUIREMENTS
)


@dataclass
class Channel:
    """
    Dataclass representing a single channel in BIDS motion data.
    
    This follows the BIDS specification for channels.tsv files:
    https://bids-specification.readthedocs.io/en/stable/modality-specific-files/motion.html#channels-description-_channelstsv
    
    Required Fields (MUST appear in this order in channels.tsv):
        name: Label of the channel (e.g., "marker0_x", "imu1_acc_x")
        component: Spatial axis or quaternion component
                   Must be one of: x, y, z, quat_x, quat_y, quat_z, quat_w, n/a
        type: Channel type (MUST be uppercase)
              Must be one of: POS, ORNT, VEL, ACCEL, GYRO, ANGACCEL, MAGN, JNTANG, LATENCY, MISC
        tracked_point: Label of the tracked point (e.g., "LeftFoot", "RightWrist")
        units: Physical or virtual unit (e.g., "m", "rad", "m/s^2", "deg")
    
    Recommended Fields:
        placement: Placement on body (e.g., "torso", "left arm")
        reference_frame: Reference frame specification (links to channels.json)
        description: Brief description or other info
        sampling_frequency: Sampling rate in Hz (if different from main rate)
        status: Data quality - "good", "bad", or "n/a"
        status_description: Explanation if status is "bad"
    
    Example:
        >>> channel = Channel(
        ...     name="marker0_x",
        ...     component="x",
        ...     type="POS",
        ...     tracked_point="marker0",
        ...     units="mm"
        ... )
    
    Component-Type Compatibility:
        - Quaternion components (quat_*) can only be used with ORNT type
        - Spatial components (x, y, z) can be used with POS, VEL, ACCEL, GYRO, MAGN, ANGACCEL
        - n/a can be used with JNTANG, LATENCY, MISC
    """
    
    # Required fields (MUST be in this order)
    name: str
    component: str
    type: str
    tracked_point: str
    units: str
    
    # Recommended fields
    placement: Optional[str] = None
    reference_frame: Optional[str] = None
    description: Optional[str] = None
    sampling_frequency: Optional[float] = None
    status: Optional[str] = None
    status_description: Optional[str] = None
    
    def __post_init__(self):
        """Validate channel fields against BIDS schema."""
        # Validate component
        if self.component not in ALLOWED_CHANNEL_COMPONENTS:
            raise ValueError(
                f"Invalid component '{self.component}' for channel '{self.name}'. "
                f"Must be one of: {sorted(ALLOWED_CHANNEL_COMPONENTS)}"
            )
        
        # Validate type (must be uppercase)
        if self.type not in ALLOWED_CHANNEL_TYPES:
            raise ValueError(
                f"Invalid type '{self.type}' for channel '{self.name}'. "
                f"Must be one of (uppercase required): {sorted(ALLOWED_CHANNEL_TYPES)}"
            )
        
        # Validate component-type compatibility
        if self.type in CHANNEL_TYPE_COMPONENT_REQUIREMENTS:
            allowed_components = CHANNEL_TYPE_COMPONENT_REQUIREMENTS[self.type]
            if self.component not in allowed_components:
                raise ValueError(
                    f"Component '{self.component}' is not allowed for type '{self.type}' "
                    f"in channel '{self.name}'. "
                    f"Allowed components for {self.type}: {sorted(allowed_components)}"
                )
        
        # Validate status if provided
        if self.status is not None and self.status not in ["good", "bad", "n/a"]:
            raise ValueError(
                f"Invalid status '{self.status}' for channel '{self.name}'. "
                f"Must be one of: 'good', 'bad', 'n/a'"
            )
    
    def to_tsv_row(self) -> dict:
        """
        Convert channel to dictionary for TSV row export.
        
        Returns only non-None fields in the correct BIDS order.
        
        Returns:
            Dictionary with channel data for TSV export
        """
        row = {
            'name': self.name,
            'component': self.component,
            'type': self.type,
            'tracked_point': self.tracked_point,
            'units': self.units,
        }
        
        # Add optional fields if present
        if self.placement is not None:
            row['placement'] = self.placement
        if self.reference_frame is not None:
            row['reference_frame'] = self.reference_frame
        if self.description is not None:
            row['description'] = self.description
        if self.sampling_frequency is not None:
            row['sampling_frequency'] = self.sampling_frequency
        if self.status is not None:
            row['status'] = self.status
        if self.status_description is not None:
            row['status_description'] = self.status_description
        
        return row
