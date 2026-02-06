"""Check for updates and open download page."""

import os
import sys
import subprocess

import bpy

from .constants import CURRENT_VERSION
from .state import UpdateState
from .update import (
    check_for_updates,
    version_tuple_to_string,
)


class object_ot_df_check_for_updates(bpy.types.Operator):
    """Check for a newer version of the addon"""
    bl_idname = "draftwolf.check_for_updates"
    bl_label = "Check for Updates"
    bl_options = {"REGISTER"}

    def execute(self, context):
        check_for_updates()
        if UpdateState.checking:
            return {"FINISHED"}
        if UpdateState.error_message:
            self.report(
                {"WARNING"},
                f"Could not check: {UpdateState.error_message[:60]}..."
            )
            return {"CANCELLED"}
        if UpdateState.update_available:
            self.report(
                {"INFO"},
                f"Update available: v{version_tuple_to_string(UpdateState.latest_version)}"
            )
        else:
            self.report(
                {"INFO"},
                f"You have the latest version (v{version_tuple_to_string(CURRENT_VERSION)})"
            )
        return {"FINISHED"}


class object_ot_df_open_update_download(bpy.types.Operator):
    """Open the page to download the latest version"""
    bl_idname = "draftwolf.open_update_download"
    bl_label = "Download Update"

    def execute(self, context):
        url = UpdateState.release_url
        if not url:
            # Fallback to releases list
            from .constants import GITHUB_REPO
            url = f"https://github.com/{GITHUB_REPO}/releases" if GITHUB_REPO else ""
        if not url:
            return {"CANCELLED"}
        try:
            if sys.platform == "win32":
                os.startfile(url)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
        except OSError:
            return {"CANCELLED"}
        return {"FINISHED"}
