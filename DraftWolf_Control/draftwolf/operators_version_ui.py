"""Version list UI operators (toggle, refresh)."""

import bpy

from .history import load_version_history
from .state import SafeVersionList


class object_ot_df_toggle_versions(bpy.types.Operator):
    """Toggle version history display"""
    bl_idname = "draftwolf.toggle_versions"
    bl_label = "Show/Hide Versions"

    def execute(self, context):
        SafeVersionList.show_versions = not SafeVersionList.show_versions
        return {'FINISHED'}


class object_ot_df_refresh_versions(bpy.types.Operator):
    """Refresh version history list"""
    bl_idname = "draftwolf.refresh_versions"
    bl_label = "Refresh Versions"

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'WARNING'}, "Save file first")
            return {'CANCELLED'}

        SafeVersionList.full_history = load_version_history(filepath)
        self.report({'INFO'}, f"✓ Refreshed! Found {len(SafeVersionList.full_history)} versions")
        return {'FINISHED'}
