"""
Validation utilities for BIDS-compliant motion data.

This module provides functions to validate MotionData instances against
BIDS requirements and recommendations.
"""
from __future__ import annotations

import re
import warnings
from typing import TYPE_CHECKING, List, Set, Tuple

if TYPE_CHECKING:
    from .datamodel_dynamic import MotionData


# Define required fields based on BIDS specification for motion data
REQUIRED_FIELDS = {
    'subject',
    'task_name',
    'sampling_frequency',
    'tracked_points_count',
    'tracksys',  # Required for BIDS-compliant motion data filenames
}

# Define recommended fields
RECOMMENDED_FIELDS = {
    'manufacturer',
    'manufacturers_model_name',
    'software_versions',
    'motion_channel_count',
    'recording_duration',
    'recording_type',
}

# BIDS entity-label format. Per the BIDS schema (objects.formats.label) a label
# must match this pattern: ASCII alphanumerics and the '+' character only.
# Notably '_' and '-' are reserved as the BIDS entity and key/value separators
# and are therefore NOT permitted inside a label.
BIDS_LABEL_PATTERN = re.compile(r'[0-9a-zA-Z+]+')


class ValidationError(ValueError):
    """Exception raised for validation errors."""
    pass


class ValidationWarning(UserWarning):
    """Warning raised for validation recommendations."""
    pass


def validate_motion_data(data: MotionData, strict: bool = False) -> bool:
    """
    Validate a MotionData instance against BIDS requirements.
    
    This function checks:
    1. All required fields are present and non-None
    2. Required fields have valid values
    3. Recommended fields are present (warns if missing)
    
    Args:
        data: MotionData instance to validate
        strict: If True, raise ValidationError for missing recommended fields
                If False (default), only warn about missing recommended fields
    
    Returns:
        True if validation passes
    
    Raises:
        ValidationError: If required fields are missing or invalid
    
    Example:
        >>> motion = MotionData(subject="01", task_name="rest", ...)
        >>> validate_motion_data(motion)
        True
    """
    errors = []
    warnings_list = []
    
    # Check required fields
    missing_required = check_required_fields(data)
    if missing_required:
        errors.append(f"Missing required fields: {', '.join(missing_required)}")
    
    # Validate field values
    value_errors = validate_field_values(data)
    errors.extend(value_errors)
    
    # Check recommended fields
    missing_recommended = check_recommended_fields(data)
    if missing_recommended:
        warning_msg = f"Missing recommended fields: {', '.join(missing_recommended)}"
        warnings_list.append(warning_msg)
        
        if strict:
            errors.append(warning_msg)
        else:
            warnings.warn(warning_msg, ValidationWarning, stacklevel=2)
    
    # Raise exception if there are errors
    if errors:
        error_msg = "Validation failed:\n  - " + "\n  - ".join(errors)
        raise ValidationError(error_msg)
    
    return True


def check_required_fields(data: MotionData) -> Set[str]:
    """
    Check if all required fields are present and non-None.
    
    Args:
        data: MotionData instance to check
    
    Returns:
        Set of missing required field names
    """
    missing = set()
    
    for field_name in REQUIRED_FIELDS:
        value = getattr(data, field_name, None)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.add(field_name)
    
    return missing


def check_recommended_fields(data: MotionData) -> Set[str]:
    """
    Check if recommended fields are present.
    
    Args:
        data: MotionData instance to check
    
    Returns:
        Set of missing recommended field names
    """
    missing = set()
    
    for field_name in RECOMMENDED_FIELDS:
        value = getattr(data, field_name, None)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.add(field_name)
    
    return missing


def _check_label(value: object, entity_name: str, errors: List[str]) -> None:
    """
    Append an error if ``value`` is not a BIDS-compliant entity label.

    A BIDS label must match ``[0-9a-zA-Z+]+`` (ASCII alphanumerics and the
    ``+`` character). ``_`` and ``-`` are reserved separators and are not
    permitted inside a label. ``None`` and empty values are skipped here;
    presence of required entities is enforced by :func:`check_required_fields`.

    Args:
        value: The label value to check.
        entity_name: Name of the entity, used in the error message.
        errors: List that an error message is appended to on failure.
    """
    if value and not BIDS_LABEL_PATTERN.fullmatch(value):
        errors.append(
            f"{entity_name} label '{value}' is not BIDS-compliant: labels must "
            f"contain only alphanumeric characters and '+' "
            f"(no '_', '-', spaces, or non-ASCII characters)"
        )


def validate_field_values(data: MotionData) -> List[str]:
    """
    Validate that field values are within acceptable ranges and formats.
    
    Args:
        data: MotionData instance to validate
    
    Returns:
        List of error messages for invalid fields
    """
    errors = []
    
    # Validate BIDS entity labels (sub-, ses-, task-, acq-, tracksys-).
    # Each must match the BIDS label format; '_' and '-' are reserved
    # separators and are not allowed inside a label.
    _check_label(data.subject, "subject", errors)
    _check_label(data.session, "session", errors)
    _check_label(data.task_name, "task_name", errors)
    _check_label(data.acquisition, "acquisition", errors)
    _check_label(data.tracksys, "tracksys", errors)
    
    # Validate sampling_frequency
    if data.sampling_frequency is not None:
        if data.sampling_frequency <= 0:
            errors.append("sampling_frequency must be positive")
        elif data.sampling_frequency > 100000:  # Reasonable upper limit
            errors.append(
                "sampling_frequency seems unreasonably high (>100kHz). "
                "Please verify the value."
            )
    
    # Validate tracked_points_count
    if data.tracked_points_count is not None:
        if data.tracked_points_count <= 0:
            errors.append("tracked_points_count must be positive")
    
    # Validate motion_channel_count if present
    if data.motion_channel_count is not None:
        if data.motion_channel_count <= 0:
            errors.append("motion_channel_count must be positive")
    
    # Validate recording_duration if present
    if data.recording_duration is not None:
        if data.recording_duration <= 0:
            errors.append("recording_duration must be positive")
    
    # Validate run if present
    if data.run is not None:
        if data.run < 1:
            errors.append("run must be >= 1")
    
    # Validate data array consistency if present
    if data.data is not None:
        if data.channels is not None:
            n_cols = data.data.shape[1] if data.data.ndim > 1 else 1
            if len(data.channels) != n_cols:
                errors.append(
                    f"Number of channels ({len(data.channels)}) does not match "
                    f"data dimensions ({n_cols})"
                )
        
        if data.recording_duration is not None:
            n_samples = data.data.shape[0]
            expected_samples = int(data.recording_duration * data.sampling_frequency)
            # Allow 1% tolerance
            if abs(n_samples - expected_samples) > expected_samples * 0.01:
                errors.append(
                    f"Number of samples ({n_samples}) does not match "
                    f"recording_duration ({data.recording_duration}s) and "
                    f"sampling_frequency ({data.sampling_frequency}Hz). "
                    f"Expected ~{expected_samples} samples."
                )
    
    # Note: Channel metadata validation is performed in MotionData.__post_init__
    # during construction, so we don't need to validate it here again
    
    return errors


def validate_bids_compliance(data: MotionData) -> bool:
    """
    Perform comprehensive BIDS compliance validation.
    
    This is a convenience function that performs full validation and
    returns a boolean result.
    
    Args:
        data: MotionData instance to validate
    
    Returns:
        True if fully BIDS compliant, False otherwise
    """
    try:
        validate_motion_data(data, strict=False)
        return True
    except ValidationError:
        return False
