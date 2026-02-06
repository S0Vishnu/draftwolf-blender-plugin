"""Commit / save version operators."""

import bpy

from .api import send_request
from .constants import CANNOT_CONNECT_APP, UNKNOWN_ERROR
from .path_utils import get_project_root
from .history import load_version_history
from .state import SafeVersionList


class object_ot_df_commit(bpy.types.Operator):
    """Save your current work as a new version (like a checkpoint)"""
    bl_idname = "draftwolf.commit"
    bl_label = "Save Version"
    bl_options = {'REGISTER', 'UNDO'}

    label_input: bpy.props.StringProperty(name="Label", default="New Version")

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "Please save your .blend file first (File > Save As)")
            return {'CANCELLED'}

        bpy.ops.wm.save_mainfile()

        root = get_project_root(filepath)
        if not root:
            self.report({'ERROR'}, "Version control not enabled. Click 'Enable Version Control' first.")
            return {'CANCELLED'}

        res = send_request('/draft/commit', {
            'projectRoot': root,
            'label': self.label_input,
            'files': [filepath]
        })

        if res and res.get('success'):
            self.report({'INFO'}, f"✓ Version saved successfully! (v{res.get('versionNumber', '?')})")
            SafeVersionList.full_history = load_version_history(filepath)
        else:
            err = res.get('error', UNKNOWN_ERROR) if res else CANNOT_CONNECT_APP
            self.report({'ERROR'}, f"Failed to save: {err}")

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class object_ot_df_commit_last_saved(bpy.types.Operator):
    """Save version of the last saved state (without current unsaved changes)"""
    bl_idname = "draftwolf.commit_last_saved"
    bl_label = "Save Last Saved as Version"
    bl_options = {'REGISTER', 'UNDO'}

    label_input: bpy.props.StringProperty(name="Label", default="New Version")

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "Please save your .blend file first (File > Save As)")
            return {'CANCELLED'}

        root = get_project_root(filepath)
        if not root:
            self.report({'ERROR'}, "Version control not enabled. Click 'Enable Version Control' first.")
            return {'CANCELLED'}

        res = send_request('/draft/commit', {
            'projectRoot': root,
            'label': self.label_input,
            'files': [filepath]
        })

        if res and res.get('success'):
            self.report({'INFO'}, f"✓ Last saved state versioned! (v{res.get('versionNumber', '?')})")
            SafeVersionList.full_history = load_version_history(filepath)
        else:
            err = res.get('error', UNKNOWN_ERROR) if res else CANNOT_CONNECT_APP
            self.report({'ERROR'}, f"Failed to save: {err}")

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
