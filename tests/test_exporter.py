"""
Tests for the export module.
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
import numpy as np
from motionbids import MotionData, Channel
from motionbids.exporter import (
    export_bids_motion,
    export_json_metadata,
    export_tsv_data,
    export_channels_tsv,
    create_bids_directory_structure,
    export_dataset_description,
    export_participants_tsv,
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
    channels = [
        Channel(channel_name="x", channel_component="x", channel_type="POS", channel_tracked_point="marker0", channel_units="mm"),
        Channel(channel_name="y", channel_component="y", channel_type="POS", channel_tracked_point="marker0", channel_units="mm"),
        Channel(channel_name="z", channel_component="z", channel_type="POS", channel_tracked_point="marker0", channel_units="mm")
    ]
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
        channels=channels
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
    # Check first data row - uses Channel objects
    parts = lines[1].strip().split('\t')
    assert parts[0] == "x"  # name
    assert parts[1] == "x"  # component
    assert parts[2] == "POS"  # type
    assert parts[3] == "marker0"  # tracked_point
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


def test_export_bids_motion_without_channels_fails(temp_dir):
    """Test that export fails if data is present but channels are not."""
    data = np.random.randn(100, 3)
    
    with pytest.raises(ValueError, match="Number of channels"):
        # Will fail in __post_init__ due to channel count mismatch
        motion = MotionData(
            subject_id="01",
            task_name="rest",
            tracksys="optical",
            sampling_frequency=100.0,
            tracked_points_count=10,
            data=data,
            channels=[]  # Empty channels list doesn't match data
        )


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
    channels = [
        Channel(channel_name="x", channel_component="x", channel_type="POS", channel_tracked_point="marker0", channel_units="mm")
    ]
    motion = MotionData(
        subject_id="01",
        task_name="rest",
        tracksys="optical",
        sampling_frequency=100.0,
        tracked_points_count=10,
        data=np.random.randn(100),
        channels=channels
    )
    
    files = export_bids_motion(motion, temp_dir)
    
    assert files['tsv'].exists()
    
    # Verify data is correctly saved (no header per BIDS spec)
    data = np.loadtxt(files['tsv'], delimiter='\t')
    assert data.shape == (100,)


def test_create_bids_directory_structure_no_session(temp_dir):
    """Without a session_id, motion files live directly under the subject."""
    motion_dir = create_bids_directory_structure(temp_dir, "01")

    assert motion_dir.exists()
    assert motion_dir == temp_dir / "sub-01" / "motion"  # No ses-* directory


def test_create_bids_directory_structure_with_session(temp_dir):
    """When a session_id is given, a ses-<label> directory level is created."""
    motion_dir = create_bids_directory_structure(temp_dir, "01", session_id="01")

    assert motion_dir.exists()
    assert motion_dir == temp_dir / "sub-01" / "ses-01" / "motion"

# ---- export_participants_tsv tests ----

def test_export_participants_tsv_creates_new_file(temp_dir):
    """Test creating a new participants.tsv from scratch."""
    output_path = export_participants_tsv(
        temp_dir, participant_id="01", age="25", sex="F", handedness="R"
    )

    assert output_path.exists()
    assert output_path == temp_dir / "participants.tsv"

    with open(output_path, "r") as f:
        lines = f.readlines()

    assert lines[0].strip() == "participant_id\tage\tsex\thandedness"
    parts = lines[1].strip().split("\t")
    assert parts[0] == "sub-01"
    assert parts[1] == "25"
    assert parts[2] == "F"
    assert parts[3] == "R"


def test_export_participants_tsv_auto_prefix(temp_dir):
    """Test that participant_id is automatically prefixed with sub-."""
    export_participants_tsv(temp_dir, participant_id="03")
    with open(temp_dir / "participants.tsv", "r") as f:
        lines = f.readlines()
    assert lines[1].strip().startswith("sub-03")


def test_export_participants_tsv_already_prefixed(temp_dir):
    """Test that sub- prefix is not duplicated."""
    export_participants_tsv(temp_dir, participant_id="sub-05")
    with open(temp_dir / "participants.tsv", "r") as f:
        lines = f.readlines()
    assert lines[1].strip().startswith("sub-05")


def test_export_participants_tsv_append(temp_dir):
    """Test appending a second participant to an existing file."""
    export_participants_tsv(temp_dir, participant_id="01", age="25", sex="F")
    export_participants_tsv(temp_dir, participant_id="02", age="30", sex="M")

    with open(temp_dir / "participants.tsv", "r") as f:
        lines = f.readlines()

    assert len(lines) == 3  # header + 2 participants
    assert "sub-01" in lines[1]
    assert "sub-02" in lines[2]


def test_export_participants_tsv_update_existing(temp_dir):
    """Test updating an existing participant entry."""
    export_participants_tsv(temp_dir, participant_id="01", age="25")
    export_participants_tsv(temp_dir, participant_id="01", age="26")

    with open(temp_dir / "participants.tsv", "r") as f:
        lines = f.readlines()

    # Should still be 2 lines (header + 1 participant), not duplicated
    assert len(lines) == 2
    assert "26" in lines[1]


def test_export_participants_tsv_extra_columns(temp_dir):
    """Test adding custom extra columns via kwargs."""
    export_participants_tsv(
        temp_dir, participant_id="01", age="25", group="control"
    )

    with open(temp_dir / "participants.tsv", "r") as f:
        lines = f.readlines()

    header_cols = lines[0].strip().split("\t")
    assert "group" in header_cols
    parts = lines[1].strip().split("\t")
    assert parts[header_cols.index("group")] == "control"


def test_export_participants_tsv_new_column_on_update(temp_dir):
    """Test that new columns are merged when updating an existing file."""
    export_participants_tsv(temp_dir, participant_id="01", age="25")
    export_participants_tsv(temp_dir, participant_id="02", age="30", group="patient")

    with open(temp_dir / "participants.tsv", "r") as f:
        lines = f.readlines()

    header_cols = lines[0].strip().split("\t")
    assert "group" in header_cols
    # First participant should have n/a for the new column
    parts_01 = lines[1].strip().split("\t")
    assert parts_01[header_cols.index("group")] == "n/a"


def test_export_participants_tsv_warns_on_existing(temp_dir):
    """Test that a warning is issued when the file already exists."""
    export_participants_tsv(temp_dir, participant_id="01")

    with pytest.warns(UserWarning, match="participants.tsv already exists"):
        export_participants_tsv(temp_dir, participant_id="02")


def test_export_participants_tsv_minimal(temp_dir):
    """Test creating participants.tsv with only participant_id."""
    export_participants_tsv(temp_dir, participant_id="99")

    with open(temp_dir / "participants.tsv", "r") as f:
        lines = f.readlines()

    assert lines[0].strip() == "participant_id"
    assert lines[1].strip() == "sub-99"
