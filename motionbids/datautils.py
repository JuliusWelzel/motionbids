"""
Utility functions for data processing and validation.
"""
import re


def _is_pascal_case(s: str) -> bool:
    """
    Check if a string is in PascalCase.
    
    PascalCase starts with an uppercase letter and contains no underscores,
    hyphens, or spaces. Each word starts with an uppercase letter.
    
    Args:
        s: String to check
        
    Returns:
        True if the string is in PascalCase, False otherwise
    """
    if not s:
        return False
    # PascalCase: starts with uppercase, no underscores/hyphens/spaces,
    # only letters and digits allowed
    return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', s))
