"""Detect whether the DraftWolf app is installed (e.g. URL protocol or install path)."""

import os
import sys
import time

# URL scheme the app registers (used by open_app and login operators)
PROTOCOL_SCHEME = "myapp"

_install_cache = None
_install_cache_time = 0.0
CACHE_TTL = 90.0


def _is_app_installed_win():
    """Check Windows: myapp URL protocol registered."""
    try:
        import winreg
        # HKCU\Software\Classes\myapp (user install) or HKCR\myapp (machine install)
        checks = [
            (winreg.HKEY_CURRENT_USER, "Software\\Classes\\" + PROTOCOL_SCHEME),
            (winreg.HKEY_CLASSES_ROOT, PROTOCOL_SCHEME),
        ]
        for root, subkey in checks:
            try:
                key = winreg.OpenKey(root, subkey, 0, winreg.KEY_READ)
                winreg.CloseKey(key)
                return True
            except OSError:
                continue
    except ImportError:
        pass
    return False


def _is_app_installed_darwin():
    """Check macOS: DraftWolf app bundle in /Applications."""
    app_names = ("DraftWolf.app", "Draftwolf.app", "Draftflow.app")
    for name in app_names:
        if os.path.isdir(os.path.join("/Applications", name)):
            return True
    return False


def _is_app_installed_linux():
    """Linux: treat as unknown; assume installed so we show 'App not running' not 'not installed'."""
    return True


def is_app_installed():
    """Return True if DraftWolf appears to be installed (protocol or app path). Uses a short TTL cache."""
    global _install_cache, _install_cache_time
    now = time.time()
    if _install_cache is not None and (now - _install_cache_time) < CACHE_TTL:
        return _install_cache
    if sys.platform == "win32":
        result = _is_app_installed_win()
    elif sys.platform == "darwin":
        result = _is_app_installed_darwin()
    else:
        result = _is_app_installed_linux()
    _install_cache = result
    _install_cache_time = now
    return result
