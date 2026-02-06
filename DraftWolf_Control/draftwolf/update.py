"""
Auto-update: check for a newer addon version from GitHub releases.
"""

import json
import re
import urllib.request

from .constants import CURRENT_VERSION, GITHUB_REPO
from .state import UpdateState


def parse_version(version_str):
    """
    Convert version string to tuple for comparison.
    Accepts: "1.0.0", "v1.0.0", "1.0", "v2.1"
    Returns tuple of ints e.g. (1, 0, 0), or None if invalid.
    """
    if not version_str:
        return None
    s = str(version_str).strip().lower()
    if s.startswith("v"):
        s = s[1:]
    parts = re.findall(r"\d+", s)
    if not parts:
        return None
    return tuple(int(p) for p in parts)


def version_tuple_to_string(v):
    """(1, 0, 0) -> '1.0.0'"""
    if v is None:
        return "?"
    return ".".join(str(x) for x in v)


def is_newer(latest_tuple, current_tuple):
    """True if latest_tuple > current_tuple (e.g. (1,1,0) > (1,0,0))."""
    if not latest_tuple or not current_tuple:
        return False
    # Pad with zeros so (1,0) compares equal to (1,0,0)
    def pad(t, length=3):
        return tuple(t) + (0,) * (length - len(t))
    n = max(len(latest_tuple), len(current_tuple), 3)
    return pad(latest_tuple, n) > pad(current_tuple, n)


def fetch_latest_release():
    """
    Fetch latest release from GitHub API.
    Returns (version_tuple, release_url) or (None, None) on failure.
    """
    if not GITHUB_REPO:
        return None, None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "DraftWolf-Blender-Addon/1.0")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as e:
        UpdateState.error_message = str(e)
        return None, None

    tag_name = data.get("tag_name") or ""
    html_url = data.get("html_url") or f"https://github.com/{GITHUB_REPO}/releases"
    version_tuple = parse_version(tag_name)
    return version_tuple, html_url


def check_for_updates():
    """
    Check for updates and update UpdateState.
    Call from main thread (e.g. operator) to avoid threading issues with Blender.
    When GITHUB_REPO is None (dummy), no check is performed and any stale update notice is cleared.
    """
    UpdateState.checking = True
    UpdateState.error_message = None
    try:
        if not GITHUB_REPO:
            UpdateState.update_available = False
            UpdateState.latest_version = None
            UpdateState.release_url = None
            return
        latest_tuple, release_url = fetch_latest_release()
        import time
        UpdateState.last_check_time = time.time()
        UpdateState.release_url = release_url
        UpdateState.latest_version = latest_tuple
        UpdateState.update_available = is_newer(latest_tuple, CURRENT_VERSION)
    finally:
        UpdateState.checking = False
