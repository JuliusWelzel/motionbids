"""
BIDS schema constants for motion data validation.

This module defines the allowed values for channel components and types
according to the BIDS specification.
"""

# Allowed channel components (from BIDS schema)
ALLOWED_CHANNEL_COMPONENTS = {
    'x',       # Position along X-axis, rotation about X-axis, or magnetic field strength along X-axis
    'y',       # Position along Y-axis, rotation about Y-axis, or magnetic field strength along Y-axis
    'z',       # Position along Z-axis, rotation about Z-axis, or magnetic field strength along Z-axis
    'quat_x',  # Quaternion component associated with X-axis
    'quat_y',  # Quaternion component associated with Y-axis
    'quat_z',  # Quaternion component associated with Z-axis
    'quat_w',  # Non-axial quaternion component
    'n/a',     # Channels with no corresponding spatial axis
}

# Allowed channel types (from BIDS schema - uppercase required)
ALLOWED_CHANNEL_TYPES = {
    'POS',       # Position in space
    'ORNT',      # Orientation
    'VEL',       # Velocity
    'ACCEL',     # Accelerometer
    'GYRO',      # Gyrometer
    'ANGACCEL',  # Angular acceleration
    'MAGN',      # Magnetic field strength
    'JNTANG',    # Joint angle between bodyparts
    'LATENCY',   # Sample latency from recording onset
    'MISC',      # Miscellaneous channels
}

# Component requirements for each channel type
CHANNEL_TYPE_COMPONENT_REQUIREMENTS = {
    'POS': {'x', 'y', 'z'},                                           # Requires spatial axes
    'ORNT': {'x', 'y', 'z', 'quat_x', 'quat_y', 'quat_z', 'quat_w'}, # Requires axes or quaternions
    'VEL': {'x', 'y', 'z'},                                           # Requires spatial axes
    'ACCEL': {'x', 'y', 'z'},                                         # Requires spatial axes
    'GYRO': {'x', 'y', 'z'},                                          # Requires spatial axes
    'ANGACCEL': {'x', 'y', 'z'},                                      # Requires spatial axes
    'MAGN': {'x', 'y', 'z'},                                          # Requires spatial axes
    'JNTANG': ALLOWED_CHANNEL_COMPONENTS,                             # Can use any component
    'LATENCY': ALLOWED_CHANNEL_COMPONENTS,                            # Can use any component
    'MISC': ALLOWED_CHANNEL_COMPONENTS,                               # Can use any component
}
