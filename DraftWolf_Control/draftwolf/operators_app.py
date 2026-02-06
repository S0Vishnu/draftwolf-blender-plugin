"""App / init / login / download operators."""

import os
import sys
import subprocess
import urllib.request

import bpy

from .api import send_request
from .constants import CANNOT_CONNECT_APP, UNKNOWN_ERROR
from .path_utils import get_project_root
from .state import StatusCache
from .app_detection import is_app_installed


class object_ot_df_init(bpy.types.Operator):
    """Enable version control for this project (one-time setup)"""
    bl_idname = "draftwolf.init"
    bl_label = "Enable Version Control"
    bl_options = {'REGISTER'}

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "Please save your .blend file first (File > Save As)")
            return {'CANCELLED'}

        directory = os.path.dirname(filepath)
        res = send_request('/draft/init', {'projectRoot': directory})
        if res and res.get('success'):
            self.report({'INFO'}, "✓ Version control enabled! You can now save versions.")
        else:
            err = res.get('error', UNKNOWN_ERROR) if res else CANNOT_CONNECT_APP
            self.report({'ERROR'}, f"Setup failed: {err}")

        return {'FINISHED'}


class object_ot_df_open_app(bpy.types.Operator):
    """Open the DraftWolf app to view full version history and manage projects"""
    bl_idname = "draftwolf.open_app"
    bl_label = "Open DraftWolf App"

    def execute(self, context):
        try:
            filepath = bpy.data.filepath
            url = "myapp://open"
            if filepath:
                safe_path = urllib.request.pathname2url(filepath)
                url += f"?path={safe_path}"

            if sys.platform == 'win32':
                os.startfile(url)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', url])
            else:
                subprocess.Popen(['xdg-open', url])

        except Exception as e:
            self.report({'ERROR'}, f"Failed to open app: {e}")

        return {'FINISHED'}


class object_ot_df_download_app(bpy.types.Operator):
    """Download DraftWolf application"""
    bl_idname = "draftwolf.download_app"
    bl_label = "Download DraftWolf"

    def execute(self, context):
        try:
            url = "https://github.com/S0Vishnu/Draftflow"
            if sys.platform == 'win32':
                os.startfile(url)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', url])
            else:
                subprocess.Popen(['xdg-open', url])
            self.report({'INFO'}, "Opening download page...")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open download page: {e}")

        return {'FINISHED'}


class object_ot_df_login(bpy.types.Operator):
    """Open DraftWolf app to login"""
    bl_idname = "draftwolf.login"
    bl_label = "Login to DraftWolf"

    def execute(self, context):
        try:
            url = "myapp://login"
            if sys.platform == 'win32':
                os.startfile(url)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', url])
            else:
                subprocess.Popen(['xdg-open', url])
            self.report({'INFO'}, "Opening DraftWolf to login...")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open login: {e}")

        return {'FINISHED'}


class object_ot_df_refresh_status(bpy.types.Operator):
    """Refresh connection status with DraftWolf app"""
    bl_idname = "draftwolf.refresh_status"
    bl_label = "Refresh Status"

    def execute(self, context):
        app_running = StatusCache.app_running
        is_logged_in = StatusCache.is_logged_in
        username = StatusCache.username

        if app_running:
            if is_logged_in:
                self.report({'INFO'}, f"✓ Connected! Logged in as {username}")
            else:
                self.report({'INFO'}, "✓ App detected but not logged in")
        else:
            if is_app_installed():
                self.report({'WARNING'}, "App not running. Make sure DraftWolf is running.")
            else:
                self.report({'WARNING'}, "App not installed. Download DraftWolf to connect.")

        return {'FINISHED'}
