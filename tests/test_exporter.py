"""
Tests for the export module.
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
import numpy as np
from motionbids.datamodel import MotionData
from motionbids.exporter import (
    export_bids_motion,
    export_json_metadata,
    export_tsv_data,
    export_channels_tsv,
    create_bids_directory_structure,
    export_dataset_description,
    _parse_channel_name,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_motion_data():
    """Create sample MotionData for testing."""
    data = np.random.randn(100, 3)
    return MotionData(
        subject_id="01",
        task_name="walk",
        sampling_frequency=120.0,
        tracked_points_count=10,
        tracksys="optical",
        manufacturer="Vicon",
        manufacturers_model_name="Vantage",
        recording_duration=100/120.0,  # Match data length
        data=data,
        columns=["x", "y", "z"],
        units=["mm", "mm", "mm"],
        channel_component=["x", "y", "z"],
        channel_type=["POS", "POS", "POS"],
        channel_tracked_point=["marker0", "marker0", "marker0"],
    )


def test_export_json_metadata(temp_dir, sample_motion_data):
    """Test exporting JSON metadata."""
    output_path = temp_dir / "test_motion.json"
    
    result_path = export_json_metadata(sample_motion_data, output_path)
    
    assert result_path.exists()
    
    # Load and verify JSON content
    with open(result_path, 'r') as f:
        metadata = json.load(f)
    
    assert metadata["TaskName"] == "walk"
    assert metadata["SamplingFrequency"] == 120.0
    assert metadata["TrackedPointsCount"] == 10
    assert metadata["Manufacturer"] == "Vicon"


def test_export_tsv_data(temp_dir, sample_motion_data):
    """Test exporting TSV data."""
    output_path = temp_dir / "test_motion.tsv"
    
    result_path = export_tsv_data(sample_motion_data, output_path)
    
    assert result_path.exists()
    
    # Load and verify TSV content (no header per BIDS spec)
    data = np.loadtxt(result_path, delimiter='\t')
    
    assert data.shape == (100, 3)
    np.testing.assert_array_almost_equal(data, sample_motion_data.data)


def test_export_channels_tsv(temp_dir, sample_motion_data):
    """Test exporting channels TSV."""
    output_path = temp_dir / "test_channels.tsv"
    
    result_path = export_channels_tsv(sample_motion_data, output_path)
    
    assert result_path.exists()
    
    # Verify content
    with open(result_path, 'r') as f:
        lines = f.readlines()
    
    # Check header has all required columns in correct order
    assert lines[0].strip() == "name\tcomponent\ttype\ttracked_point\tunits"
    # Check first data row - now uses explicit channel metadata
    parts = lines[1].strip().split('\t')
    assert parts[0] == "x"  # name
    assert parts[1] == "x"  # component (from channel_component)
    assert parts[2] == "POS"  # type (from channel_type)
    assert parts[3] == "marker0"  # tracked_point (from channel_tracked_point)
    assert parts[4] == "mm"  # units


def test_export_bids_motion_full(temp_dir, sample_motion_data):
    """Test full BIDS export with all files."""
    files = export_bids_motion(sample_motion_data, temp_dir)
    
    assert 'json' in files
    assert 'tsv' in files
    assert 'channels' in files
    
    assert files['json'].exists()
    assert files['tsv'].exists()
    assert files['channels'].exists()
    
    # Verify filenames follow BIDS convention (now includes required tracksys)
    assert files['json'].name == "sub-01_task-walk_tracksys-optical_motion.json"
    assert files['tsv'].name == "sub-01_task-walk_tracksys-optical_motion.tsv"
    assert files['channels'].name == "sub-01_task-walk_tracksys-optical_channels.tsv"


def test_export_bids_motion_metadata_only(temp_dir):
    """Test BIDS export with only metadata (no data array)."""
    motion = MotionData(
        subject_id="02",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=5,
        manufacturer="OptiTrack",
        tracksys="optical"
    )
    
    files = export_bids_motion(motion, temp_dir)
    
    assert 'json' in files
    assert 'tsv' not in files
    assert 'channels' not in files
    
    assert files['json'].exists()


def test_export_bids_motion_no_overwrite(temp_dir, sample_motion_data):
    """Test that export fails when files exist and overwrite=False."""
    # First export
    export_bids_motion(sample_motion_data, temp_dir)
    
    # Second export should fail
    with pytest.raises(FileExistsError):
        export_bids_motion(sample_motion_data, temp_dir, overwrite=False)


def test_export_bids_motion_with_overwrite(temp_dir, sample_motion_data):
    """Test that export succeeds with overwrite=True."""
    # First export
    files1 = export_bids_motion(sample_motion_data, temp_dir)
    
    # Second export with overwrite should succeed
    files2 = export_bids_motion(sample_motion_data, temp_dir, overwrite=True)
    
    assert files1['json'] == files2['json']


def test_export_bids_motion_create_dirs(temp_dir):
    """Test that export creates directories if needed."""
    output_dir = temp_dir / "nested" / "directories"
    
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        sampling_frequency=100.0,
        tracked_points_count=10,
        manufacturer="Vicon",
        tracksys="optical"
    )
    
    files = export_bids_motion(motion, output_dir, create_dirs=True)
    
    assert output_dir.exists()
    assert files['json'].exists()


def test_export_bids_motion_without_columns_fails(temp_dir):
    """Test that export fails if data is present but columns are not."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10,
        data=np.random.randn(100, 3)
        # No columns specified
    )
    
    with pytest.raises(ValueError, match="columns are not defined"):
        export_bids_motion(motion, temp_dir)


