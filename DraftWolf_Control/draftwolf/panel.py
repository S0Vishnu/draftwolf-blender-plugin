"""Main sidebar panel UI."""

import time

import bpy

from .path_utils import get_project_root
from .state import SafeVersionList, StatusCache, UpdateState, check_app_status, check_login_status
from .app_detection import is_app_installed
from .history import load_version_history
from .update import version_tuple_to_string
from .constants import CURRENT_VERSION


def _get_cached_status():
    """Return (current_time, filepath, is_saved, is_initialized)."""
    current_time = time.time()
    filepath = bpy.data.filepath
    if (current_time - StatusCache.last_draw_time < 0.5 and
            StatusCache.cached_filepath == filepath):
        return current_time, filepath, StatusCache.cached_is_saved, StatusCache.cached_is_initialized
    is_saved = bool(filepath)
    is_initialized = bool(get_project_root(filepath)) if is_saved else False
    StatusCache.last_draw_time = current_time
    StatusCache.cached_is_saved = is_saved
    StatusCache.cached_is_initialized = is_initialized
    StatusCache.cached_filepath = filepath
    return current_time, filepath, is_saved, is_initialized


def _draw_update_notice(layout):
    """Draw update-available box if applicable."""
    if not (UpdateState.update_available and UpdateState.latest_version):
        return
    update_box = layout.box()
    row = update_box.row(align=True)
    row.alert = True
    row.label(
        text=f"Update available: v{version_tuple_to_string(UpdateState.latest_version)}",
        icon="SORT_DESC",
    )
    row = update_box.row(align=True)
    row.operator("draftwolf.open_update_download", text="Download", icon="EXPORT")
    row.operator("draftwolf.check_for_updates", text="", icon="FILE_REFRESH")


def _draw_login_status(layout, app_running, is_logged_in, username):
    """Draw logged-in status box when app is running and user is logged in."""
    if not (app_running and is_logged_in):
        return
    status_box = layout.box()
    row = status_box.row()
    row.label(text=f"✓ Logged in as: {username}", icon='USER')


def _draw_getting_started(layout, is_saved, is_initialized):
    """Draw Step ① Getting Started box."""
    box = layout.box()
    box.label(text="① Getting Started", icon='INFO')
    if not is_saved:
        box.label(text="Save your .blend file first", icon='ERROR')
        box.operator("wm.save_as_mainfile", text="Save File", icon='FILE_TICK')
        return
    if not is_initialized:
        box.label(text="Enable version control for this project")
        row = box.row(align=True)
        row.scale_y = 1.2
        row.operator("draftwolf.init", text="Enable Version Control", icon="CHECKMARK")
        return
    box.label(text="✓ Project Ready", icon='CHECKMARK')


def _draw_versions_commit_row(box):
    """Draw commit / save version row in Manage Versions."""
    if bpy.data.is_dirty:
        box.label(text="Unsaved changes detected:", icon='ERROR')
        row = box.row(align=True)
        row.scale_y = 1.2
        row.operator("draftwolf.commit", text="Save & Create Version", icon="FILE_TICK")
        row = box.row(align=True)
        row.scale_y = 1.0
        row.operator("draftwolf.commit_last_saved", text="Version Last Saved Only", icon="DISK_DRIVE")
    else:
        row = box.row(align=True)
        row.scale_y = 1.3
        row.operator("draftwolf.commit", text="Save Version", icon="EXPORT")


def _update_history_cache_if_needed(filepath, current_time):
    """Update SafeVersionList cache when filepath changes or interval elapsed."""
    if filepath != SafeVersionList.current_filepath:
        SafeVersionList.current_filepath = filepath
        SafeVersionList.full_history = None
    if (SafeVersionList.full_history is None and SafeVersionList.show_versions and
            current_time - SafeVersionList.last_fetch_time > SafeVersionList.fetch_interval):
        SafeVersionList.last_fetch_time = current_time
        SafeVersionList.full_history = load_version_history(filepath)


