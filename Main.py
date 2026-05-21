import ctypes
import json
import os
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.colorchooser import askcolor
import tkinter as tk

try:
    from ctypes import wintypes
except ImportError:
    wintypes = None


APP_NAME = "OpenSkin Lab"
IS_WINDOWS = os.name == "nt"
APP_DIR = Path(__file__).resolve().parent
PROFILE_PATH = APP_DIR / "openskin_profiles.json"

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_BORDER_COLOR = 34
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36
DWMWA_SYSTEMBACKDROP_TYPE = 38
DWM_COLOR_DEFAULT = 0xFFFFFFFF

CORNER_OPTIONS = {
    "System default": 0,
    "Square": 1,
    "Rounded": 2,
    "Small rounded": 3,
}

BACKDROP_OPTIONS = {
    "Auto": 0,
    "None": 1,
    "Mica": 2,
    "Acrylic": 3,
    "Tabbed": 4,
}

BUILT_IN_PROFILES = {
    "Research blue": {
        "caption_color": "#154c79",
        "text_color": "#ffffff",
        "border_color": "#4db6ac",
        "dark_mode": True,
        "corner": "Rounded",
        "backdrop": "Mica",
        "close_symbol": "X",
    },
    "Signal green": {
        "caption_color": "#164b35",
        "text_color": "#f2fff8",
        "border_color": "#75d492",
        "dark_mode": True,
        "corner": "Small rounded",
        "backdrop": "Mica",
        "close_symbol": "X",
    },
    "Paper light": {
        "caption_color": "#f4f0e8",
        "text_color": "#202124",
        "border_color": "#7b8a8b",
        "dark_mode": False,
        "corner": "Rounded",
        "backdrop": "Auto",
        "close_symbol": "X",
    },
    "High contrast": {
        "caption_color": "#050505",
        "text_color": "#ffffff",
        "border_color": "#ffcc00",
        "dark_mode": True,
        "corner": "Square",
        "backdrop": "None",
        "close_symbol": "X",
    },
    "Soft graphite": {
        "caption_color": "#2f3437",
        "text_color": "#f6f7f8",
        "border_color": "#9aa4aa",
        "dark_mode": True,
        "corner": "Rounded",
        "backdrop": "Tabbed",
        "close_symbol": "X",
    },
}

RESEARCH_LINKS = [
    {
        "title": "DWM window attributes",
        "url": "https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute",
        "note": "Official attributes for caption, text, border, corners, dark mode, and backdrop.",
    },
    {
        "title": "Windows title bar customization",
        "url": "https://learn.microsoft.com/en-us/windows/apps/develop/title-bar?tabs=winui3",
        "note": "Microsoft guidance for what should and should not be customized.",
    },
    {
        "title": "SetWindowTextW",
        "url": "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowtextw",
        "note": "Official Win32 API used for scoped title overrides.",
    },
    {
        "title": "WCAG 2.2 contrast",
        "url": "https://www.w3.org/TR/wcag/#contrast-minimum",
        "note": "4.5:1 normal text contrast and 7:1 enhanced contrast targets.",
    },
]

