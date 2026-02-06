"""
DraftWolf Control - Version control for Blender with DraftWolf.
"""

import bpy

from .constants import BL_INFO
from .state import StatusCache, status_worker
from .operators_commit import object_ot_df_commit, object_ot_df_commit_last_saved
from .operators_restore import (
    object_ot_df_retrieve,
    object_ot_df_restore_quick,
    object_ot_df_rename_version,
)
from .operators_app import (
    object_ot_df_init,
    object_ot_df_open_app,
    object_ot_df_download_app,
    object_ot_df_login,
    object_ot_df_refresh_status,
)
from .operators_version_ui import object_ot_df_toggle_versions, object_ot_df_refresh_versions
from .operators_update import object_ot_df_check_for_updates, object_ot_df_open_update_download
from .panel import df_pt_main_panel
from .constants import GITHUB_REPO
from .state import UpdateState

# Expose bl_info at package level for Blender
bl_info = BL_INFO

classes = (
    object_ot_df_commit,
    object_ot_df_commit_last_saved,
    object_ot_df_retrieve,
    object_ot_df_init,
    object_ot_df_open_app,
    object_ot_df_download_app,
    object_ot_df_login,
    object_ot_df_toggle_versions,
    object_ot_df_refresh_versions,
    object_ot_df_restore_quick,
    object_ot_df_rename_version,
    object_ot_df_refresh_status,
    object_ot_df_check_for_updates,
    object_ot_df_open_update_download,
    df_pt_main_panel,
)


def _deferred_update_check():
    """Run once after a short delay to avoid blocking startup."""
    from .constants import UPDATE_CHECK_INTERVAL
    from .update import check_for_updates
    if UPDATE_CHECK_INTERVAL > 0:
        check_for_updates()


def register():
    # Unregister first so we're idempotent (reinstall/reload won't double-register)
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    for cls in classes:
        bpy.utils.register_class(cls)
    # When update check is disabled (dummy), clear any stale update notice immediately
    if not GITHUB_REPO:
        UpdateState.update_available = False
        UpdateState.latest_version = None
        UpdateState.release_url = None
    if not StatusCache.thread_running:
        StatusCache.thread_running = True
        import threading
        StatusCache.thread = threading.Thread(target=status_worker, daemon=True)
        StatusCache.thread.start()
    # Auto-check for addon updates after 2 seconds (once per session)
    if hasattr(bpy.app, "timers") and bpy.app.timers:
        if hasattr(bpy.app.timers, "run_once"):
            bpy.app.timers.run_once(_deferred_update_check, first_interval=2.0)
        elif hasattr(bpy.app.timers, "register"):
            # Older Blender: register with first_interval; returning None runs once
            bpy.app.timers.register(_deferred_update_check, first_interval=2.0)


def unregister():
    StatusCache.thread_running = False
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
