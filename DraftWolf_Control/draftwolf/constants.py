"""Addon metadata and shared constants."""

import re

# Addon metadata (also used by __init__.py for bl_info)
BL_INFO = {
    "name": "DraftWolf Control",
    "author": "DraftWolf",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > DraftWolf",
    "description": "Version control for Blender with DraftWolf",
    "category": "Development",
}

# Current addon version (must match BL_INFO["version"])
CURRENT_VERSION = BL_INFO["version"]

# Auto-update: GitHub repo "owner/repo" for releases
# Set to None to disable update check (dummy for now - addon will be from another repo)
GITHUB_REPO = None
# How often to check for updates (seconds); 0 = only when user clicks "Check for updates"
UPDATE_CHECK_INTERVAL = 0

API_PORT = 45000
API_URL = f"http://127.0.0.1:{API_PORT}"

# Error message literals (avoid duplication for linter)
UNKNOWN_ERROR = "Unknown Error"
CONNECTION_ERROR = "Connection Error"
CANNOT_CONNECT_APP = "Cannot connect to DraftWolf App"

# Pre-compile regex patterns for performance
VERSION_SUFFIX_PATTERN = re.compile(r'-v[\d\.]+$')
NUMBER_SUFFIX_PATTERN = re.compile(r'-\d+$')
