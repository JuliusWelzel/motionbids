"""
Tests for the validation module.
"""
import pytest
import warnings
import numpy as np
from motionbids import MotionData, Channel
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
        subject="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        manufacturer="Vicon",
        tracksys="optical",
    )
    
    assert validate_motion_data(motion) is True


def test_validate_motion_data_missing_required():
    """Test validation fails for missing required fields."""
    # Create data with empty subject (simulating missing required field)
    motion = MotionData(
        subject="",  # Invalid: empty string
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
        subject="01",
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
        subject="01",
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
        subject="01",
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
        subject="",  # Empty
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    missing = check_required_fields(motion)
    assert "subject" in missing


def test_check_recommended_fields():
    """Test checking recommended fields."""
    motion = MotionData(
        subject="01",
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
        subject="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    missing = check_recommended_fields(motion)
    assert "manufacturer" in missing
    assert "manufacturers_model_name" in missing


def test_validate_invalid_subject():
    """Test validation fails for invalid subject format."""
    motion = MotionData(
        subject="01 invalid",  # Space not allowed
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    with pytest.raises(ValidationError, match="subject"):
        validate_motion_data(motion)


def test_validate_invalid_task_name():
    """Test validation fails for invalid task_name format."""
    motion = MotionData(
        subject="01",
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
        subject="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=200000.0,  # 200 kHz - unreasonably high
        tracked_points_count=10
    )
    
    with pytest.raises(ValidationError, match="unreasonably high"):
        validate_motion_data(motion)


def test_validate_data_columns_mismatch():
    """Test that data channel mismatch is caught in __post_init__."""
    data = np.random.randn(100, 3)
    channels = [
        Channel(channel_name="x", channel_component="x", channel_type="POS", channel_tracked_point="marker0", channel_units="mm"),
        Channel(channel_name="y", channel_component="y", channel_type="POS", channel_tracked_point="marker0", channel_units="mm")
    ]  # Only 2 channels for 3D data
    
    # This should fail in __post_init__ when creating the MotionData object
    with pytest.raises(ValueError, match="Number of channels.*must match"):
        MotionData(
            subject="01",
            task_name="rest",
            tracksys="optical",
            sampling_frequency=100.0,
            tracked_points_count=10,
            data=data,
            channels=channels
        )


def test_validate_data_duration_mismatch():
    """Test validation fails when data doesn't match recording duration."""
    data = np.random.randn(100, 3)  # 100 samples
    channels = [
        Channel(channel_name="x", channel_component="x", channel_type="POS", channel_tracked_point="marker0", channel_units="mm"),
        Channel(channel_name="y", channel_component="y", channel_type="POS", channel_tracked_point="marker0", channel_units="mm"),
        Channel(channel_name="z", channel_component="z", channel_type="POS", channel_tracked_point="marker0", channel_units="mm")
    ]
    
    motion = MotionData(
        subject="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,  # 100 Hz
        tracked_points_count=10,
        recording_duration=2.0,  # 2 seconds would need 200 samples
        data=data,
        channels=channels
    )
    
    with pytest.raises(ValidationError, match="Number of samples"):
        validate_motion_data(motion)


def test_validate_bids_compliance():
    """Test BIDS compliance check function."""
    motion_valid = MotionData(
        subject="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        tracksys="optical",
    )
    
    assert validate_bids_compliance(motion_valid) is True
    
    motion_invalid = MotionData(
        subject="",  # Invalid
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10
    )
    
    assert validate_bids_compliance(motion_invalid) is False


# --- BIDS entity-label format regression tests --------------------------------
# A BIDS label must match [0-9a-zA-Z+]+ : ASCII alphanumerics and '+' only.
# '_' and '-' are reserved separators and are forbidden inside a label.

def _make_motion(**overrides):
    """Build a minimal otherwise-valid MotionData, applying field overrides."""
    params = dict(
        subject="01",
        task_name="rest",
        tracksys="imu",
        sampling_frequency=100.0,
        tracked_points_count=10,
    )
    params.update(overrides)
    return MotionData(**params)


@pytest.mark.parametrize("field, value", [
    ("subject", "01"),
    ("subject", "001"),       # leading zeros are allowed (digits)
    ("subject", "01+02"),     # '+' is permitted by the BIDS label format
    ("session", "pre"),
    ("session", "01"),
    ("task_name", "restEC"),
    ("acquisition", "highSNR"),
    ("tracksys", "imu"),
])
def test_valid_bids_labels(field, value):
    """Labels matching [0-9a-zA-Z+]+ are accepted for every label entity."""
    motion = _make_motion(**{field: value})
    assert validate_bids_compliance(motion) is True


@pytest.mark.parametrize("field, value", [
    ("subject", "01_A"),      # '_' is the BIDS entity separator
    ("subject", "01-A"),      # '-' is the BIDS key/value separator
    ("subject", "café"), # non-ASCII alphanumerics are not allowed
    ("subject", "01\n"),      # trailing newline must not slip through
    ("task_name", "rest_2"),
    ("task_name", "rest task"),  # space
    ("session", "pre_1"),     # regression: session was previously unvalidated
    ("session", "a b"),
    ("acquisition", "hi_res"),   # regression: acq was previously unvalidated
    ("tracksys", "imu_left"),    # regression: tracksys was previously unvalidated
])
def test_invalid_bids_labels(field, value):
    """Labels with '_', '-', spaces, non-ASCII, or newlines are rejected per entity."""
    motion = _make_motion(**{field: value})
    with pytest.raises(ValidationError, match=field):
        validate_motion_data(motion)