VIDEO_LIBRARY = [
    ("Windows UI", "Windows title bar customization with Windows App SDK", "https://www.youtube.com/results?search_query=Windows+App+SDK+title+bar+customization+Microsoft", "Modern titlebar patterns and constraints."),
    ("Windows UI", "DwmSetWindowAttribute titlebar colors", "https://www.youtube.com/results?search_query=DwmSetWindowAttribute+DWMWA_CAPTION_COLOR", "Caption, text, and border color APIs."),
    ("Windows UI", "Win32 window handles and HWND basics", "https://www.youtube.com/results?search_query=Win32+HWND+window+handles+tutorial", "Targeting windows safely."),
    ("Windows UI", "Windows 11 Mica material explained", "https://www.youtube.com/results?search_query=Windows+11+Mica+material+developer", "Backdrop design and platform expectations."),
    ("Windows UI", "Windows 11 rounded corners developer guidance", "https://www.youtube.com/results?search_query=Windows+11+rounded+corners+developer+DWM", "Corner preference behavior."),
    ("Windows UI", "WinUI 3 titlebar customization", "https://www.youtube.com/results?search_query=WinUI+3+custom+titlebar+tutorial", "Migration path beyond Tkinter."),
    ("Windows UI", "Windows App SDK windowing", "https://www.youtube.com/results?search_query=Windows+App+SDK+windowing+AppWindow+tutorial", "AppWindow APIs and HWND interop."),
    ("Windows UI", "Windows dark mode for desktop apps", "https://www.youtube.com/results?search_query=Windows+desktop+app+dark+mode+DWM", "Dark-mode frame behavior."),
    ("Windows UI", "Microsoft Fluent Design for desktop apps", "https://www.youtube.com/results?search_query=Microsoft+Fluent+Design+Windows+desktop+apps", "Visual language and restraint."),
    ("Windows UI", "Windows accessibility for desktop developers", "https://www.youtube.com/results?search_query=Microsoft+Windows+accessibility+desktop+developer", "Accessible platform behavior."),
    ("Tkinter", "Modern Tkinter ttk layouts", "https://www.youtube.com/results?search_query=modern+tkinter+ttk+layout+tutorial", "Cleaner layout patterns."),
    ("Tkinter", "Tkinter notebook tabs tutorial", "https://www.youtube.com/results?search_query=tkinter+ttk+notebook+tabs+tutorial", "Multi-panel interface structure."),
    ("Tkinter", "Tkinter Treeview search and filter", "https://www.youtube.com/results?search_query=tkinter+treeview+search+filter+tutorial", "Fast list browsing."),
    ("Tkinter", "Tkinter color chooser best practices", "https://www.youtube.com/results?search_query=tkinter+colorchooser+tutorial", "User-controlled color input."),
    ("Tkinter", "Tkinter after method event loop", "https://www.youtube.com/results?search_query=tkinter+after+method+event+loop+tutorial", "Safe periodic work without threads."),
    ("Tkinter", "Tkinter file dialogs and validation", "https://www.youtube.com/results?search_query=tkinter+filedialog+validation+tutorial", "Safer file selection."),
    ("Tkinter", "Tkinter JSON settings persistence", "https://www.youtube.com/results?search_query=tkinter+json+settings+persistence", "Profile save/load patterns."),
    ("Tkinter", "Tkinter responsive grid weights", "https://www.youtube.com/results?search_query=tkinter+grid+weight+responsive+layout", "Resizable interfaces."),
    ("Win32", "Python ctypes Win32 API tutorial", "https://www.youtube.com/results?search_query=python+ctypes+win32+api+tutorial", "Calling User32 and DWM from Python."),
    ("Win32", "EnumWindows Python tutorial", "https://www.youtube.com/results?search_query=python+EnumWindows+ctypes+tutorial", "Window discovery and filtering."),
    ("Win32", "GetWindowTextW Python ctypes", "https://www.youtube.com/results?search_query=GetWindowTextW+python+ctypes", "Reading titles safely."),
    ("Win32", "SetWindowTextW Python ctypes", "https://www.youtube.com/results?search_query=SetWindowTextW+python+ctypes", "Scoped title updates."),
    ("Win32", "Windows process and window enumeration", "https://www.youtube.com/results?search_query=windows+process+window+enumeration+python", "Understanding target surfaces."),
    ("Win32", "HRESULT debugging for Windows APIs", "https://www.youtube.com/results?search_query=HRESULT+debugging+Windows+API+tutorial", "Diagnosing failed DWM calls."),
    ("Accessibility", "WCAG color contrast explained", "https://www.youtube.com/results?search_query=WCAG+color+contrast+explained", "Why contrast ratios matter."),
    ("Accessibility", "Designing accessible color palettes", "https://www.youtube.com/results?search_query=accessible+color+palette+design+contrast", "Palette quality beyond aesthetics."),
    ("Accessibility", "Color blindness friendly UI design", "https://www.youtube.com/results?search_query=color+blindness+friendly+UI+design", "Avoid color-only communication."),
    ("Accessibility", "High contrast mode Windows apps", "https://www.youtube.com/results?search_query=Windows+high+contrast+mode+app+development", "Respecting user accessibility settings."),
    ("Accessibility", "Keyboard accessible desktop UI", "https://www.youtube.com/results?search_query=keyboard+accessible+desktop+UI+design", "Operable tool workflows."),
    ("Accessibility", "Inclusive design Microsoft", "https://www.youtube.com/results?search_query=Microsoft+inclusive+design+developer", "Broader design principles."),
    ("UX Research", "Human centered design for tools", "https://www.youtube.com/results?search_query=human+centered+design+developer+tools+UX", "Build around repeated workflows."),
    ("UX Research", "Progressive disclosure UI design", "https://www.youtube.com/results?search_query=progressive+disclosure+UI+design+tools", "Power without clutter."),
    ("UX Research", "Designing expert tools and dashboards", "https://www.youtube.com/results?search_query=designing+expert+tools+dashboard+UX", "Dense but readable control surfaces."),
    ("UX Research", "Error prevention in UI design", "https://www.youtube.com/results?search_query=error+prevention+UI+design", "Safer destructive and broad actions."),
    ("UX Research", "Visual feedback in desktop apps", "https://www.youtube.com/results?search_query=visual+feedback+desktop+application+UX", "Make state changes visible."),
    ("UX Research", "Design systems for desktop applications", "https://www.youtube.com/results?search_query=design+systems+desktop+applications", "Consistency and affordances."),
    ("Performance", "Avoiding busy loops in GUI apps", "https://www.youtube.com/results?search_query=avoid+busy+loop+GUI+application+python", "Event-driven scheduling."),
    ("Performance", "Tkinter threading pitfalls", "https://www.youtube.com/results?search_query=tkinter+threading+pitfalls", "Why Tk work stays on the main thread."),
    ("Performance", "Python GUI performance profiling", "https://www.youtube.com/results?search_query=python+GUI+performance+profiling", "Finding UI bottlenecks."),
    ("Performance", "Debouncing UI events", "https://www.youtube.com/results?search_query=debouncing+UI+events+python", "Avoid over-applying settings."),
    ("Performance", "Efficient Windows API calls from Python", "https://www.youtube.com/results?search_query=efficient+Windows+API+calls+Python+ctypes", "Keep API calls bounded."),
    ("Product Ideas", "Theme editor UX patterns", "https://www.youtube.com/results?search_query=theme+editor+UX+patterns", "Better skin editing workflows."),
    ("Product Ideas", "Live preview UI design", "https://www.youtube.com/results?search_query=live+preview+UI+design+desktop+app", "Preview before applying."),
    ("Product Ideas", "Preset management UI design", "https://www.youtube.com/results?search_query=preset+management+UI+design", "Save, recall, and compare variants."),
    ("Product Ideas", "Command palette desktop app UX", "https://www.youtube.com/results?search_query=command+palette+desktop+app+UX", "Possible next productivity feature."),
    ("Product Ideas", "Plugin architecture Python desktop app", "https://www.youtube.com/results?search_query=plugin+architecture+python+desktop+app", "Future extension model."),
    ("Product Ideas", "A/B testing UI themes", "https://www.youtube.com/results?search_query=A%2FB+testing+UI+themes+UX", "Experimentation ideas."),
    ("Product Ideas", "Design tokens explained", "https://www.youtube.com/results?search_query=design+tokens+explained", "Treat skins as structured tokens."),
    ("Product Ideas", "AI assisted UI theme generation", "https://www.youtube.com/results?search_query=AI+assisted+UI+theme+generation", "Experimental theme ideation."),
    ("Product Ideas", "Windows customization tools overview", "https://www.youtube.com/results?search_query=Windows+customization+tools+overview", "Competitive product research."),
]


