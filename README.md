# DraftWolf Control — Blender Add-on

Version control for Blender with [DraftWolf](https://draftwolf.vercel.app). Commit, restore, and manage versions of your Blender projects from the 3D Viewport sidebar.

## Requirements

- **Blender** 2.80 or newer  
- **DraftWolf desktop app** running locally (default port: `45000`). The add-on talks to the app over HTTP for version history and sync.

## Installation

### Option A: Install the folder addon (recommended)

1. Zip the **`DraftWolf_Control`** folder (it must contain `DraftWolf_Control/__init__.py` and `DraftWolf_Control/draftwolf/` with all package files).
2. In Blender: **Edit → Preferences → Add-ons → Install…** and select the zip.
3. Enable **DraftWolf Control** in the add-ons list.

### Option B: Single-file launcher

1. Copy **`draftwolf_addon.py`** and the **`draftwolf`** package folder into the same directory (e.g. your Blender scripts addons folder).
2. In Blender: **Edit → Preferences → Add-ons → Install…** and select `draftwolf_addon.py`.
3. Enable **DraftWolf Control**.

## Where to find it

- **Location:** **View3D → Sidebar (N) → DraftWolf** tab.

## Features

- **Getting started** — Save your `.blend` file, then **Enable Version Control** for the project.
- **Commit** — Save & create a version; optional “Commit last saved” for the current file state.
- **Restore** — Restore a previous version or retrieve a specific version.
- **Manage versions** — Expand/collapse version list, refresh, quick restore, rename versions.
- **DraftWolf app** — Open app, download app, login; status and login state shown in the panel.
- **Updates** — Check for add-on updates and open the download page when available.

## Project layout

```
aadons/
├── README.md                 # This file
├── draftwolf_addon.py        # Single-file launcher (alternative install)
└── DraftWolf_Control/        # Folder addon (zip this to install)
    ├── __init__.py           # Addon entry point
    └── draftwolf/            # Main package
        ├── __init__.py       # Registration, bl_info
        ├── api.py            # HTTP client for DraftWolf local server
        ├── constants.py      # Port, URLs, bl_info
        ├── state.py          # Status cache, update state
        ├── history.py        # Version history loading
        ├── path_utils.py     # Project root resolution
        ├── panel.py          # Sidebar UI
        ├── operators_*.py    # Commit, restore, app, version UI, update
        ├── update.py         # Update check logic
        └── blender_manifest.toml  # Addon manifest (Blender 4.2+)
```

## License

GPL-2.0-or-later. See `blender_manifest.toml` in `DraftWolf_Control/draftwolf/` for details.

## Maintainer

S0Vishnu — vishnus.connect@gmail.com
