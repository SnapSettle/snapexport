# SnapExport 🚀

SnapExport is an extension for **Inkscape** designed to streamline asset production pipelines. It allows designers to simultaneously export active compositions into multiple standard production and vector formats with a single click.

Instead of sequentially clicking through multiple export paths, menus, and configurations, SnapExport aggregates your targets into a clean user interface panel right inside Inkscape and processes them in parallel.
## ✨ Features

- **Multi-Format Matrix Export**: Output to `PNG`, `JPEG`, `PDF`, and `EPS` simultaneously.
- **Multiple SVG Compilation Variants**:
  - `Plain SVG`: Strips editor metadata for universal web components.
  - `Inkscape SVG`: Retains editable node structures and layers.
  - `Optimized SVG`: Compiles highly compressed outputs using Scour processing pipelines.
- **Clean Indented Interface**: Visual alignment flags group sub-options naturally without adding complex, bulky nested UI tabs.
- **Dynamic File Auto-Naming**: If multiple SVG variations are exported at the same time, suffixes (e.g., `_optimized`, `_plain`) are gracefully appended to ensure no outputs overlap.
- **Formatted Status Dashboard**: Replaces standard diagnostic message footnotes with a clean, well-aligned typographical block report listing generated totals, active targets, and sequential counters.
- **Native Preview Supression**: Prevents runtime performance lagging by skipping live canvas rerendering tasks.

## 🛠️ Project Architecture

```text
.
├── flake.nix          # Nix environment expression (LSP, dependencies, formatting)
├── snapexport.inx     # Inkscape Extension XML graphical user interface layout
└── snapexport.py      # Extension processing engine orchestrating Inkscape CLI commands

```

## 🚀 Installation

### 1. Locate your Inkscape User Extensions Directory

Open Inkscape and navigate to **Edit ➔ Preferences ➔ System ➔ User extensions**.

Alternatively, navigate there directly via your system file manager:

* **Windows**: `%APPDATA%\inkscape\extensions`
* **macOS**: `~/Library/Application Support/inkscape/extensions`
* **Linux**: `~/.config/inkscape/extensions`

### 2. Copy the Files

Clone this repository or download the files, then place both `snapexport.inx` and `snapexport.py` directly inside that folder:

```bash
cd ~/.config/inkscape/extensions/
git clone https://github.com/snapsettle/snapexport.git
```

OR

```bash
cd ~/Downloads/snapexport
cp snapexport.inx snapexport.py ~/.config/inkscape/extensions/
```

### 3. Restart Inkscape

Completely close and reopen Inkscape. The tool will be loaded and visible in the top system menu under **Extensions ➔ Export ➔ SnapExport**.

## 💻 Development Environment (Nix)

This project features a fully reproducible developmental environment configured via flakes. It wraps Python dependencies (`inkex`), an LSP server for semantic diagnostics (`pyright`), and automated code formatters (`treefmt` running `black` and `xmlstarlet`).

### To spin up the shell & load LSP assistance:

```bash
nix develop
```

### To automatically format Python, XML, and Nix code files:

```bash
nix fmt
```

## 📝 Usage Guide

1. Create or open your artwork inside Inkscape.
2. Navigate to **Extensions ➔ Export ➔ SnapExport**.
3. Choose your targeted output directory path and define your asset's **Base Filename**.
4. Check or uncheck your preferred delivery formats.
5. Hit **Apply**. A clean dashboard window will popup reporting your successfully compiled items.

## 📜 Commit Guidelines

This project utilizes the **Conventional Commits** specification. Please structure commit modifications using descriptive scopes:

* `feat(inx): ...` - New features or additions to user parameters.
* `fix(engine): ...` - Bug patches related to compilation loops or formatting streams.
* `style(python): ...` - White-space corrections, syntax cleanups, or code formatting.
* `chore(nix): ...` - Package version overrides or channel adjustments inside flakes.