def _draw_versions_history_ui(box):
    """Draw version history toggle row and list."""
    count = len(SafeVersionList.full_history) if SafeVersionList.full_history else 0
    icon = 'DOWNARROW_HLT' if SafeVersionList.show_versions else 'RIGHTARROW'
    row = box.row(align=True)
    row.operator("draftwolf.toggle_versions",
                 text=f"Version History ({count} saved)",
                 icon=icon, emboss=False)
    row.operator("draftwolf.refresh_versions", text="", icon="FILE_REFRESH")
    if not (SafeVersionList.show_versions and SafeVersionList.full_history):
        return
    version_box = box.box()
    for v in SafeVersionList.full_history[:10]:
        vid = v.get('id')
        vlbl = v.get('label', 'Untitled')
        vtime = v.get('timestamp', '').split('T')[0]
        row = version_box.row(align=True)
        row.label(text=f"{vlbl} ({vtime})", icon='FILE')
        rename_op = row.operator("draftwolf.rename_version", text="", icon="GREASEPENCIL")
        rename_op.version_id = vid
        restore_op = row.operator("draftwolf.restore_quick", text="", icon="LOOP_BACK")
        restore_op.version_id = vid
    if len(SafeVersionList.full_history) > 10:
        version_box.label(text=f"+ {len(SafeVersionList.full_history) - 10} more versions")


def _draw_manage_versions(layout, is_initialized, filepath, current_time):
    """Draw Step ② Manage Versions box."""
    box = layout.box()
    box.label(text="② Manage Versions", icon='FILE_FOLDER')
    if not is_initialized:
        box.enabled = False
        box.label(text="Complete Step ① first", icon='INFO')
        return
    _draw_versions_commit_row(box)
    _update_history_cache_if_needed(filepath, current_time)
    _draw_versions_history_ui(box)


def _draw_app_section(layout, app_running, is_logged_in):
    """Draw Step ③ DraftWolf App box."""
    box = layout.box()
    row = box.row(align=True)
    row.label(text="③ DraftWolf App", icon='WINDOW')
    row.operator("draftwolf.refresh_status", text="", icon="FILE_REFRESH")
    row.operator("draftwolf.check_for_updates", text="", icon="WORLD")
    if not app_running:
        installed = is_app_installed()
        if not installed:
            box.label(text="App not installed", icon='ERROR')
            box.label(text="Install DraftWolf to connect")
            row = box.row(align=True)
            row.scale_y = 1.2
            row.operator("draftwolf.download_app", text="Download App", icon="INTERNET")
        else:
            box.label(text="App not running", icon='ERROR')
            box.label(text="Make sure DraftWolf is running")
            row = box.row(align=True)
            row.scale_y = 1.2
            row.operator("draftwolf.open_app", text="Open DraftWolf", icon="URL")
        return
    if not is_logged_in:
        box.label(text="Please login to continue", icon='INFO')
        row = box.row(align=True)
        row.scale_y = 1.2
        row.operator("draftwolf.login", text="Login to DraftWolf", icon="USER")
        return
    row = box.row(align=True)
    row.scale_y = 1.2
    row.operator("draftwolf.open_app", text="Open DraftWolf App", icon="URL")


class df_pt_main_panel(bpy.types.Panel):
    bl_label = "DraftWolf"
    bl_idname = "DF_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DraftWolf'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        current_time, filepath, is_saved, is_initialized = _get_cached_status()
        app_running = check_app_status()
        is_logged_in, username = check_login_status()

        _draw_update_notice(layout)
        _draw_login_status(layout, app_running, is_logged_in, username)
        _draw_getting_started(layout, is_saved, is_initialized)
        _draw_manage_versions(layout, is_initialized, filepath, current_time)
        _draw_app_section(layout, app_running, is_logged_in)
