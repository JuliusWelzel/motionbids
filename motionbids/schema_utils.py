"""
Schema utilities for extracting BIDS motion metadata fields.

This module uses bidsschematools to extract schema definitions for motion data
without loading the schema at runtime in typical user workflows.
"""
from functools import lru_cache
from typing import Dict, List, Optional, Set
from bidsschematools import schema


@lru_cache(maxsize=1)
def _load_schema_cached():
    """Cached BIDS schema load — parsing the schema is expensive, so do it once."""
    return schema.load_schema()


def get_motion_metadata_fields() -> Dict[str, Dict]:
    """
    Extract motion-related metadata fields from BIDS schema.
    
    Returns:
        Dictionary mapping field names to their schema definitions,
        including requirement level (required/recommended/optional).
    """
    # Load the BIDS schema
    bids_schema = _load_schema_cached()
    
    # Get metadata fields - motion data typically uses the same metadata structure
    # as other continuous recordings (like physiological data)
    metadata_fields = {}
    
    # Get all metadata objects from the schema
    if hasattr(bids_schema, 'objects') and 'metadata' in bids_schema.objects:
        for field_name, field_info in bids_schema.objects.metadata.items():
            metadata_fields[field_name] = {
                'name': field_name,
                'type': field_info.get('type', 'string'),
                'description': field_info.get('description', ''),
                'requirement_level': field_info.get('requirement_level', 'optional')
            }
    
    return metadata_fields


def get_motion_entities() -> Dict[str, Dict]:
    """
    Extract BIDS entities relevant to motion data.
    
    Returns:
        Dictionary mapping entity names to their schema definitions.
    """
    bids_schema = _load_schema_cached()
    entities = {}
    
    # Common entities for motion data
    common_motion_entities = ['subject', 'session', 'task', 'acquisition', 'run', 'tracksys']
    
    if hasattr(bids_schema, 'objects') and 'entities' in bids_schema.objects:
        for entity_name, entity_info in bids_schema.objects.entities.items():
            if entity_name in common_motion_entities:
                entities[entity_name] = {
                    'name': entity_name,
                    'type': entity_info.get('type', 'string'),
                    'description': entity_info.get('description', ''),
                    'format': entity_info.get('format', '')
                }
    
    return entities


def get_required_fields() -> Set[str]:
    """
    Get the set of required fields for motion data.
    
    Returns:
        Set of required field names.
    """
    required = set()
    
    # Core required fields for motion data (based on BIDS spec)
    # These are typically required for continuous recordings
    core_required = [
        'SamplingFrequency',
        'TaskName',
        'TrackedPointsCount'
    ]
    
    metadata = get_motion_metadata_fields()
    for field_name, field_info in metadata.items():
        if field_info.get('requirement_level') == 'required':
            required.add(field_name)
    
    # Add core required fields
    required.update(core_required)
    
    return required


def get_recommended_fields() -> Set[str]:
    """
    Get the set of recommended fields for motion data.
    
    Returns:
        Set of recommended field names.
    """
    recommended = set()
    
    # Core recommended fields for motion data
    core_recommended = [
        'Manufacturer',
        'ManufacturersModelName',
        'SoftwareVersions',
        'MotionChannelCount',
        'RecordingDuration',
        'RecordingType'
    ]
    
    metadata = get_motion_metadata_fields()
    for field_name, field_info in metadata.items():
        if field_info.get('requirement_level') == 'recommended':
            recommended.add(field_name)
    
    # Add core recommended fields
    recommended.update(core_recommended)
    
    return recommended


def get_field_type(field_name: str) -> type:
    """
    Get the Python type for a given BIDS field.
    
    Args:
        field_name: Name of the BIDS field
        
    Returns:
        Python type (str, int, float, list, etc.)
    """
    type_mapping = {
        'string': str,
        'number': float,
        'integer': int,
        'boolean': bool,
        'array': list,
        'object': dict
    }
    
    metadata = get_motion_metadata_fields()
    if field_name in metadata:
        schema_type = metadata[field_name].get('type', 'string')
        return type_mapping.get(schema_type, str)
    
    return str
