"""
Tests for the validation module.
"""
import pytest
import warnings
import numpy as np
from motionbids.datamodel import MotionData
from motionbids.validator import (
    validate_motion_data,
    validate_bids_compliance,
    ValidationError,
    ValidationWarning,
    check_required_fields,
    check_recommended_fields,
)


def test_validate_motion_data_valid():
    """Test validation passes for valid data."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        manufacturer="Vicon",
        tracksys="optical",
    )
    
    assert validate_motion_data(motion) is True


def test_validate_motion_data_missing_required():
    """Test validation fails for missing required fields."""
    # Create data with empty subject_id (simulating missing required field)
    motion = MotionData(
        subject_id="",  # Invalid: empty string
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    with pytest.raises(ValidationError, match="Missing required fields"):
        validate_motion_data(motion)


def test_validate_motion_data_warns_missing_recommended():
    """Test validation warns about missing recommended fields."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
        # No recommended fields provided
    )
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        validate_motion_data(motion)
        
        # Should have warning about missing recommended fields
        assert len(w) > 0
        assert issubclass(w[0].category, ValidationWarning)
        assert "recommended" in str(w[0].message).lower()


def test_validate_motion_data_strict_mode():
    """Test strict mode raises error for missing recommended fields."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    with pytest.raises(ValidationError, match="recommended"):
        validate_motion_data(motion, strict=True)


def test_check_required_fields():
    """Test checking required fields."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    missing = check_required_fields(motion)
    assert len(missing) == 0


def test_check_required_fields_with_missing():
    """Test checking required fields with missing values."""
    motion = MotionData(
        subject_id="",  # Empty
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    missing = check_required_fields(motion)
    assert "subject_id" in missing


def test_check_recommended_fields():
    """Test checking recommended fields."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        manufacturer="Vicon",
        manufacturers_model_name="Vantage",
        software_versions="2.0",
        motion_channel_count=15,
        recording_duration=10.0,
        recording_type="continuous",
        tracksys="optical",
    )
    
    missing = check_recommended_fields(motion)
    assert len(missing) == 0


def test_check_recommended_fields_with_missing():
    """Test checking recommended fields with missing values."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    missing = check_recommended_fields(motion)
    assert "manufacturer" in missing
    assert "manufacturers_model_name" in missing


def test_validate_invalid_subject_id():
    """Test validation fails for invalid subject_id format."""
    motion = MotionData(
        subject_id="01 invalid",  # Space not allowed
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    with pytest.raises(ValidationError, match="subject_id"):
        validate_motion_data(motion)


def test_validate_invalid_task_name():
    """Test validation fails for invalid task_name format."""
    motion = MotionData(
        subject_id="01",
        task_name="rest task",  # Space not allowed
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    with pytest.raises(ValidationError, match="task_name"):
        validate_motion_data(motion)


def test_validate_high_sampling_frequency():
    """Test validation warns about unreasonably high sampling frequency."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=200000.0,  # 200 kHz - unreasonably high
        tracked_points_count=10
    )
    
    with pytest.raises(ValidationError, match="unreasonably high"):
        validate_motion_data(motion)


def test_validate_data_columns_mismatch():
    """Test that data column mismatch is caught in __post_init__."""
    data = np.random.randn(100, 3)
    
    # This should fail in __post_init__ when creating the MotionData object
    with pytest.raises(ValueError, match="Number of columns.*must match"):
        MotionData(
            subject_id="01",
            task_name="rest",
            tracksys="optical",
            sampling_frequency=100.0,
            tracked_points_count=10,
            data=data,
            columns=["x", "y"]  # Only 2 columns for 3D data
        )


def test_validate_data_duration_mismatch():
    """Test validation fails when data doesn't match recording duration."""
    data = np.random.randn(100, 3)  # 100 samples
    
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,  # 100 Hz
        tracked_points_count=10,
        recording_duration=2.0,  # 2 seconds would need 200 samples
        data=data,
        columns=["x", "y", "z"],
        units=["mm", "mm", "mm"],
        channel_component=["x", "y", "z"],
        channel_type=["POS", "POS", "POS"],
        channel_tracked_point=["marker0", "marker0", "marker0"]
    )
    
    with pytest.raises(ValidationError, match="Number of samples"):
        validate_motion_data(motion)


def test_validate_bids_compliance():
    """Test BIDS compliance check function."""
    motion_valid = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        tracksys="optical",
    )
    
    assert validate_bids_compliance(motion_valid) is True
    
    motion_invalid = MotionData(
        subject_id="",  # Invalid
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    assert validate_bids_compliance(motion_invalid) is False