@dataclass
class WindowInfo:
    hwnd: int
    title: str

    @property
    def display(self):
        return f"{self.title}  [0x{self.hwnd:08X}]"


if IS_WINDOWS:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetForegroundWindow.argtypes = []
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
    user32.SetWindowTextW.restype = wintypes.BOOL

    dwmapi.DwmSetWindowAttribute.argtypes = [
        wintypes.HWND,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long
else:
    user32 = None
    dwmapi = None
    WNDENUMPROC = None


class OpenSkinLab:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.minsize(980, 660)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.profiles = dict(BUILT_IN_PROFILES)
        self.user_profile_names = set()
        self.visible_windows = []
        self.live_job_id = None

        self.caption_color_var = tk.StringVar(value="#154c79")
        self.text_color_var = tk.StringVar(value="#ffffff")
        self.border_color_var = tk.StringVar(value="#4db6ac")
        self.window_title_var = tk.StringVar()
        self.close_symbol_var = tk.StringVar(value="X")
        self.texture_path_var = tk.StringVar()
        self.profile_var = tk.StringVar(value="Research blue")
        self.dark_mode_var = tk.BooleanVar(value=True)
        self.corner_var = tk.StringVar(value="Rounded")
        self.backdrop_var = tk.StringVar(value="Mica")
        self.target_mode_var = tk.StringVar(value="selected")
        self.title_filter_var = tk.StringVar()
        self.interval_var = tk.StringVar(value="2.0")
        self.status_var = tk.StringVar(value="Ready")
        self.contrast_var = tk.StringVar()
        self.video_search_var = tk.StringVar()
        self.video_category_var = tk.StringVar(value="All")

        self.load_profiles()
        self.create_gui()
        self.apply_profile("Research blue")
        self.refresh_windows()
        self.refresh_video_list()
        self.update_preview()

    def create_gui(self):
        self.configure_style()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.skin_tab = ttk.Frame(notebook, padding=10)
        self.targets_tab = ttk.Frame(notebook, padding=10)
        self.videos_tab = ttk.Frame(notebook, padding=10)
        self.research_tab = ttk.Frame(notebook, padding=10)
        self.log_tab = ttk.Frame(notebook, padding=10)

        notebook.add(self.skin_tab, text="Skin Studio")
        notebook.add(self.targets_tab, text="Targets")
        notebook.add(self.videos_tab, text="Videos")
        notebook.add(self.research_tab, text="Research")
        notebook.add(self.log_tab, text="Log")

        self.create_skin_tab()
        self.create_targets_tab()
        self.create_videos_tab()
        self.create_research_tab()
        self.create_log_tab()

        status = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        for variable in (
            self.caption_color_var,
            self.text_color_var,
            self.border_color_var,
            self.close_symbol_var,
        ):
            variable.trace_add("write", lambda *_: self.update_preview())
        self.video_search_var.trace_add("write", lambda *_: self.refresh_video_list())
        self.video_category_var.trace_add("write", lambda *_: self.refresh_video_list())

    def configure_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Muted.TLabel", foreground="#5f6368")
        style.configure("Warn.TLabel", foreground="#9a3412")

    def create_skin_tab(self):
        self.skin_tab.columnconfigure(0, weight=1)
        self.skin_tab.columnconfigure(1, weight=1)
        self.skin_tab.rowconfigure(1, weight=1)

        profile_frame = ttk.LabelFrame(self.skin_tab, text="Profiles", padding=10)
        profile_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        profile_frame.columnconfigure(1, weight=1)

        ttk.Label(profile_frame, text="Profile").grid(row=0, column=0, sticky="w")
        self.profile_combo = ttk.Combobox(
            profile_frame,
            textvariable=self.profile_var,
            values=sorted(self.profiles),
            state="normal",
        )
        self.profile_combo.grid(row=0, column=1, sticky="ew", padx=8)
        self.profile_combo.bind("<<ComboboxSelected>>", lambda _event: self.apply_profile())
        ttk.Button(profile_frame, text="Load", command=self.apply_profile).grid(row=0, column=2, padx=3)
        ttk.Button(profile_frame, text="Save", command=self.save_profile).grid(row=0, column=3, padx=3)
        ttk.Button(profile_frame, text="Delete", command=self.delete_profile).grid(row=0, column=4, padx=3)

        controls = ttk.LabelFrame(self.skin_tab, text="Composer", padding=10)
        controls.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        controls.columnconfigure(1, weight=1)

        self.color_row(controls, 0, "Caption", self.caption_color_var)
        self.color_row(controls, 1, "Text", self.text_color_var)
        self.color_row(controls, 2, "Border", self.border_color_var)

        ttk.Checkbutton(controls, text="Use dark frame mode", variable=self.dark_mode_var).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(8, 2)
        )

        ttk.Label(controls, text="Corners").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Combobox(
            controls,
            textvariable=self.corner_var,
            values=list(CORNER_OPTIONS),
            state="readonly",
        ).grid(row=4, column=1, columnspan=2, sticky="ew", pady=4)

        ttk.Label(controls, text="Backdrop").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Combobox(
            controls,
            textvariable=self.backdrop_var,
            values=list(BACKDROP_OPTIONS),
            state="readonly",
        ).grid(row=5, column=1, columnspan=2, sticky="ew", pady=4)

        ttk.Label(controls, text="Title override").grid(row=6, column=0, sticky="w", pady=4)
        ttk.Entry(controls, textvariable=self.window_title_var).grid(
            row=6, column=1, columnspan=2, sticky="ew", pady=4
        )

        ttk.Label(controls, text="Close symbol preview").grid(row=7, column=0, sticky="w", pady=4)
        ttk.Entry(controls, textvariable=self.close_symbol_var, width=8).grid(row=7, column=1, sticky="w", pady=4)
        ttk.Label(
            controls,
            text="Windows does not expose safe per-window close glyph replacement.",
            style="Muted.TLabel",
        ).grid(row=7, column=2, sticky="w", padx=8)

        ttk.Label(controls, text="Texture reference").grid(row=8, column=0, sticky="w", pady=4)
        ttk.Entry(controls, textvariable=self.texture_path_var).grid(row=8, column=1, sticky="ew", pady=4)
        ttk.Button(controls, text="Browse", command=self.pick_texture).grid(row=8, column=2, padx=(8, 0), pady=4)

        ttk.Label(controls, text="Live interval (s)").grid(row=9, column=0, sticky="w", pady=4)
        ttk.Spinbox(controls, from_=0.5, to=20.0, increment=0.5, textvariable=self.interval_var, width=8).grid(
            row=9, column=1, sticky="w", pady=4
        )

        actions = ttk.Frame(controls)
        actions.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        actions.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(actions, text="Apply once", style="Accent.TButton", command=self.apply_once).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(actions, text="Start live", command=self.start_live).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(actions, text="Stop", command=self.stop_live).grid(row=0, column=2, sticky="ew", padx=(4, 0))
        ttk.Button(actions, text="Reset selected windows", command=self.reset_selected).grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0)
        )

        preview = ttk.LabelFrame(self.skin_tab, text="Preview and Contrast", padding=10)
        preview.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(preview, height=250, highlightthickness=0, background="#f5f7fa")
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")

        ttk.Label(preview, textvariable=self.contrast_var).grid(row=1, column=0, sticky="w", pady=(10, 2))
        ttk.Button(preview, text="Auto-pick readable text color", command=self.auto_text_color).grid(
            row=2, column=0, sticky="ew", pady=(6, 0)
        )

    def color_row(self, parent, row, label, variable):
        ttk.Label(parent, text=f"{label} color").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=4)
        ttk.Button(parent, text="Pick", command=lambda: self.pick_color(variable)).grid(
            row=row, column=2, padx=(8, 0), pady=4
        )

    def create_targets_tab(self):
        self.targets_tab.columnconfigure(0, weight=1)
        self.targets_tab.rowconfigure(1, weight=1)

        scope = ttk.LabelFrame(self.targets_tab, text="Apply Scope", padding=10)
        scope.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for column in range(4):
            scope.columnconfigure(column, weight=1)

        ttk.Radiobutton(scope, text="Selected windows", variable=self.target_mode_var, value="selected").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Radiobutton(scope, text="Foreground window", variable=self.target_mode_var, value="active").grid(
            row=0, column=1, sticky="w"
        )
        ttk.Radiobutton(scope, text="Title contains", variable=self.target_mode_var, value="title_contains").grid(
            row=0, column=2, sticky="w"
        )
        ttk.Radiobutton(scope, text="All visible windows", variable=self.target_mode_var, value="all_visible").grid(
            row=0, column=3, sticky="w"
        )
        ttk.Label(scope, text="Title filter").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(scope, textvariable=self.title_filter_var).grid(
            row=1, column=1, columnspan=3, sticky="ew", pady=(8, 0)
        )

        list_frame = ttk.LabelFrame(self.targets_tab, text="Visible Windows", padding=10)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.window_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, activestyle="dotbox")
        self.window_listbox.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.window_listbox.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.window_listbox.configure(yscrollcommand=yscroll.set)

        target_actions = ttk.Frame(list_frame)
        target_actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        target_actions.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(target_actions, text="Refresh", command=self.refresh_windows).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(target_actions, text="Pick foreground in 2s", command=self.select_foreground_window).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(target_actions, text="Apply to selected", command=self.apply_once).grid(
            row=0, column=2, sticky="ew", padx=(4, 0)
        )

    def create_videos_tab(self):
        self.videos_tab.columnconfigure(0, weight=1)
        self.videos_tab.rowconfigure(1, weight=1)

        filters = ttk.Frame(self.videos_tab)
        filters.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        filters.columnconfigure(1, weight=1)

        ttk.Label(filters, text="Search").grid(row=0, column=0, sticky="w")
        ttk.Entry(filters, textvariable=self.video_search_var).grid(row=0, column=1, sticky="ew", padx=8)
        categories = ["All"] + sorted({item[0] for item in VIDEO_LIBRARY})
        ttk.Combobox(
            filters,
            textvariable=self.video_category_var,
            values=categories,
            state="readonly",
            width=18,
        ).grid(row=0, column=2, sticky="e")

        self.video_tree = ttk.Treeview(
            self.videos_tab,
            columns=("category", "title", "note"),
            show="headings",
            height=18,
        )
        self.video_tree.heading("category", text="Category")
        self.video_tree.heading("title", text="Video or search")
        self.video_tree.heading("note", text="Why it matters")
        self.video_tree.column("category", width=130, stretch=False)
        self.video_tree.column("title", width=360, stretch=True)
        self.video_tree.column("note", width=360, stretch=True)
        self.video_tree.grid(row=1, column=0, sticky="nsew")
        self.video_tree.bind("<Double-1>", lambda _event: self.open_selected_video())

        video_scroll = ttk.Scrollbar(self.videos_tab, orient="vertical", command=self.video_tree.yview)
        video_scroll.grid(row=1, column=1, sticky="ns")
        self.video_tree.configure(yscrollcommand=video_scroll.set)

        actions = ttk.Frame(self.videos_tab)
        actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        actions.columnconfigure((0, 1), weight=1)
        ttk.Button(actions, text="Open selected", command=self.open_selected_video).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(actions, text="Copy selected link", command=self.copy_selected_video_link).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

    def create_research_tab(self):
        self.research_tab.columnconfigure(0, weight=1)
        self.research_tab.rowconfigure(0, weight=1)

        self.research_tree = ttk.Treeview(
            self.research_tab,
            columns=("title", "note", "url"),
            show="headings",
            height=8,
        )
        self.research_tree.heading("title", text="Source")
        self.research_tree.heading("note", text="Applied in OpenSkin")
        self.research_tree.heading("url", text="Link")
        self.research_tree.column("title", width=220, stretch=False)
        self.research_tree.column("note", width=420, stretch=True)
        self.research_tree.column("url", width=360, stretch=True)
        self.research_tree.grid(row=0, column=0, sticky="nsew")
        self.research_tree.bind("<Double-1>", lambda _event: self.open_selected_research())

        for index, item in enumerate(RESEARCH_LINKS):
            self.research_tree.insert("", "end", iid=str(index), values=(item["title"], item["note"], item["url"]))

        notes = ttk.LabelFrame(self.research_tab, text="Implementation Notes", padding=10)
        notes.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        text = (
            "OpenSkin now uses documented Windows DWM attributes for safe frame-level skinning. "
            "Close-button glyph replacement and arbitrary texture injection are intentionally kept as previews "
            "because Windows does not provide a safe public API for changing another app's caption buttons or drawing textures into its non-client area."
        )
        ttk.Label(notes, text=text, wraplength=920, justify="left").grid(row=0, column=0, sticky="ew")
        ttk.Button(notes, text="Open selected source", command=self.open_selected_research).grid(
            row=1, column=0, sticky="ew", pady=(10, 0)
        )

    def create_log_tab(self):
        self.log_tab.columnconfigure(0, weight=1)
        self.log_tab.rowconfigure(0, weight=1)
        self.log_text = tk.Text(self.log_tab, height=20, wrap="word", state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(self.log_tab, orient="vertical", command=self.log_text.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=yscroll.set)
        ttk.Button(self.log_tab, text="Clear log", command=self.clear_log).grid(row=1, column=0, sticky="ew", pady=(10, 0))

    def pick_color(self, variable):
        initial = variable.get() if is_hex_color(variable.get()) else "#ffffff"
        _rgb, color = askcolor(color=initial, parent=self.root)
        if color:
            variable.set(color.lower())

    def pick_texture(self):
        file_path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose a texture reference",
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.texture_path_var.set(file_path)

    def update_preview(self):
        if not hasattr(self, "preview_canvas"):
            return

        canvas = self.preview_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 500)
        height = max(canvas.winfo_height(), 240)

        caption = self.caption_color_var.get()
        text = self.text_color_var.get()
        border = self.border_color_var.get()
        if not is_hex_color(caption):
            caption = "#154c79"
        if not is_hex_color(text):
            text = "#ffffff"
        if not is_hex_color(border):
            border = "#4db6ac"

        margin = 32
        x1, y1 = margin, 42
        x2, y2 = width - margin, height - 42
        canvas.create_rectangle(x1, y1, x2, y2, fill="#ffffff", outline=border, width=3)
        canvas.create_rectangle(x1, y1, x2, y1 + 44, fill=caption, outline=caption)
        canvas.create_text(x1 + 18, y1 + 22, anchor="w", text="OpenSkin target preview", fill=text, font=("Segoe UI", 11, "bold"))
        symbol = (self.close_symbol_var.get() or "X")[:3]
        canvas.create_rectangle(x2 - 50, y1, x2, y1 + 44, fill=caption, outline=caption)
        canvas.create_text(x2 - 25, y1 + 22, text=symbol, fill=text, font=("Segoe UI", 12, "bold"))
        canvas.create_text(
            x1 + 18,
            y1 + 82,
            anchor="w",
            text="Texture and custom glyphs are preview metadata; DWM applies frame colors, corners, and backdrop.",
            fill="#4b5563",
            font=("Segoe UI", 10),
            width=x2 - x1 - 36,
        )

        try:
            ratio = contrast_ratio(hex_to_rgb(caption), hex_to_rgb(text))
            level = "AAA" if ratio >= 7 else "AA" if ratio >= 4.5 else "low"
            self.contrast_var.set(f"Caption/text contrast: {ratio:.2f}:1 ({level}; normal text target is 4.5:1)")
        except ValueError:
            self.contrast_var.set("Caption/text contrast: enter valid #RRGGBB colors.")

    def auto_text_color(self):
        try:
            caption_rgb = hex_to_rgb(self.caption_color_var.get())
        except ValueError:
            messagebox.showerror(APP_NAME, "Enter a valid caption color first.")
            return
        black_ratio = contrast_ratio(caption_rgb, (0, 0, 0))
        white_ratio = contrast_ratio(caption_rgb, (255, 255, 255))
        self.text_color_var.set("#000000" if black_ratio >= white_ratio else "#ffffff")

    def load_profiles(self):
        if not PROFILE_PATH.exists():
            return
        try:
            payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.log(f"Could not load profiles: {exc}")
            return

        if not isinstance(payload, dict):
            return
        for name, settings in payload.items():
            if isinstance(name, str) and isinstance(settings, dict):
                self.profiles[name] = settings
                self.user_profile_names.add(name)

    def persist_profiles(self):
        user_profiles = {
            name: self.profiles[name]
            for name in sorted(self.user_profile_names)
            if name in self.profiles
        }
        PROFILE_PATH.write_text(json.dumps(user_profiles, indent=2), encoding="utf-8")

    def update_profile_values(self):
        self.profile_combo.configure(values=sorted(self.profiles))

    def apply_profile(self, name=None):
        profile_name = name or self.profile_var.get().strip()
        settings = self.profiles.get(profile_name)
        if not settings:
            messagebox.showerror(APP_NAME, f"Profile '{profile_name}' was not found.")
            return
        self.profile_var.set(profile_name)
        self.caption_color_var.set(settings.get("caption_color", "#154c79"))
        self.text_color_var.set(settings.get("text_color", "#ffffff"))
        self.border_color_var.set(settings.get("border_color", "#4db6ac"))
        self.dark_mode_var.set(bool(settings.get("dark_mode", True)))
        self.corner_var.set(settings.get("corner", "Rounded"))
        self.backdrop_var.set(settings.get("backdrop", "Mica"))
        self.close_symbol_var.set(settings.get("close_symbol", "X"))
        self.log(f"Loaded profile: {profile_name}")

    def save_profile(self):
        name = self.profile_var.get().strip()
        if not name:
            messagebox.showerror(APP_NAME, "Enter a profile name before saving.")
            return
        try:
            settings = self.snapshot_settings(include_title=False)
        except ValueError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        self.profiles[name] = settings
        self.user_profile_names.add(name)
        self.persist_profiles()
        self.update_profile_values()
        self.profile_var.set(name)
        self.log(f"Saved profile: {name}")

    def delete_profile(self):
        name = self.profile_var.get().strip()
        if name in BUILT_IN_PROFILES:
            messagebox.showinfo(APP_NAME, "Built-in profiles cannot be deleted.")
            return
        if name not in self.profiles:
            messagebox.showerror(APP_NAME, f"Profile '{name}' was not found.")
            return
        del self.profiles[name]
        self.user_profile_names.discard(name)
        self.persist_profiles()
        self.update_profile_values()
        self.profile_var.set("Research blue")
        self.apply_profile("Research blue")
        self.log(f"Deleted profile: {name}")

    def snapshot_settings(self, include_title=True):
        caption_color = normalize_hex(self.caption_color_var.get(), "Caption color")
        text_color = normalize_hex(self.text_color_var.get(), "Text color")
        border_color = normalize_hex(self.border_color_var.get(), "Border color")
        corner = self.corner_var.get()
        backdrop = self.backdrop_var.get()
        if corner not in CORNER_OPTIONS:
            raise ValueError("Choose a valid corner style.")
        if backdrop not in BACKDROP_OPTIONS:
            raise ValueError("Choose a valid backdrop style.")

        settings = {
            "caption_color": caption_color,
            "text_color": text_color,
            "border_color": border_color,
            "dark_mode": bool(self.dark_mode_var.get()),
            "corner": corner,
            "backdrop": backdrop,
            "close_symbol": self.close_symbol_var.get()[:3] or "X",
            "texture_path": self.texture_path_var.get().strip(),
        }
        if include_title:
            settings["title"] = self.window_title_var.get().strip()
        return settings

    def refresh_windows(self):
        self.visible_windows = self.enumerate_windows()
        self.window_listbox.delete(0, tk.END)
        for window in self.visible_windows:
            self.window_listbox.insert(tk.END, window.display)
        self.status_var.set(f"Found {len(self.visible_windows)} visible titled windows.")
        self.log(f"Refreshed windows: {len(self.visible_windows)} visible titled windows")

    def enumerate_windows(self):
        if not IS_WINDOWS:
            return []

        windows = []
        own_hwnd = 0
        try:
            own_hwnd = int(self.root.winfo_id())
        except tk.TclError:
            pass

        def callback(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            hwnd_int = int(hwnd)
            if own_hwnd and hwnd_int == own_hwnd:
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value.strip()
            if title and title != APP_NAME:
                windows.append(WindowInfo(hwnd_int, title))
            return True

        enum_proc = WNDENUMPROC(callback)
        if not user32.EnumWindows(enum_proc, 0):
            self.log_last_error("EnumWindows failed")
        return sorted(windows, key=lambda item: item.title.casefold())

    def select_foreground_window(self):
        if not IS_WINDOWS:
            return
        self.status_var.set("Focus the target window now. Capturing foreground window in 2 seconds.")
        self.root.after(2000, self.capture_foreground_window)

    def capture_foreground_window(self):
        hwnd = int(user32.GetForegroundWindow())
        self.window_listbox.selection_clear(0, tk.END)
        for index, item in enumerate(self.visible_windows):
            if item.hwnd == hwnd:
                self.window_listbox.selection_set(index)
                self.window_listbox.see(index)
                self.target_mode_var.set("selected")
                self.status_var.set("Foreground window selected.")
                return
        self.status_var.set("Foreground window is not in the current list. Refresh and try again.")

    def target_windows(self):
        if not IS_WINDOWS:
            return []
        mode = self.target_mode_var.get()
        if mode == "active":
            hwnd = int(user32.GetForegroundWindow())
            return [hwnd] if hwnd else []
        if mode == "title_contains":
            needle = self.title_filter_var.get().strip().casefold()
            if not needle:
                raise ValueError("Enter text for the title filter.")
            return [item.hwnd for item in self.visible_windows if needle in item.title.casefold()]
        if mode == "all_visible":
            return [item.hwnd for item in self.visible_windows]

        selections = self.window_listbox.curselection()
        return [self.visible_windows[index].hwnd for index in selections]

    def apply_once(self, quiet=False):
        if not IS_WINDOWS:
            messagebox.showerror(APP_NAME, "OpenSkin can only apply skins on Windows.")
            return
        try:
            settings = self.snapshot_settings()
            targets = self.target_windows()
        except ValueError as exc:
            if not quiet:
                messagebox.showerror(APP_NAME, str(exc))
            self.status_var.set(str(exc))
            return
        if not targets:
            if not quiet:
                messagebox.showinfo(APP_NAME, "Choose at least one target window.")
            self.status_var.set("No target windows selected.")
            return

        successes = 0
        failures = []
        for hwnd in targets:
            ok, messages = self.apply_to_window(hwnd, settings)
            if ok:
                successes += 1
            else:
                failures.append(f"0x{hwnd:08X}: {'; '.join(messages)}")

        summary = f"Applied skin to {successes}/{len(targets)} window(s)."
        if failures:
            summary += f" {len(failures)} failure(s); see log."
            for failure in failures[:8]:
                self.log(f"Apply failed: {failure}")
        self.status_var.set(summary)
        self.log(summary)

    def apply_to_window(self, hwnd, settings):
        messages = []
        success = True

        for attr, color_key in (
            (DWMWA_CAPTION_COLOR, "caption_color"),
            (DWMWA_TEXT_COLOR, "text_color"),
            (DWMWA_BORDER_COLOR, "border_color"),
        ):
            ok, message = self.dwm_set_dword(hwnd, attr, colorref_from_hex(settings[color_key]))
            success = success and ok
            if not ok:
                messages.append(message)

        ok, message = self.dwm_set_bool(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, settings["dark_mode"])
        success = success and ok
        if not ok:
            messages.append(message)

        ok, message = self.dwm_set_dword(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, CORNER_OPTIONS[settings["corner"]])
        success = success and ok
        if not ok:
            messages.append(message)

        ok, message = self.dwm_set_dword(hwnd, DWMWA_SYSTEMBACKDROP_TYPE, BACKDROP_OPTIONS[settings["backdrop"]])
        success = success and ok
        if not ok:
            messages.append(message)

        title = settings.get("title", "")
        if title:
            if not user32.SetWindowTextW(wintypes.HWND(hwnd), title):
                success = False
                messages.append(last_error_message("SetWindowTextW failed"))

        return success, messages

    def reset_selected(self):
        if not IS_WINDOWS:
            messagebox.showerror(APP_NAME, "OpenSkin can only reset skins on Windows.")
            return
        try:
            targets = self.target_windows()
        except ValueError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        if not targets:
            messagebox.showinfo(APP_NAME, "Choose at least one target window.")
            return
        failures = []
        for hwnd in targets:
            for attr in (DWMWA_CAPTION_COLOR, DWMWA_TEXT_COLOR, DWMWA_BORDER_COLOR):
                ok, message = self.dwm_set_dword(hwnd, attr, DWM_COLOR_DEFAULT)
                if not ok:
                    failures.append(f"0x{hwnd:08X}: {message}")
            self.dwm_set_bool(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, False)
            self.dwm_set_dword(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, CORNER_OPTIONS["System default"])
            self.dwm_set_dword(hwnd, DWMWA_SYSTEMBACKDROP_TYPE, BACKDROP_OPTIONS["Auto"])
        summary = f"Reset {len(targets)} selected window(s)."
        if failures:
            summary += f" {len(failures)} color reset failure(s); see log."
            for failure in failures[:8]:
                self.log(f"Reset failed: {failure}")
        self.status_var.set(summary)
        self.log(summary)

    def start_live(self):
        if self.live_job_id:
            self.status_var.set("Live apply is already running.")
            return
        self.status_var.set("Live apply started.")
        self.log("Live apply started")
        self.schedule_live()

    def schedule_live(self):
        self.apply_once(quiet=True)
        try:
            interval = max(0.5, float(self.interval_var.get()))
        except ValueError:
            interval = 2.0
            self.interval_var.set("2.0")
        self.live_job_id = self.root.after(int(interval * 1000), self.schedule_live)

    def stop_live(self):
        if self.live_job_id:
            self.root.after_cancel(self.live_job_id)
            self.live_job_id = None
            self.status_var.set("Live apply stopped.")
            self.log("Live apply stopped")

    def dwm_set_dword(self, hwnd, attr, value):
        data = wintypes.DWORD(value & 0xFFFFFFFF)
        result = dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(attr),
            ctypes.byref(data),
            ctypes.sizeof(data),
        )
        if result != 0:
            return False, f"DwmSetWindowAttribute({attr}) failed with HRESULT 0x{result & 0xFFFFFFFF:08X}"
        return True, ""

    def dwm_set_bool(self, hwnd, attr, value):
        data = wintypes.BOOL(1 if value else 0)
        result = dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(attr),
            ctypes.byref(data),
            ctypes.sizeof(data),
        )
        if result != 0:
            return False, f"DwmSetWindowAttribute({attr}) failed with HRESULT 0x{result & 0xFFFFFFFF:08X}"
        return True, ""

    def refresh_video_list(self):
        if not hasattr(self, "video_tree"):
            return
        for item in self.video_tree.get_children():
            self.video_tree.delete(item)
        query = self.video_search_var.get().strip().casefold()
        category = self.video_category_var.get()
        count = 0
        for index, (item_category, title, url, note) in enumerate(VIDEO_LIBRARY):
            haystack = f"{item_category} {title} {note}".casefold()
            if category != "All" and item_category != category:
                continue
            if query and query not in haystack:
                continue
            self.video_tree.insert("", "end", iid=str(index), values=(item_category, title, note))
            count += 1
        self.status_var.set(f"Showing {count} video resource(s).")

    def selected_video_url(self):
        selection = self.video_tree.selection()
        if not selection:
            return None
        index = int(selection[0])
        return VIDEO_LIBRARY[index][2]

    def open_selected_video(self):
        url = self.selected_video_url()
        if not url:
            messagebox.showinfo(APP_NAME, "Select a video resource first.")
            return
        webbrowser.open(url)
        self.log(f"Opened video resource: {url}")

    def copy_selected_video_link(self):
        url = self.selected_video_url()
        if not url:
            messagebox.showinfo(APP_NAME, "Select a video resource first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.status_var.set("Copied video link to clipboard.")

    def open_selected_research(self):
        selection = self.research_tree.selection()
        if not selection:
            messagebox.showinfo(APP_NAME, "Select a research source first.")
            return
        index = int(selection[0])
        url = RESEARCH_LINKS[index]["url"]
        webbrowser.open(url)
        self.log(f"Opened research source: {url}")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        if hasattr(self, "log_text"):
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, line)
            self.log_text.see(tk.END)
            self.log_text.configure(state="disabled")

    def log_last_error(self, context):
        self.log(f"{context}: {last_error_message(context)}")

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def on_close(self):
        self.stop_live()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def is_hex_color(value):
    if not isinstance(value, str):
        return False
    if len(value) != 7 or not value.startswith("#"):
        return False
    try:
        int(value[1:], 16)
    except ValueError:
        return False
    return True


def normalize_hex(value, label):
    value = value.strip().lower()
    if not is_hex_color(value):
        raise ValueError(f"{label} must be a #RRGGBB color.")
    return value


def hex_to_rgb(value):
    value = normalize_hex(value, "Color")
    return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)


def colorref_from_hex(value):
    red, green, blue = hex_to_rgb(value)
    return red | (green << 8) | (blue << 16)


def relative_luminance(rgb):
    def channel(value):
        value = value / 255
        if value <= 0.03928:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (channel(component) for component in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first, second):
    first_luminance = relative_luminance(first)
    second_luminance = relative_luminance(second)
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def last_error_message(context):
    error_code = ctypes.get_last_error()
    if error_code == 0:
        return context
    return f"{context}: Windows error {error_code}"


if __name__ == "__main__":
    app = OpenSkinLab()
    app.run()
