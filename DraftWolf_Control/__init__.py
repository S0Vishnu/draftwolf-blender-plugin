# DraftWolf Control - Folder addon launcher
# Install by zipping this folder (DraftWolf_Control) and use Blender's Install from file.
# The zip must contain: DraftWolf_Control/__init__.py and DraftWolf_Control/draftwolf/ (with all package files).

import os
import sys

bl_info = {
    "name": "DraftWolf Control",
    "author": "DraftWolf",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > DraftWolf",
    "description": "Version control for Blender with DraftWolf",
    "category": "Development",
}

def _ensure_draftwolf_on_path():
    """Ensure the addon directory (containing the draftwolf package) is on sys.path."""
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    if addon_dir not in sys.path:
        sys.path.insert(0, addon_dir)

def register():
    _ensure_draftwolf_on_path()
    from draftwolf import register as _register
    _register()

def unregister():
    from draftwolf import unregister as _unregister
    _unregister()

if __name__ == "__main__":
    register()
