# OpenSkin Lab

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4.svg)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Experimental%20Windows%20UI%20Lab-orange.svg)](#project-status)

**OpenSkin Lab** is a Python desktop tool for experimenting with Windows window-frame styling. It lets you compose, preview, save, import, export, and apply themed title-bar/window-frame looks using Windows DWM attributes such as caption color, title text color, border color, corner preference, dark mode, and backdrop material.

The project is designed as a practical Windows customization lab: part theme studio, part accessibility checker, part target-window manager, and part research playground for safer Windows UI experiments.

---

## ✨ Features

### Skin Studio

- Create custom window-frame themes.
- Edit caption color, title text color, border color, dark mode, corner style, and backdrop style.
- Choose from built-in profiles:
  - **Research blue**
  - **Signal green**
  - **Paper light**
  - **High contrast**
  - **Soft graphite**
- Generate accessible palettes automatically.
- Mutate palettes into new variations.
- Auto-select readable title text colors.
- Derive matching border colors.
- Preview the theme before applying it.
- Copy a clean theme summary to the clipboard.

### Profiles

- Save your own profiles locally.
- Load, delete, import, and export profiles as JSON.
- Share profile packs between machines.
- Built-in profiles are protected from accidental deletion.

### Experiments

- Generate multiple experimental theme variants from the current palette.
- Compare caption, text, border, contrast, dark/light mode, and backdrop choices.
- Apply an experiment to the composer.
- Save selected experiments as reusable profiles.
- Copy experiment summaries for documentation or sharing.

### Target Window Control

- Refresh and inspect visible titled windows.
- Target:
  - selected windows
  - active foreground window
  - all visible windows
  - windows matching title text
  - saved favourite target rules
- View title, process, PID, class name, HWND, and path where available.
- Save favourite targeting rules.
- Preview which windows will be affected before applying.
- Broad-apply confirmation helps prevent accidental mass changes.

### Apply, Live Apply, and Undo

- Apply a skin once to selected targets.
- Optional live apply mode for iterative tweaking.
- Undo the most recent apply operation.
- Store a small undo history.
- Cache repeated live-apply states to avoid unnecessary API calls.
- Record recent apply results for diagnostics.

### Accessibility

- Calculates caption/text contrast ratio.
- Uses **4.5:1** as the normal text contrast target.
- Can auto-fix title text colour for better contrast.
- Includes a high-contrast built-in profile.
- Encourages readable palettes instead of purely aesthetic colours.

### Research and Learning

- Built-in research links for:
  - DWM window attributes
  - Windows title bar customization
  - `SetWindowTextW`
  - WCAG contrast guidance
- Built-in video-search library for:
  - Windows UI customization
  - Win32 window handles
  - DWM title-bar colours
  - Mica and Acrylic materials
  - Tkinter UI layout
  - accessibility
  - UX research
  - performance/debugging

### Diagnostics

- Log tab for runtime messages.
- Run diagnostics.
- Copy log.
- Save log.
- Clear log.
- Records apply successes and failures.

---

## 🖥️ Platform Support

OpenSkin Lab is focused on **Windows**.

| Platform | Support |
|---|---|
| Windows 11 | Recommended |
| Windows 10 | Partial / depends on DWM attribute support |
| macOS | Not supported for applying skins |
| Linux | Not supported for applying skins |

The app uses Windows APIs through Python `ctypes`, including DWM and Win32 window functions. Non-Windows systems may be able to open parts of the interface, but applying skins is Windows-only.

For full title-bar colour, corner, border, dark-mode, and backdrop behaviour, Windows 11 is recommended because several DWM styling attributes are Windows 11-era APIs.

---

## ⚠️ Important Limitations

OpenSkin Lab works with public Windows window-management APIs. Some visual ideas are shown as previews or metadata because Windows does not provide a safe public API for every kind of non-client-area modification.

Currently limited/experimental areas include:

- Replacing another app’s actual caption-button glyphs.
- Injecting arbitrary texture artwork into another app’s title bar.
- Applying every visual option to every app equally.
- Styling elevated/admin apps from a non-elevated OpenSkin session.
- Styling apps that custom-draw their own title bars.
- Styling hidden, cloaked, tool, or hung windows.

The app tries to avoid unsafe targeting by filtering unsuitable windows and asking for confirmation before broad apply operations.

---

## 🚀 Getting Started

### Prerequisites

- Windows 10 or Windows 11
- Python 3.10 or newer recommended
- Tkinter available in your Python installation

OpenSkin Lab currently uses Python standard-library modules such as:

- `tkinter`
- `ctypes`
- `json`
- `pathlib`
- `colorsys`
- `webbrowser`
- `dataclasses`

No external Python package is required for the current single-file version.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/kai9987kai/OpenSkin.git
cd OpenSkin
```

Run the app:

```bash
python Main.py
```

On Windows, you can also try:

```bash
py Main.py
```

---

## Basic Usage

1. Open **OpenSkin Lab**.
2. Go to **Skin Studio**.
3. Choose a built-in profile or create your own colours.
4. Use **Generate accessible palette** or **Mutate palette** if you want quick ideas.
5. Check the contrast readout.
6. Go to **Targets**.
7. Click **Refresh windows**.
8. Select the target window or choose a target mode.
9. Use **Preview targets** before applying.
10. Click **Apply once**.
11. Use **Undo last apply** if needed.

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + R` | Refresh visible windows |
| `Ctrl + Enter` | Apply current skin |
| `Ctrl + S` | Save current profile |
| `Esc` | Stop live apply |

---

## Profile Data

OpenSkin Lab stores local profile and targeting data near the app file:

| File | Purpose |
|---|---|
| `openskin_profiles.json` | Saved user profiles |
| `openskin_targets.json` | Favourite target rules and recent apply history |

These files are generated locally when you save profiles or target data. They do not need to be committed unless you intentionally want to share example profiles.

Recommended `.gitignore` entries:

```gitignore
openskin_profiles.json
openskin_targets.json
*.log
__pycache__/
*.pyc
```

---

## Theme Profile Format

Exported profiles use JSON. A profile contains values similar to:

```json
{
  "caption_color": "#154c79",
  "text_color": "#ffffff",
  "border_color": "#4db6ac",
  "dark_mode": true,
  "corner": "Rounded",
  "backdrop": "Mica",
  "close_symbol": "X"
}
```

Supported corner options:

- `System default`
- `Square`
- `Rounded`
- `Small rounded`

Supported backdrop options:

- `Auto`
- `None`
- `Mica`
- `Acrylic`
- `Tabbed`

---

## Safety Notes

OpenSkin Lab changes window-frame attributes on live windows. Before broad use:

- Test on a single non-critical window first.
- Avoid targeting unsaved work.
- Use **Preview targets** before applying.
- Keep broad-apply confirmation enabled.
- Use **Undo last apply** if the result is not what you expected.
- Run the app with matching privileges if you need to affect elevated applications.

The app is intended for experimentation, learning, and personal desktop customization.

---

## Project Structure

```text
OpenSkin/
├── Main.py              # Main OpenSkin Lab application
├── README.md            # Project documentation
├── LICENSE              # MIT license
├── SECURITY.md          # Security policy
└── CODE_OF_CONDUCT.md   # Community conduct guidelines
```

---

## Project Status

OpenSkin Lab is an experimental Windows UI customization tool.

Current focus:

- Safer target-window selection
- Better profile workflows
- Accessible palette generation
- Clearer preview behaviour
- Research-led Windows styling experiments

Future ideas:

- Screenshot-based before/after comparison
- Theme gallery with thumbnails
- Portable release builds
- More robust Windows-version capability detection
- Per-app saved target presets
- Safer dry-run mode
- Better documentation screenshots
- Optional tray integration
- Improved diagnostics for failed DWM calls
- Exportable theme packs

---

## Troubleshooting

### “OpenSkin can only apply skins on Windows”

You are running the app outside Windows. The interface may open, but Windows DWM styling cannot be applied.

### Some windows do not change

Some applications custom-draw their title bars, run at a higher privilege level, are cloaked/hidden, or do not expose standard DWM behaviour.

Try:

- running OpenSkin with the same privilege level
- targeting a normal desktop app first
- refreshing the window list
- using active-window capture
- checking the Log tab

### Colours apply but texture/glyph changes do not

Texture and custom caption-button glyph features are preview/metadata concepts. Windows does not expose a safe public API for injecting arbitrary title-bar textures or replacing another app’s caption button symbols.

### Contrast warning appears

The selected caption/text colours do not meet the configured contrast target. Use:

- **Auto text colour**
- **Generate accessible palette**
- **High contrast** profile
- **Auto-fix contrast**

---

## Development

OpenSkin Lab is currently a single-file Python/Tkinter application. To improve it:

```bash
python Main.py
```

Suggested development tasks:

- split UI tabs into modules
- add automated colour/contrast tests
- add a `requirements.txt` only if external packages are introduced
- add screenshots to `docs/`
- add a release workflow for packaged Windows builds
- document known Windows build compatibility

---

## Security

Please report security issues through the repository security policy rather than public issues where possible.

Do not use OpenSkin Lab to interfere with other users’ systems or applications. The tool is intended for personal customization, learning, and Windows UI experimentation.

---

## Contributing

Contributions are welcome.

Good first improvements include:

- fixing UI layout issues
- improving documentation
- adding screenshots
- testing Windows version compatibility
- improving error messages
- refining accessibility checks
- adding safer defaults
- adding example profile packs

Before opening a pull request:

1. Keep the current single-file app working.
2. Avoid adding heavy dependencies without a clear reason.
3. Test on Windows.
4. Document new features in this README.
5. Follow the repository code of conduct.

---

## License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## Author

Created by [kai9987kai](https://github.com/kai9987kai).

Website: [kai9987kai.co.uk](https://kai9987kai.co.uk/)
