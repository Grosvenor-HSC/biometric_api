# biometric_api/env.py
import os

def env(key: str, default=None):
    """
    Get an environment variable value or a default.
    This wraps os.getenv and trims whitespace.
    """
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip()
