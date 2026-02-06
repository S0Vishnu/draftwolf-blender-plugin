"""Global state, caches, and background status worker."""

import time
import threading

from .api import send_request


class SafeVersionList:
    """UI state for version history list."""
    items = []
    full_history = None
    show_versions = False
    last_fetch_time = 0
    fetch_interval = 10.0
    current_filepath = None


class StatusCache:
    """Shared state updated by background thread."""
    app_running = False
    is_logged_in = False
    username = None
    thread_running = False
    thread = None
    last_draw_time = 0
    cached_is_saved = False
    cached_is_initialized = False
    cached_filepath = None


class RootCache:
    """Cache for project root discovery."""
    cache = {}
    duration = 30.0


class UpdateState:
    """State for addon auto-update check."""
    latest_version = None   # tuple e.g. (1, 1, 0) or None
    release_url = None     # URL to download / releases page
    update_available = False
    last_check_time = 0.0
    checking = False       # True while a check is in progress
    error_message = None   # Set if last check failed


def check_app_status():
    """Return latest known app status from background thread."""
    return StatusCache.app_running


def check_login_status():
    """Return latest known login status from background thread."""
    return StatusCache.is_logged_in, StatusCache.username


def _truncate_username(uname: str, max_display: int = 15) -> str:
    """Return username truncated for display if too long."""
    if len(uname) <= max_display:
        return uname
    return uname[:12] + "..."


def _apply_auth_status(auth_res):
    """Update StatusCache from auth/status response. Call when app is running."""
    if not auth_res:
        StatusCache.is_logged_in = False
        StatusCache.username = None
        return
    # Accept both camelCase (loggedIn) and snake_case (logged_in); treat username as logged-in hint
    logged_in = auth_res.get('loggedIn', auth_res.get('logged_in', False))
    if not logged_in and auth_res.get('username'):
        # App may send username without loggedIn when session is valid
        logged_in = True
    if not logged_in:
        StatusCache.is_logged_in = False
        StatusCache.username = None
        return
    StatusCache.is_logged_in = True
    StatusCache.username = _truncate_username(auth_res.get('username', 'User'))


def _sleep_while_running(seconds: float, step: float = 0.1) -> None:
    """Sleep in steps until seconds elapsed or thread_running becomes False."""
    steps = max(0, int(seconds / step))
    for _ in range(steps):
        if not StatusCache.thread_running:
            break
        time.sleep(step)


def status_worker():
    """Background thread that polls app and login status."""
    while StatusCache.thread_running:
        try:
            res = send_request('/health')
            is_running = bool(res and res.get('success'))
            StatusCache.app_running = is_running

            if is_running:
                _apply_auth_status(send_request('/auth/status'))
            else:
                StatusCache.is_logged_in = False
                StatusCache.username = None

        except Exception as e:
            print(f"Background check failed: {e}")
            StatusCache.app_running = False

        _sleep_while_running(5.0)


def run_once_sync_status():
    """One-off health + auth/status check; updates StatusCache. Safe to call from main thread (e.g. Blender timer)."""
    try:
        res = send_request('/health')
        is_running = bool(res and res.get('success'))
        StatusCache.app_running = is_running
        if is_running:
            _apply_auth_status(send_request('/auth/status'))
        else:
            StatusCache.is_logged_in = False
            StatusCache.username = None
    except Exception as e:
        print(f"DraftWolf one-off sync failed: {e}")
        StatusCache.app_running = False
