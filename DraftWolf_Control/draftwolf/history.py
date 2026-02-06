"""Version history loading and filtering."""

import os

from .constants import VERSION_SUFFIX_PATTERN, NUMBER_SUFFIX_PATTERN
from .api import send_request
from .path_utils import get_project_root


def load_version_history(filepath):
    """Load and filter version history for the current file."""
    if not filepath:
        return []

    root = get_project_root(filepath)
    if not root:
        return []

    history = send_request('/draft/history', {'projectRoot': root})
    if not history:
        return []

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
    target_lower = target_file.lower()

    filtered_history = []
    for v in history:
        files = v.get('files', {})
        if any(os.path.basename(f_path).lower() == target_lower for f_path in files.keys()):
            filtered_history.append(v)

    return filtered_history
