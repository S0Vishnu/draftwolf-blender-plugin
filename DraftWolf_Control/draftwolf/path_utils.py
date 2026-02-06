"""Path and filepath helpers for version recovery and project root."""

import os
import time

from .api import send_request
from .state import RootCache


def recover_original_filepath(filepath):
    """
    Recover the original filepath from a retrieved version file.
    """
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)

    if name.endswith('-retrieved-version') or '-retrieved-version-' in name:
        split_key = '-retrieved-version'
        if split_key in name:
            original_name_part = name.split(split_key)[0]
            return os.path.join(os.path.dirname(filepath), original_name_part + ext)
    elif name.endswith('-retrieved'):
        temp = name[:-len('-retrieved')]
        if '-' in temp:
            original_name_part = temp.rsplit('-', 1)[0]
            return os.path.join(os.path.dirname(filepath), original_name_part + ext)

    return filepath


def get_project_root(filepath):
    if not filepath:
        return None

    dir_path = os.path.dirname(filepath)
    current_time = time.time()

    if dir_path in RootCache.cache:
        entry = RootCache.cache[dir_path]
        if current_time - entry['time'] < RootCache.duration:
            return entry['root']

    res = send_request('/draft/find-root', {'path': dir_path})
    root = res.get('root') if res else None
    RootCache.cache[dir_path] = {'root': root, 'time': current_time}

    return root
