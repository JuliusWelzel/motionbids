"""
Tests for the MotionData datamodel.
"""
import pytest
import numpy as np
from motionbids.datamodel import MotionData


def test_motion_data_creation_minimal():
    """Test creating MotionData with only required fields."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        tracksys="optical"
    )
    
    assert motion.subject_id == "01"
    assert motion.task_name == "rest"
    assert motion.sampling_frequency == 100.0
    assert motion.tracked_points_count == 10
    assert motion.tracksys == "optical"


def test_motion_data_creation_full():
    """Test creating MotionData with all fields."""
    data = np.random.randn(100, 3)
    columns = ["x", "y", "z"]
    units = ["mm", "mm", "mm"]
    
    motion = MotionData(
        subject_id="01",
        task_name="walk",
        sampling_frequency=120.0,
        tracked_points_count=5,
        manufacturer="Vicon",
        manufacturers_model_name="Vantage",
        software_versions="2.0",
        motion_channel_count=15,
        recording_duration=10.0,
        recording_type="continuous",
        session_id="01",
        acquisition="outdoor",
        run=1,
        tracksys="optical",
        data=data,
        columns=columns,
        units=units,
        additional_metadata={"CustomField": "value"}
    )
    
    assert motion.manufacturer == "Vicon"
    assert motion.session_id == "01"
    assert motion.run == 1
    assert np.array_equal(motion.data, data)
    assert motion.columns == columns
    assert motion.units == units


def test_motion_data_invalid_sampling_frequency():
    """Test that negative sampling frequency raises error."""
    with pytest.raises(ValueError, match="sampling_frequency must be positive"):
        MotionData(
            subject_id="01",
            task_name="rest",
            sampling_frequency=-100.0,
            tracked_points_count=10,
            tracksys="optical"
        )


def test_motion_data_invalid_tracked_points():
    """Test that negative tracked points count raises error."""
    with pytest.raises(ValueError, match="tracked_points_count must be positive"):
        MotionData(
            subject_id="01",
            task_name="rest",
            sampling_frequency=100.0,
            tracked_points_count=-5,
            tracksys="optical"
        )


def test_motion_data_invalid_run():
    """Test that run < 1 raises error."""
    with pytest.raises(ValueError, match="run must be >= 1"):
        MotionData(
            subject_id="01",
            task_name="rest",
            sampling_frequency=100.0,
            tracked_points_count=10,
            tracksys="optical",
            run=0
        )


def test_motion_data_columns_mismatch():
    """Test that column count must match data dimensions."""
    data = np.random.randn(100, 3)
    columns = ["x", "y"]  # Only 2 columns for 3D data
    
    with pytest.raises(ValueError, match="Number of columns.*must match"):
        MotionData(
            subject_id="01",
            task_name="rest",
            sampling_frequency=100.0,
            tracked_points_count=10,
            tracksys="optical",
            data=data,
            columns=columns
        )


def test_motion_data_units_mismatch():
    """Test that units count must match columns count."""
    data = np.random.randn(100, 3)
    columns = ["x", "y", "z"]
    units = ["mm", "mm"]  # Only 2 units for 3 columns
    
    with pytest.raises(ValueError, match="Number of units.*must match"):
        MotionData(
            subject_id="01",
            task_name="rest",
            sampling_frequency=100.0,
            tracked_points_count=10,
            tracksys="optical",
            data=data,
            columns=columns,
            units=units
        )


def test_get_bids_filename_minimal():
    """Test BIDS filename generation with minimal fields."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        tracksys="optical"
    )
    
    filename = motion.get_bids_filename()
    assert filename == "sub-01_task-rest_tracksys-optical_motion.json"


def test_get_bids_filename_full():
    """Test BIDS filename generation with all optional entities."""
    motion = MotionData(
        subject_id="01",
        task_name="walk",
        sampling_frequency=100.0,
        tracked_points_count=10,
        session_id="01",
        acquisition="outdoor",
        run=2,
        tracksys="optical"
    )
    
    filename = motion.get_bids_filename()
    # Entity order: sub, ses, task, tracksys, acq, run
    assert filename == "sub-01_ses-01_task-walk_tracksys-optical_acq-outdoor_run-02_motion.json"


def test_get_bids_filename_custom_suffix():
    """Test BIDS filename generation with custom suffix and extension."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        tracksys="optical"
    )
    
    filename = motion.get_bids_filename(suffix="channels", extension="tsv")
    assert filename == "sub-01_task-rest_tracksys-optical_channels.tsv"


def test_to_metadata_dict():
    """Test conversion to metadata dictionary."""
    motion = MotionData(
        subject_id="01",
        task_name="walk",
        sampling_frequency=120.0,
        tracked_points_count=5,
        tracksys="optical",
        manufacturer="Vicon",
        recording_type="continuous"
    )
    
    metadata = motion.to_metadata_dict()
    
    assert metadata["TaskName"] == "walk"
    assert metadata["SamplingFrequency"] == 120.0
    assert metadata["TrackedPointsCount"] == 5
    assert metadata["Manufacturer"] == "Vicon"
    assert metadata["RecordingType"] == "continuous"


def test_to_metadata_dict_with_additional():
    """Test metadata dictionary includes additional metadata."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        tracksys="optical",
        additional_metadata={"CustomField": "custom_value", "AnotherField": 42}
    )
    
    metadata = motion.to_metadata_dict()
    
    assert metadata["CustomField"] == "custom_value"
    assert metadata["AnotherField"] == 42


def test_motion_data_with_1d_array():
    """Test MotionData with 1D data array."""
    data = np.random.randn(100)
    
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        tracksys="optical",
        data=data,
        columns=["x"]
    )
    
    assert motion.data.shape == (100,)
    assert motion.columns == ["x"]
