"""Restore / retrieve version operators."""

import os

import bpy

from .constants import (
    CONNECTION_ERROR,
    UNKNOWN_ERROR,
    VERSION_SUFFIX_PATTERN,
    NUMBER_SUFFIX_PATTERN,
)
from .api import send_request
from .path_utils import get_project_root, recover_original_filepath
from .history import load_version_history
from .state import SafeVersionList


def _is_same_open_file(filepath, req_filepath):
    """True if filepath and req_filepath refer to the same file."""
    try:
        return os.path.samefile(filepath, req_filepath)
    except Exception:
        return os.path.normpath(filepath) == os.path.normpath(req_filepath)


def _open_mainfile_safe(filepath, on_error=None):
    """Open the mainfile; on exception call on_error(e) if provided."""
    try:
        bpy.ops.wm.open_mainfile(filepath=filepath)
    except Exception as e:
        if on_error is not None:
            on_error(e)


def _resolve_rel_path(root, filepath):
    """Resolve filepath relative to root; strip -retrieved suffix for matching. Returns None if outside root."""
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    real_filepath = filepath
    if '-retrieved' in name:
        clean_name = name
        if clean_name.endswith('-retrieved'):
            clean_name = clean_name[:-len('-retrieved')]
        if '-' in clean_name:
            parts = clean_name.rsplit('-', 1)
            if parts[-1].startswith('v') or parts[-1].replace('.', '').isdigit():
                clean_name = parts[0]
        real_filepath = os.path.join(os.path.dirname(filepath), clean_name + ext)
    try:
        root_abs = os.path.abspath(root)
        filepath_abs = os.path.abspath(real_filepath)
        if os.name == 'nt':
            if os.path.splitdrive(root_abs)[0].lower() != os.path.splitdrive(filepath_abs)[0].lower():
                filepath_abs = os.path.abspath(filepath)
        rel_path = os.path.relpath(filepath_abs, root_abs)
        return None if rel_path.startswith('..') else rel_path
    except ValueError:
        return None


def _get_clean_target_basename(filepath):
    """Return (target_file, target_lower) for matching history entries."""
    target_file = os.path.basename(filepath)
    name, ext = os.path.splitext(target_file)
    clean_name = name
    if ' retrieved version' in clean_name.lower():
        idx = clean_name.lower().find(' retrieved version')
        clean_name = clean_name[:idx]
    elif '-retrieved' in clean_name:
        clean_name = clean_name.replace('-retrieved', '')
        clean_name = VERSION_SUFFIX_PATTERN.sub('', clean_name)
        clean_name = NUMBER_SUFFIX_PATTERN.sub('', clean_name)
    target_file = clean_name + ext
    return target_file, target_file.lower()


def _filter_history_by_basename(history, target_lower):
    """Return versions that contain a file whose basename (lower) equals target_lower."""
    result = []
    for v in history:
        files = v.get('files', {})
        for f_path in files:
            if os.path.basename(f_path).lower() == target_lower:
                result.append(v)
                break
    return result


def _populate_version_dialog_items(history):
    """Fill SafeVersionList.items from history for the version selector dialog."""
    SafeVersionList.items = []
    for v in history:
        vid = v.get('id')
        vnum = v.get('versionNumber', '0')
        vlbl = v.get('label', 'Untitled')
        vtime = v.get('timestamp', '').split('T')[0]
        display_name = f"v{vnum}: {vlbl} ({vtime})"
        SafeVersionList.items.append((vid, display_name, vlbl))