def test_create_bids_directory_structure(temp_dir):
    """Test creating BIDS directory structure."""
    motion_dir = create_bids_directory_structure(temp_dir, "01")
    
    assert motion_dir.exists()
    assert motion_dir == temp_dir / "sub-01" / "motion"


def test_create_bids_directory_structure_with_session(temp_dir):
    """Test creating BIDS directory structure with session."""
    motion_dir = create_bids_directory_structure(temp_dir, "01", "02")
    
    assert motion_dir.exists()
    assert motion_dir == temp_dir / "sub-01" / "ses-02" / "motion"


def test_export_dataset_description(temp_dir):
    """Test exporting dataset_description.json."""
    output_path = export_dataset_description(
        temp_dir,
        name="Test Dataset",
        authors=["Jane Doe", "John Smith"]
    )
    
    assert output_path.exists()
    assert output_path == temp_dir / "dataset_description.json"
    
    # Verify content
    with open(output_path, 'r') as f:
        description = json.load(f)
    
    assert description["Name"] == "Test Dataset"
    assert description["BIDSVersion"] == "1.9.0"
    assert description["DatasetType"] == "raw"
    assert description["Authors"] == ["Jane Doe", "John Smith"]


def test_export_with_all_entities(temp_dir):
    """Test export with all BIDS entities."""
    motion = MotionData(
        subject_id="01",
        session_id="01",
        task_name="walk",
        acquisition="outdoor",
        run=2,
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10,
        manufacturer="Vicon",
    )
    
    files = export_bids_motion(motion, temp_dir)
    
    # Entity order: sub, ses, task, tracksys, acq, run
    expected_name = "sub-01_ses-01_task-walk_tracksys-optical_acq-outdoor_run-02_motion.json"
    assert files['json'].name == expected_name


def test_export_tsv_1d_data(temp_dir):
    """Test exporting 1D data array."""
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10,
        data=np.random.randn(100),
        columns=["x"],
        units=["mm"],
        channel_component=["x"],
        channel_type=["POS"],
        channel_tracked_point=["marker0"]
    )
    
    files = export_bids_motion(motion, temp_dir)
    
    assert files['tsv'].exists()
    
    # Verify data is correctly saved (no header per BIDS spec)
    data = np.loadtxt(files['tsv'], delimiter='\t')
    assert data.shape == (100,)


def test_parse_channel_name_position():
    """Test parsing position channel names."""
    component, tracked_point, channel_type = _parse_channel_name("marker0_x")
    assert component == "x"
    assert tracked_point == "marker0"
    assert channel_type == "POS"
    
    component, tracked_point, channel_type = _parse_channel_name("point1_y")
    assert component == "y"
    assert tracked_point == "point1"
    assert channel_type == "POS"


def test_parse_channel_name_orientation():
    """Test parsing orientation channel names."""
    # Quaternion
    component, tracked_point, channel_type = _parse_channel_name("marker0_quat_w")
    assert component == "quat_w"
    assert tracked_point == "marker0"
    assert channel_type == "ORNT"
    
    # Euler angles
    component, tracked_point, channel_type = _parse_channel_name("sensor1_roll")
    assert component == "roll"
    assert tracked_point == "sensor1"
    assert channel_type == "ORNT"


def test_parse_channel_name_velocity():
    """Test parsing velocity channel names."""
    component, tracked_point, channel_type = _parse_channel_name("marker0_vx")
    assert component == "vx"
    assert tracked_point == "marker0"
    assert channel_type == "VEL"


def test_parse_channel_name_acceleration():
    """Test parsing acceleration channel names."""
    component, tracked_point, channel_type = _parse_channel_name("marker0_ax")
    assert component == "ax"
    assert tracked_point == "marker0"
    assert channel_type == "ACCEL"


def test_parse_channel_name_unparseable():
    """Test parsing unparseable channel names."""
    component, tracked_point, channel_type = _parse_channel_name("unknown_channel")
    assert component == "n/a"
    assert tracked_point == "unknown_channel"
    assert channel_type == "POS"
