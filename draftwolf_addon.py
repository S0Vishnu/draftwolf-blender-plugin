# DraftWolf Control - Single-file launcher (alternative install)
# Prefer installing the folder addon: zip "DraftWolf_Control" (contains __init__.py + draftwolf/)
# and use Blender Edit > Preferences > Add-ons > Install from file.
# Or install this .py and place the "draftwolf" folder in the same directory as this file.

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
    """Ensure the directory containing this addon (and the draftwolf package) is on sys.path."""
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    if addon_dir not in sys.path:
        sys.path.insert(0, addon_dir)

def register():
    _ensure_draftwolf_on_path()
    from draftwolf import register as _register
    _register()

def unregister():
    _ensure_draftwolf_on_path()
    from draftwolf import unregister as _unregister
    _unregister()

if __name__ == "__main__":
    register()