class object_ot_df_retrieve(bpy.types.Operator):
    """Go back to a previous version of your work"""
    bl_idname = "draftwolf.retrieve"
    bl_label = "Restore Version"
    bl_options = {'REGISTER'}

    def get_items(self, context):
        return SafeVersionList.items

    version_enum: bpy.props.EnumProperty(items=get_items, name="Select Version")

    def execute(self, context):
        version_id = self.version_enum
        filepath = bpy.data.filepath
        if not version_id:
            return {'CANCELLED'}
        root = get_project_root(filepath)
        if not root:
            return {'CANCELLED'}

        req_filepath = recover_original_filepath(filepath)
        is_open_file = _is_same_open_file(filepath, req_filepath)
        if is_open_file:
            bpy.ops.wm.read_homefile(app_template="")

        res = send_request('/draft/restore', {
            'projectRoot': root,
            'versionId': version_id
        })
        success = res and res.get('success')
        if success:
            self.report({'INFO'}, f"Restored Version {version_id}")
            _open_mainfile_safe(req_filepath, on_error=lambda e: self.report({'ERROR'}, f"Restored but failed to open: {e}"))
        else:
            err = res.get('error', UNKNOWN_ERROR) if res else CONNECTION_ERROR
            self.report({'ERROR'}, f"Restore failed: {err}")
            if is_open_file:
                _open_mainfile_safe(req_filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "Please save your .blend file first")
            return {'CANCELLED'}
        root = get_project_root(filepath)
        if not root:
            self.report({'ERROR'}, "Version control not enabled for this project")
            return {'CANCELLED'}
        rel_path = _resolve_rel_path(root, filepath)
        if not rel_path:
            self.report({'ERROR'}, "Could not resolve file path relative to project.")
            return {'CANCELLED'}
        history = send_request('/draft/history', {'projectRoot': root})
        if history is None:
            self.report({'ERROR'}, "Could not connect to DraftWolf App.")
            return {'CANCELLED'}
        if not history:
            self.report({'WARNING'}, "No version history found.")
            return {'CANCELLED'}
        target_file, target_lower = _get_clean_target_basename(filepath)
        history = _filter_history_by_basename(history, target_lower)
        if not history:
            self.report({'WARNING'}, f"No versions found for '{target_file}'")
            return {'CANCELLED'}
        _populate_version_dialog_items(history)
        return context.window_manager.invoke_props_dialog(self)


class object_ot_df_restore_quick(bpy.types.Operator):
    """Quickly restore a specific version"""
    bl_idname = "draftwolf.restore_quick"
    bl_label = "Restore This Version"
    bl_options = {'REGISTER'}

    version_id: bpy.props.StringProperty()

    def execute(self, context):
        filepath = bpy.data.filepath
        if not self.version_id:
            return {'CANCELLED'}
        root = get_project_root(filepath)
        if not root:
            return {'CANCELLED'}
        req_filepath = recover_original_filepath(filepath)
        is_open_file = _is_same_open_file(filepath, req_filepath)
        if is_open_file:
            bpy.ops.wm.read_homefile(app_template="")
        res = send_request('/draft/restore', {
            'projectRoot': root,
            'versionId': self.version_id
        })
        success = res and res.get('success')
        if success:
            self.report({'INFO'}, "✓ Version restored successfully")
            _open_mainfile_safe(req_filepath, on_error=lambda e: self.report({'ERROR'}, f"Restored but failed to open: {e}"))
        else:
            err = res.get('error', UNKNOWN_ERROR) if res else CONNECTION_ERROR
            self.report({'ERROR'}, f"Restore failed: {err}")
            if is_open_file:
                _open_mainfile_safe(req_filepath)
        return {'FINISHED'}


class object_ot_df_rename_version(bpy.types.Operator):
    """Rename a version's label"""
    bl_idname = "draftwolf.rename_version"
    bl_label = "Rename Version"
    bl_options = {'REGISTER', 'UNDO'}

    version_id: bpy.props.StringProperty(options={'HIDDEN'})
    new_label: bpy.props.StringProperty(name="New Label", default="")

    def execute(self, context):
        filepath = bpy.data.filepath
        if not self.version_id or not self.new_label.strip():
            return {'CANCELLED'}

        root = get_project_root(filepath)
        if not root:
            return {'CANCELLED'}

        res = send_request('/draft/rename-version', {
            'projectRoot': root,
            'versionId': self.version_id,
            'newLabel': self.new_label.strip()
        })

        if res and res.get('success'):
            self.report({'INFO'}, "✓ Version renamed successfully")
            SafeVersionList.full_history = load_version_history(filepath)
        else:
            err = res.get('error', UNKNOWN_ERROR) if res else CONNECTION_ERROR
            self.report({'ERROR'}, f"Rename failed: {err}")

        return {'FINISHED'}

    def invoke(self, context, event):
        history = SafeVersionList.full_history or []
        for v in history:
            if v.get('id') == self.version_id:
                self.new_label = v.get('label', 'Untitled')
                break
        return context.window_manager.invoke_props_dialog(self)
