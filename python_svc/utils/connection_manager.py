"""
Connection Management Utilities
===============================
This module provides connection type definitions for data pipelines.
"""

# Connection Types
CONNECTION_TYPES = {
    'input_sor': 'Flat Files',
    'target_db': 'Destination Databases',
    'api_source': 'API Source Feed'
}


def get_connection_types():
    """Return available connection types."""
    return CONNECTION_TYPES.copy()