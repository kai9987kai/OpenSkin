import ctypes
import colorsys
import json
import os
import random
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
TARGET_RULES_PATH = APP_DIR / "openskin_targets.json"
PROFILE_EXPORT_VERSION = 2
MIN_TEXT_CONTRAST = 4.5
BROAD_TARGET_LIMIT = 8
MAX_UNDO_STACK = 10
MAX_RECENT_APPLIES = 25
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
DWMWA_CLOAKED = 14
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080

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

RESEARCH_LINKS.extend(
    [
        {
            "title": "Custom frame with DWM",
            "url": "https://learn.microsoft.com/en-us/windows/win32/dwm/customframe",
            "note": "Official DWM custom-frame guidance for deeper future chrome work.",
        },
        {
            "title": "DWM composition overview",
            "url": "https://learn.microsoft.com/en-us/windows/win32/dwm/composition-ovw",
            "note": "Explains Desktop Window Manager composition behavior and constraints.",
        },
        {
            "title": "Accessible Windows apps",
            "url": "https://learn.microsoft.com/en-us/windows/apps/develop/accessibility",
            "note": "Microsoft guidance for accessible Windows app development.",
        },
        {
            "title": "Inclusive Windows apps",
            "url": "https://learn.microsoft.com/en-us/windows/apps/design/accessibility/developing-inclusive-windows-apps",
            "note": "Inclusive design requirements for Windows experiences.",
        },
        {
            "title": "Windows accessibility testing",
            "url": "https://learn.microsoft.com/en-us/windows/apps/design/accessibility/accessibility-testing",
            "note": "Testing workflow for keyboard, screen reader, and accessibility behavior.",
        },
        {
            "title": "UI Automation overview",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview",
            "note": "Future path for inspecting target app accessibility metadata.",
        },
        {
            "title": "Windows contrast themes",
            "url": "https://learn.microsoft.com/en-us/windows/apps/design/accessibility/high-contrast-themes",
            "note": "How Windows apps should behave with contrast themes.",
        },
        {
            "title": "Color in Windows apps",
            "url": "https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/color",
            "note": "Microsoft color guidance for Windows app interfaces.",
        },
        {
            "title": "Fluent 2 color",
            "url": "https://fluent2.microsoft.design/color",
            "note": "Current Microsoft color system and design-token grounding.",
        },
        {
            "title": "Fluent 2 material",
            "url": "https://fluent2.microsoft.design/material",
            "note": "Material guidance for Mica, Acrylic-like surfaces, and depth.",
        },
        {
            "title": "Microsoft Inclusive Design",
            "url": "https://inclusive.microsoft.design/",
            "note": "Inclusive design principles behind the guardrails and preview workflows.",
        },
        {
            "title": "WCAG non-text contrast",
            "url": "https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast",
            "note": "3:1 guidance for UI component boundaries and visual indicators.",
        },
        {
            "title": "WCAG focus appearance",
            "url": "https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance",
            "note": "Current focus-indicator quality guidance in WCAG 2.2.",
        },
        {
            "title": "MDN color contrast",
            "url": "https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Understanding_WCAG/Perceivable/Color_contrast",
            "note": "Practical contrast guidance used by many accessibility teams.",
        },
        {
            "title": "MDN forced colors",
            "url": "https://developer.mozilla.org/en-US/docs/Web/CSS/%40media/forced-colors",
            "note": "Useful model for thinking about forced/high-contrast color environments.",
        },
        {
            "title": "A11Y Project checklist",
            "url": "https://www.a11yproject.com/checklist/",
            "note": "Practical accessibility checklist for product review.",
        },
        {
            "title": "Deque WCAG 2.2",
            "url": "https://dequeuniversity.com/resources/wcag-2.2/",
            "note": "Operational summary of WCAG 2.2 changes and testing implications.",
        },
        {
            "title": "Section508 color usage",
            "url": "https://www.section508.gov/create/making-color-usage-accessible/",
            "note": "Government accessibility guidance for color-dependent UI.",
        },
        {
            "title": "NN/g usability heuristics",
            "url": "https://www.nngroup.com/articles/ten-usability-heuristics/",
            "note": "Usability baseline behind preview, undo, and status feedback.",
        },
        {
            "title": "NN/g visual design principles",
            "url": "https://www.nngroup.com/articles/principles-visual-design/",
            "note": "Visual hierarchy and contrast principles for theme design.",
        },
        {
            "title": "NN/g usability testing",
            "url": "https://www.nngroup.com/articles/usability-testing-101/",
            "note": "Workflow for validating OpenSkin target and theme editing tasks.",
        },
    ]
)

VIDEO_LIBRARY.extend(
    [
        ("Windows DWM", "DwmSetWindowAttribute caption color Windows 11", "https://www.youtube.com/results?search_query=DwmSetWindowAttribute+caption+color+Windows+11", "Direct coverage of the API OpenSkin calls."),
        ("Windows DWM", "DWMWA_USE_IMMERSIVE_DARK_MODE Win32", "https://www.youtube.com/results?search_query=DWMWA_USE_IMMERSIVE_DARK_MODE+Win32", "Dark frame behavior and compatibility."),
        ("Windows DWM", "DWMWA_CAPTION_COLOR DWMWA_TEXT_COLOR tutorial", "https://www.youtube.com/results?search_query=DWMWA_CAPTION_COLOR+DWMWA_TEXT_COLOR+tutorial", "Caption and title text color workflow."),
        ("Windows DWM", "Custom window frame using DWM Win32", "https://www.youtube.com/results?search_query=custom+window+frame+using+DWM+Win32", "Path for custom chrome beyond frame attributes."),
        ("Windows DWM", "DwmExtendFrameIntoClientArea custom title bar", "https://www.youtube.com/results?search_query=DwmExtendFrameIntoClientArea+custom+title+bar", "Advanced frame extension concepts."),
        ("Windows DWM", "Win32 non-client area painting title bar", "https://www.youtube.com/results?search_query=Win32+non-client+area+painting+title+bar", "Riskier custom drawing concepts for future research."),
        ("Windows DWM", "Windows 11 rounded corners DWM API", "https://www.youtube.com/results?search_query=Windows+11+rounded+corners+DWM+API", "Corner preference behavior and limits."),
        ("Windows DWM", "Windows title bar active inactive color states", "https://www.youtube.com/results?search_query=Windows+title+bar+active+inactive+color+states", "State-aware theme quality."),
        ("Windows DWM", "DwmGetWindowAttribute examples", "https://www.youtube.com/results?search_query=DwmGetWindowAttribute+examples+Win32", "Useful for undo and diagnostics."),
        ("Windows DWM", "Windows composition and DWM architecture", "https://www.youtube.com/results?search_query=Windows+DWM+composition+architecture", "Mental model for what can be customized safely."),
        ("Windows App SDK", "AppWindowTitleBar Windows App SDK", "https://www.youtube.com/results?search_query=AppWindowTitleBar+Windows+App+SDK", "Modern titlebar APIs for a future native rewrite."),
        ("Windows App SDK", "Windows App SDK title bar customization", "https://www.youtube.com/results?search_query=Windows+App+SDK+title+bar+customization", "Official app-window direction."),
        ("Windows App SDK", "WinUI 3 custom title bar", "https://www.youtube.com/results?search_query=WinUI+3+custom+title+bar", "Production-grade custom chrome workflow."),
        ("Windows App SDK", "Windows App SDK AppWindow tutorial", "https://www.youtube.com/results?search_query=Windows+App+SDK+AppWindow+tutorial", "Window control beyond Tkinter."),
        ("Windows App SDK", "Windows 11 app design guidelines", "https://www.youtube.com/results?search_query=Windows+11+app+design+guidelines", "Design fit for Windows 11."),
        ("Windows App SDK", "Microsoft Developer Windows app design", "https://www.youtube.com/results?search_query=Microsoft+Developer+Windows+app+design", "Current Microsoft design talks."),
        ("Fluent Design", "Fluent Design Windows 11 color system", "https://www.youtube.com/results?search_query=Fluent+Design+Windows+11+color+system", "Better color-token decisions."),
        ("Fluent Design", "Microsoft Fluent 2 color accessibility", "https://www.youtube.com/results?search_query=Microsoft+Fluent+2+color+accessibility", "Current Microsoft accessibility color guidance."),
        ("Fluent Design", "Mica Acrylic Windows 11 app design", "https://www.youtube.com/results?search_query=Mica+Acrylic+Windows+11+app+design", "Backdrop material decisions."),
        ("Fluent Design", "Fluent 2 design tokens", "https://www.youtube.com/results?search_query=Fluent+2+design+tokens", "Theme profiles as design tokens."),
        ("Fluent Design", "Microsoft Inclusive Design for software", "https://www.youtube.com/results?search_query=Microsoft+Inclusive+Design+software", "Guardrail design philosophy."),
        ("Python Desktop", "Tkinter Windows native title bar customization", "https://www.youtube.com/results?search_query=Tkinter+Windows+native+title+bar+customization", "Tkinter and native frame boundaries."),
        ("Python Desktop", "Tkinter ctypes DwmSetWindowAttribute", "https://www.youtube.com/results?search_query=Tkinter+ctypes+DwmSetWindowAttribute", "Python-specific implementation examples."),
        ("Python Desktop", "Python Windows dark mode title bar", "https://www.youtube.com/results?search_query=Python+Windows+dark+mode+title+bar", "Dark titlebar from Python."),
        ("Python Desktop", "Tkinter modern Windows 11 UI", "https://www.youtube.com/results?search_query=Tkinter+modern+Windows+11+UI", "Improving the app shell."),
        ("Python Desktop", "CustomTkinter Windows 11 theme", "https://www.youtube.com/results?search_query=CustomTkinter+Windows+11+theme", "Optional future UI direction."),
        ("Python Desktop", "ttk themes high contrast Tkinter", "https://www.youtube.com/results?search_query=ttk+themes+high+contrast+Tkinter", "Theme compatibility with accessibility."),
        ("Python Desktop", "Tkinter accessibility keyboard navigation", "https://www.youtube.com/results?search_query=Tkinter+accessibility+keyboard+navigation", "Keyboard-friendly desktop tooling."),
        ("Python Desktop", "Tkinter import export JSON settings", "https://www.youtube.com/results?search_query=Tkinter+import+export+JSON+settings", "Profile sharing patterns."),
        ("Python Desktop", "Tkinter undo redo pattern", "https://www.youtube.com/results?search_query=Tkinter+undo+redo+pattern", "Safer experimentation flows."),
        ("Accessibility", "Windows contrast themes app accessibility", "https://www.youtube.com/results?search_query=Windows+contrast+themes+app+accessibility", "Respect system-level contrast needs."),
        ("Accessibility", "WCAG 2.2 color contrast UI components", "https://www.youtube.com/results?search_query=WCAG+2.2+color+contrast+UI+components", "Modern contrast baseline."),
        ("Accessibility", "WCAG non-text contrast icons buttons", "https://www.youtube.com/results?search_query=WCAG+non-text+contrast+icons+buttons", "Borders and controls need contrast too."),
        ("Accessibility", "WCAG focus visible focus appearance", "https://www.youtube.com/results?search_query=WCAG+focus+visible+focus+appearance", "Keyboard focus quality."),
        ("Accessibility", "Forced colors mode Windows high contrast CSS", "https://www.youtube.com/results?search_query=forced-colors+mode+Windows+high+contrast+CSS", "High-contrast mental model."),
        ("Accessibility", "prefers contrast forced colors accessibility", "https://www.youtube.com/results?search_query=prefers-contrast+forced-colors+accessibility", "User contrast preferences."),
        ("Accessibility", "Screen reader desktop app accessibility UI Automation", "https://www.youtube.com/results?search_query=screen+reader+desktop+app+accessibility+UI+Automation", "Beyond visual customization."),
        ("Accessibility", "Windows UI Automation accessibility testing", "https://www.youtube.com/results?search_query=Windows+UI+Automation+accessibility+testing", "Testing target app metadata."),
        ("Accessibility", "A11Y Project accessibility checklist", "https://www.youtube.com/results?search_query=A11Y+Project+accessibility+checklist", "Practical review habits."),
        ("Accessibility", "Deque WCAG 2.2 accessibility testing", "https://www.youtube.com/results?search_query=Deque+WCAG+2.2+accessibility+testing", "Operational accessibility testing."),
        ("Color Science", "Dark mode accessibility contrast design", "https://www.youtube.com/results?search_query=dark+mode+accessibility+contrast+design", "Readable dark palettes."),
        ("Color Science", "Accessible color palette design UI", "https://www.youtube.com/results?search_query=accessible+color+palette+design+UI", "Palette generation grounded in readability."),
        ("Color Science", "APCA contrast WCAG comparison", "https://www.youtube.com/results?search_query=APCA+contrast+WCAG+comparison", "Emerging contrast-model research."),
        ("Color Science", "OKLCH color palette UI design", "https://www.youtube.com/results?search_query=OKLCH+color+palette+UI+design", "Newer color-space thinking for future work."),
        ("Color Science", "Semantic color tokens design system", "https://www.youtube.com/results?search_query=semantic+color+tokens+design+system", "Profiles as structured semantic tokens."),
        ("Color Science", "Active inactive window contrast UX", "https://www.youtube.com/results?search_query=active+inactive+window+contrast+UX", "Window-state readability."),
        ("Color Science", "Color blindness simulation UI design", "https://www.youtube.com/results?search_query=color+blindness+simulation+UI+design", "Avoid color-only affordances."),
        ("Color Science", "HSL color palette generation UI", "https://www.youtube.com/results?search_query=HSL+color+palette+generation+UI", "How the experiment lab currently derives variants."),
        ("Color Science", "Color harmony rules interface design", "https://www.youtube.com/results?search_query=color+harmony+rules+interface+design", "Complementary, triadic, and analogous palettes."),
        ("UX Research", "Nielsen Norman Group visual hierarchy contrast", "https://www.youtube.com/results?search_query=Nielsen+Norman+Group+visual+hierarchy+contrast", "Visual clarity research."),
        ("UX Research", "Nielsen Norman Group usability heuristics UI", "https://www.youtube.com/results?search_query=Nielsen+Norman+Group+usability+heuristics+UI", "Undo, status, and error prevention."),
        ("UX Research", "Aesthetic minimalist design desktop UI", "https://www.youtube.com/results?search_query=aesthetic+minimalist+design+desktop+UI", "Reduce control clutter."),
        ("UX Research", "Recognition rather than recall UI controls", "https://www.youtube.com/results?search_query=recognition+rather+than+recall+UI+controls", "Visible choices beat memorized commands."),
        ("UX Research", "Visibility of system status UI feedback", "https://www.youtube.com/results?search_query=visibility+of+system+status+UI+feedback", "Status messages and logs."),
        ("UX Research", "Usability testing desktop app theme editor", "https://www.youtube.com/results?search_query=usability+testing+desktop+app+theme+editor", "Validate the target/apply workflow."),
        ("UX Research", "Keyboard only usability testing Windows app", "https://www.youtube.com/results?search_query=keyboard+only+usability+testing+Windows+app", "Keyboard-first workflows."),
        ("UX Research", "Dry run preview pattern destructive actions", "https://www.youtube.com/results?search_query=dry+run+preview+pattern+destructive+actions+UX", "Why target previews reduce accidental changes."),
        ("UX Research", "Undo design pattern user interface", "https://www.youtube.com/results?search_query=undo+design+pattern+user+interface", "Safer experimentation."),
        ("Diagnostics", "Windows HRESULT error handling Win32", "https://www.youtube.com/results?search_query=Windows+HRESULT+error+handling+Win32", "Better failure diagnosis."),
        ("Diagnostics", "ctypes get last error Python Windows", "https://www.youtube.com/results?search_query=ctypes+get_last_error+Python+Windows", "Debugging Win32 calls."),
        ("Diagnostics", "Windows API access denied elevated windows", "https://www.youtube.com/results?search_query=Windows+API+access+denied+elevated+windows", "Understanding failed target operations."),
        ("Diagnostics", "Windows build version detection Python", "https://www.youtube.com/results?search_query=Windows+build+version+detection+Python", "Feature availability checks."),
        ("Diagnostics", "Python logging Tkinter application", "https://www.youtube.com/results?search_query=Python+logging+Tkinter+application", "Better app diagnostics."),
        ("Product Ideas", "Theme A/B testing design workflow", "https://www.youtube.com/results?search_query=theme+A%2FB+testing+design+workflow", "Compare generated skins."),
        ("Product Ideas", "Palette generator UI design", "https://www.youtube.com/results?search_query=palette+generator+UI+design", "Experiment lab evolution."),
        ("Product Ideas", "Design token export JSON", "https://www.youtube.com/results?search_query=design+token+export+JSON", "Profile sharing and future integration."),
        ("Product Ideas", "Desktop app plugin architecture Python", "https://www.youtube.com/results?search_query=desktop+app+plugin+architecture+Python", "Future extension path."),
        ("Product Ideas", "Local first desktop app settings sync", "https://www.youtube.com/results?search_query=local+first+desktop+app+settings+sync", "Future profile sync direction."),
    ]
)

RESEARCH_LINKS.extend(
    [
        {
            "title": "DWM API overview",
            "url": "https://learn.microsoft.com/en-us/windows/win32/api/_dwm/",
            "note": "Central Microsoft reference for Desktop Window Manager APIs.",
        },
        {
            "title": "DWM backdrop type",
            "url": "https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwm_systembackdrop_type",
            "note": "Official enum used by Mica, Acrylic, and Tabbed backdrop settings.",
        },
        {
            "title": "DwmSetWindowAttribute",
            "url": "https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmsetwindowattribute",
            "note": "Direct reference for the core apply calls.",
        },
        {
            "title": "GetWindowThreadProcessId",
            "url": "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid",
            "note": "Used to identify the process that owns each target HWND.",
        },
        {
            "title": "OpenProcess",
            "url": "https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess",
            "note": "Used with limited query access to inspect target process identity.",
        },
        {
            "title": "QueryFullProcessImageNameW",
            "url": "https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-queryfullprocessimagenamew",
            "note": "Retrieves target executable paths for safer target rows.",
        },
        {
            "title": "Extended window styles",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles",
            "note": "Reference for filtering tool windows out of broad scopes.",
        },
        {
            "title": "Window features",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features",
            "note": "Background for window types and why some HWNDs are poor targets.",
        },
        {
            "title": "UI Automation testing",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-usefortesting",
            "note": "Official direction for automated accessibility-oriented UI inspection.",
        },
        {
            "title": "UI Automation specification",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winauto/ui-automation-specification",
            "note": "Future direction for deeper target inspection.",
        },
        {
            "title": "Accessibility Insights Windows",
            "url": "https://accessibilityinsights.io/docs/windows/overview/",
            "note": "Recommended Windows accessibility inspection tool.",
        },
        {
            "title": "Windows App SDK",
            "url": "https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/",
            "note": "Future native Windows implementation path beyond Tkinter.",
        },
        {
            "title": "WinUI overview",
            "url": "https://learn.microsoft.com/en-us/windows/apps/winui/",
            "note": "Modern Windows UI stack for a future OpenSkin rewrite.",
        },
        {
            "title": "Microsoft confirmations",
            "url": "https://learn.microsoft.com/en-us/windows/win32/uxguide/mess-confirm",
            "note": "UX guide behind broad-scope confirmation prompts.",
        },
        {
            "title": "Python packaging guide",
            "url": "https://packaging.python.org/en/latest/overview/",
            "note": "Packaging reference for distributing OpenSkin.",
        },
        {
            "title": "PyInstaller manual",
            "url": "https://www.pyinstaller.org/en/stable/",
            "note": "Practical path to a Windows executable build.",
        },
    ]
)

VIDEO_LIBRARY.extend(
    [
        ("Window Metadata", "Windows HWND class name title process id", "https://www.youtube.com/results?search_query=Windows+HWND+class+name+title+process+id", "Understand the metadata now shown in the Targets table."),
        ("Window Metadata", "GetWindowThreadProcessId Win32 process inspection", "https://www.youtube.com/results?search_query=GetWindowThreadProcessId+Win32+process+inspection", "PID ownership lookup for target safety."),
        ("Window Metadata", "QueryFullProcessImageName Windows API", "https://www.youtube.com/results?search_query=QueryFullProcessImageName+Windows+API", "Resolve executable names from process handles."),
        ("Window Metadata", "Win32 window styles WS_EX_TOOLWINDOW WS_EX_APPWINDOW", "https://www.youtube.com/results?search_query=Win32+window+styles+WS_EX_TOOLWINDOW+WS_EX_APPWINDOW", "Filter poor targets from broad scans."),
        ("Window Metadata", "Spy++ window handles Win32 tutorial", "https://www.youtube.com/results?search_query=Spy%2B%2B+window+handles+Win32+tutorial", "Inspect HWNDs, classes, and process ownership."),
        ("Window Metadata", "Win32 EnumWindows tutorial", "https://www.youtube.com/results?search_query=Win32+EnumWindows+tutorial", "Window discovery foundations."),
        ("Window Metadata", "Win32 GetWindowRect vs DwmGetWindowAttribute", "https://www.youtube.com/results?search_query=Win32+GetWindowRect+vs+DwmGetWindowAttribute", "Geometry and DWM metadata differences."),
        ("Window Metadata", "DWM extended frame bounds Win32", "https://www.youtube.com/results?search_query=DWM+extended+frame+bounds+Win32", "Future target preview and geometry work."),
        ("Window Metadata", "Windows HWND reuse stale handle safety", "https://www.youtube.com/results?search_query=Windows+HWND+reuse+stale+handle+safety", "Why OpenSkin validates handles before apply."),
        ("Window Metadata", "Win32 IsWindow IsWindowVisible tutorial", "https://www.youtube.com/results?search_query=Win32+IsWindow+IsWindowVisible+tutorial", "Basic validity checks before calling APIs."),
        ("UI Automation", "Microsoft UI Automation tutorial", "https://www.youtube.com/results?search_query=Microsoft+UI+Automation+tutorial", "Future deeper app inspection."),
        ("UI Automation", "Win32 accessibility UI Automation overview", "https://www.youtube.com/results?search_query=Win32+accessibility+UI+Automation+overview", "Accessibility tree concepts."),
        ("UI Automation", "UI Automation Inspect tool Windows SDK", "https://www.youtube.com/results?search_query=UI+Automation+Inspect+tool+Windows+SDK", "Inspect target app UIA properties."),
        ("UI Automation", "Accessibility Insights for Windows tutorial", "https://www.youtube.com/results?search_query=Accessibility+Insights+for+Windows+tutorial", "Recommended Microsoft accessibility workflow."),
        ("UI Automation", "Windows Narrator app accessibility testing", "https://www.youtube.com/results?search_query=Windows+Narrator+app+accessibility+testing", "Manual accessibility checks."),
        ("UI Automation", "AccChecker Windows accessibility testing", "https://www.youtube.com/results?search_query=AccChecker+Windows+accessibility+testing", "Legacy SDK accessibility checking."),
        ("UI Automation", "UIA Verify Windows accessibility", "https://www.youtube.com/results?search_query=UIA+Verify+Windows+accessibility", "Manual and automated UIA validation."),
        ("UI Automation", "UI Automation control patterns explained", "https://www.youtube.com/results?search_query=UI+Automation+control+patterns+explained", "Understand UIA behavior contracts."),
        ("UI Automation", "Windows UI Automation Python", "https://www.youtube.com/results?search_query=Windows+UI+Automation+Python", "Potential future Python UIA integration."),
        ("UI Automation", "Desktop UI automation accessibility tree", "https://www.youtube.com/results?search_query=desktop+UI+automation+accessibility+tree", "Modern desktop automation research direction."),
        ("WinUI Roadmap", "WinUI 3 introduction Windows App SDK", "https://www.youtube.com/results?search_query=WinUI+3+introduction+Windows+App+SDK", "Future native OpenSkin shell."),
        ("WinUI Roadmap", "Windows App SDK tutorial WinUI 3", "https://www.youtube.com/results?search_query=Windows+App+SDK+tutorial+WinUI+3", "Modern Windows desktop framework."),
        ("WinUI Roadmap", "WinUI 3 desktop app C# tutorial", "https://www.youtube.com/results?search_query=WinUI+3+desktop+app+C%23+tutorial", "Implementation path for a native rewrite."),
        ("WinUI Roadmap", "WinUI 3 Mica backdrop title bar", "https://www.youtube.com/results?search_query=WinUI+3+Mica+backdrop+title+bar", "Native Mica/titlebar behavior."),
        ("WinUI Roadmap", "Windows App SDK app lifecycle desktop", "https://www.youtube.com/results?search_query=Windows+App+SDK+app+lifecycle+desktop", "App lifecycle concepts."),
        ("WinUI Roadmap", "WinUI 3 custom title bar Windows 11", "https://www.youtube.com/results?search_query=WinUI+3+custom+title+bar+Windows+11", "Production custom titlebar controls."),
        ("WinUI Roadmap", "Windows 11 app design Fluent UI", "https://www.youtube.com/results?search_query=Windows+11+app+design+Fluent+UI", "Windows-native design direction."),
        ("WinUI Roadmap", "WinUI 3 packaging MSIX desktop app", "https://www.youtube.com/results?search_query=WinUI+3+packaging+MSIX+desktop+app", "Distribution path for native apps."),
        ("Color Science", "relative luminance WCAG color contrast", "https://www.youtube.com/results?search_query=relative+luminance+WCAG+color+contrast", "Understand the implemented contrast math."),
        ("Color Science", "color science for UI design contrast", "https://www.youtube.com/results?search_query=color+science+for+UI+design+contrast", "Go beyond naive hue picking."),
        ("Color Science", "perceptual color spaces design systems", "https://www.youtube.com/results?search_query=perceptual+color+spaces+design+systems", "Future palette generator improvements."),
        ("Color Science", "Material Design color system accessibility", "https://www.youtube.com/results?search_query=Material+Design+color+system+accessibility", "Compare Fluent and Material color guidance."),
        ("Color Science", "Fluent UI color tokens accessibility", "https://www.youtube.com/results?search_query=Fluent+UI+color+tokens+accessibility", "Design-token accessibility model."),
        ("Safety Patterns", "UX error prevention destructive actions", "https://www.youtube.com/results?search_query=UX+error+prevention+destructive+actions", "Why OpenSkin confirms broad scope changes."),
        ("Safety Patterns", "confirmation dialogs UX best practices", "https://www.youtube.com/results?search_query=confirmation+dialogs+UX+best+practices", "Better confirmations."),
        ("Safety Patterns", "undo pattern UX destructive actions", "https://www.youtube.com/results?search_query=undo+pattern+UX+destructive+actions", "Undo as safety net."),
        ("Safety Patterns", "Nielsen heuristics error prevention user control", "https://www.youtube.com/results?search_query=Nielsen+heuristics+error+prevention+user+control", "Research basis for preview/undo/status."),
        ("Safety Patterns", "safe destructive action UX design", "https://www.youtube.com/results?search_query=safe+destructive+action+UX+design", "Guardrail design patterns."),
        ("Safety Patterns", "toast undo pattern UX", "https://www.youtube.com/results?search_query=toast+undo+pattern+UX", "Future nonblocking undo flow."),
        ("Packaging", "Python desktop app packaging Windows", "https://www.youtube.com/results?search_query=Python+desktop+app+packaging+Windows", "Prepare OpenSkin for distribution."),
        ("Packaging", "PyInstaller Windows desktop app tutorial", "https://www.youtube.com/results?search_query=PyInstaller+Windows+desktop+app+tutorial", "Executable packaging path."),
        ("Packaging", "PyInstaller onefile Windows no console", "https://www.youtube.com/results?search_query=PyInstaller+onefile+Windows+no+console", "Better end-user launch behavior."),
        ("Packaging", "PyInstaller code signing Windows", "https://www.youtube.com/results?search_query=PyInstaller+code+signing+Windows", "Trust and distribution concerns."),
        ("Packaging", "Nuitka onefile Windows Python app", "https://www.youtube.com/results?search_query=Nuitka+onefile+Windows+Python+app", "Alternative compiled packaging."),
        ("Packaging", "Nuitka vs PyInstaller Windows desktop", "https://www.youtube.com/results?search_query=Nuitka+vs+PyInstaller+Windows+desktop", "Packaging tradeoffs."),
        ("Packaging", "cx_Freeze Windows MSI Python app", "https://www.youtube.com/results?search_query=cx_Freeze+Windows+MSI+Python+app", "MSI-style packaging option."),
        ("Packaging", "BeeWare Briefcase Windows packaging", "https://www.youtube.com/results?search_query=BeeWare+Briefcase+Windows+packaging", "Native-app packaging ecosystem."),
        ("Packaging", "Python tkinter package exe Windows", "https://www.youtube.com/results?search_query=Python+tkinter+package+exe+Windows", "Tkinter executable distribution."),
        ("Packaging", "Windows desktop app code signing certificate tutorial", "https://www.youtube.com/results?search_query=Windows+desktop+app+code+signing+certificate+tutorial", "End-user trust and SmartScreen considerations."),
    ]
)

RESEARCH_LINKS.extend(
    [
        {
            "title": "User Interface Privilege Isolation",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-securityoverview",
            "note": "Explains why some elevated/protected windows cannot be controlled by normal desktop apps.",
        },
        {
            "title": "Window messages",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winmsg/window-messages",
            "note": "Background for Win32 message safety and window interaction boundaries.",
        },
        {
            "title": "SetWindowDisplayAffinity",
            "url": "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity",
            "note": "Privacy-related window display behavior for future target diagnostics.",
        },
        {
            "title": "UI Automation entry point",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32",
            "note": "Microsoft entry point for UI Automation concepts.",
        },
        {
            "title": "UI Automation control patterns",
            "url": "https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-controlpatternsoverview",
            "note": "Future path for target capability inspection.",
        },
        {
            "title": "ARIA Authoring Practices",
            "url": "https://www.w3.org/WAI/ARIA/apg/",
            "note": "Interaction-pattern guidance useful for accessibility-minded UI design.",
        },
        {
            "title": "Migrate to Windows App SDK",
            "url": "https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/migrate-to-windows-app-sdk/",
            "note": "Migration guide for a future native Windows version.",
        },
        {
            "title": "Windows App SDK lifecycle",
            "url": "https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/applifecycle/applifecycle",
            "note": "Lifecycle model for a more native OpenSkin app.",
        },
        {
            "title": "Windows App SDK windowing",
            "url": "https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/windowing/windowing-overview",
            "note": "Modern app windowing and titlebar APIs.",
        },
        {
            "title": "Windows Community Toolkit",
            "url": "https://learn.microsoft.com/en-us/windows/communitytoolkit/",
            "note": "Reusable Windows UI helpers for a future rewrite.",
        },
        {
            "title": "PyPI trusted publishing",
            "url": "https://docs.pypi.org/trusted-publishers/",
            "note": "Supply-chain guidance for publishing Python packages.",
        },
        {
            "title": "PyPI digital attestations",
            "url": "https://docs.pypi.org/attestations/",
            "note": "Emerging Python package provenance guidance.",
        },
        {
            "title": "pip-audit",
            "url": "https://pypi.org/project/pip-audit/",
            "note": "Python dependency vulnerability scanning.",
        },
        {
            "title": "Microsoft SignTool",
            "url": "https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool",
            "note": "Authenticode signing tool for Windows desktop distribution.",
        },
        {
            "title": "CSS Color 4",
            "url": "https://www.w3.org/TR/css-color-4/",
            "note": "Modern color spaces and color syntax reference.",
        },
        {
            "title": "Design Tokens Community Group",
            "url": "https://www.w3.org/community/design-tokens/",
            "note": "Standards track behind portable theme token formats.",
        },
        {
            "title": "Design Tokens format draft",
            "url": "https://tr.designtokens.org/format/",
            "note": "Future export target for OpenSkin profiles.",
        },
        {
            "title": "Material 3 color",
            "url": "https://m3.material.io/styles/color/overview",
            "note": "Modern color-system comparison point for palette generation.",
        },
        {
            "title": "NN/g A/B testing",
            "url": "https://www.nngroup.com/articles/ab-testing/",
            "note": "Experimentation guidance for comparing generated themes.",
        },
        {
            "title": "Microsoft ExP Platform",
            "url": "https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/",
            "note": "Research reference for controlled product experiments.",
        },
    ]
)

VIDEO_LIBRARY.extend(
    [
        ("Window Safety", "Windows UI Automation security overview Microsoft", "https://www.youtube.com/results?search_query=Windows+UI+Automation+security+overview+Microsoft", "Privilege boundaries and automation limits."),
        ("Window Safety", "Windows UIPI explained UIAccess desktop apps", "https://www.youtube.com/results?search_query=Windows+UIPI+explained+UIAccess+desktop+apps", "Why some target operations are blocked."),
        ("Window Safety", "Win32 window handle safety GetWindowThreadProcessId", "https://www.youtube.com/results?search_query=Win32+window+handle+safety+GetWindowThreadProcessId", "Safer target identity checks."),
        ("Window Safety", "Windows target window validation HWND process integrity", "https://www.youtube.com/results?search_query=Windows+target+window+validation+HWND+process+integrity", "Avoid stale or privileged targets."),
        ("Window Safety", "SetWindowDisplayAffinity Windows privacy overlay capture protection", "https://www.youtube.com/results?search_query=SetWindowDisplayAffinity+Windows+privacy+overlay+capture+protection", "Privacy-aware window behavior."),
        ("Window Safety", "Win32 window messages security risks", "https://www.youtube.com/results?search_query=Win32+window+messages+security+risks", "Security model behind window messaging."),
        ("Window Safety", "Windows low integrity medium integrity high integrity UI automation", "https://www.youtube.com/results?search_query=Windows+low+integrity+medium+integrity+high+integrity+UI+automation", "Integrity levels and UI access."),
        ("Window Safety", "Secure desktop Windows UAC UI automation limitations", "https://www.youtube.com/results?search_query=Secure+desktop+Windows+UAC+UI+automation+limitations", "Why secure desktop cannot be styled."),
        ("UI Automation", "UI Automation provider client patterns Windows", "https://www.youtube.com/results?search_query=UI+Automation+provider+client+patterns+Windows", "Provider/client mental model."),
        ("UI Automation", "UI Automation tree walker control view raw view", "https://www.youtube.com/results?search_query=UI+Automation+tree+walker+control+view+raw+view", "Tree views and inspection modes."),
        ("UI Automation", "UI Automation control patterns invoke value selection", "https://www.youtube.com/results?search_query=UI+Automation+control+patterns+invoke+value+selection", "Capability-level target inspection."),
        ("UI Automation", "Accessibility Insights for Windows FastPass tutorial", "https://www.youtube.com/results?search_query=Accessibility+Insights+for+Windows+FastPass+tutorial", "Quick accessibility checks."),
        ("UI Automation", "Accessibility Insights for Windows event monitoring", "https://www.youtube.com/results?search_query=Accessibility+Insights+for+Windows+event+monitoring", "Event/debugging workflows."),
        ("UI Automation", "Inspect.exe Windows SDK UI Automation tutorial", "https://www.youtube.com/results?search_query=Inspect.exe+Windows+SDK+UI+Automation+tutorial", "Inspect tool workflow."),
        ("UI Automation", "AccEvent Windows accessibility testing tutorial", "https://www.youtube.com/results?search_query=AccEvent+Windows+accessibility+testing+tutorial", "Event validation."),
        ("UI Automation", "Windows screen reader testing Narrator developer workflow", "https://www.youtube.com/results?search_query=Windows+screen+reader+testing+Narrator+developer+workflow", "Narrator testing habits."),
        ("UI Automation", "WCAG 2.2 desktop app accessibility testing", "https://www.youtube.com/results?search_query=WCAG+2.2+desktop+app+accessibility+testing", "Applying web guidance to desktop UI."),
        ("UI Automation", "ARIA Authoring Practices practical accessibility testing", "https://www.youtube.com/results?search_query=ARIA+Authoring+Practices+practical+accessibility+testing", "Interaction pattern testing."),
        ("UI Automation", "Keyboard accessibility testing Windows desktop apps", "https://www.youtube.com/results?search_query=Keyboard+accessibility+testing+Windows+desktop+apps", "Keyboard-first validation."),
        ("UI Automation", "High contrast mode Windows app testing", "https://www.youtube.com/results?search_query=High+contrast+mode+Windows+app+testing", "Contrast theme checks."),
        ("WinUI Roadmap", "WinUI 3 accessibility best practices", "https://www.youtube.com/results?search_query=WinUI+3+accessibility+best+practices", "Native accessibility patterns."),
        ("WinUI Roadmap", "WinUI 3 migration from WPF", "https://www.youtube.com/results?search_query=WinUI+3+migration+from+WPF", "Migration comparison."),
        ("WinUI Roadmap", "WinUI 3 migration from UWP", "https://www.youtube.com/results?search_query=WinUI+3+migration+from+UWP", "Windows App SDK migration."),
        ("WinUI Roadmap", "Windows App SDK migration guide", "https://www.youtube.com/results?search_query=Windows+App+SDK+migration+guide", "Future platform path."),
        ("WinUI Roadmap", "Windows App SDK windowing tutorial", "https://www.youtube.com/results?search_query=Windows+App+SDK+windowing+tutorial", "Modern window APIs."),
        ("WinUI Roadmap", "Windows App SDK app lifecycle tutorial", "https://www.youtube.com/results?search_query=Windows+App+SDK+app+lifecycle+tutorial", "Lifecycle and activation."),
        ("WinUI Roadmap", "WinUI 3 packaging MSIX unpackaged comparison", "https://www.youtube.com/results?search_query=WinUI+3+packaging+MSIX+unpackaged+comparison", "Distribution choices."),
        ("WinUI Roadmap", "WinUI 3 desktop app deployment", "https://www.youtube.com/results?search_query=WinUI+3+desktop+app+deployment", "Deployment planning."),
        ("WinUI Roadmap", "Windows Community Toolkit WinUI 3 examples", "https://www.youtube.com/results?search_query=Windows+Community+Toolkit+WinUI+3+examples", "Reusable Windows components."),
        ("Fluent Design", "Fluent 2 design system Windows apps", "https://www.youtube.com/results?search_query=Fluent+2+design+system+Windows+apps", "Current Microsoft design system."),
        ("Packaging Security", "Python packaging trusted publishing PyPI", "https://www.youtube.com/results?search_query=Python+packaging+trusted+publishing+PyPI", "Modern publish security."),
        ("Packaging Security", "PyPI digital attestations Python packages", "https://www.youtube.com/results?search_query=PyPI+digital+attestations+Python+packages", "Package provenance."),
        ("Packaging Security", "pip audit Python dependency security", "https://www.youtube.com/results?search_query=pip+audit+Python+dependency+security", "Dependency scanning."),
        ("Packaging Security", "Python wheel signing and supply chain security", "https://www.youtube.com/results?search_query=Python+wheel+signing+and+supply+chain+security", "Distribution trust."),
        ("Packaging Security", "Python packaging pyproject.toml best practices", "https://www.youtube.com/results?search_query=Python+packaging+pyproject.toml+best+practices", "Project packaging hygiene."),
        ("Packaging Security", "PyInstaller antivirus false positive mitigation", "https://www.youtube.com/results?search_query=PyInstaller+antivirus+false+positive+mitigation", "Common Windows packaging issue."),
        ("Packaging Security", "PyInstaller hidden imports hooks tutorial", "https://www.youtube.com/results?search_query=PyInstaller+hidden+imports+hooks+tutorial", "Robust executable builds."),
        ("Packaging Security", "Nuitka onefile vs standalone Windows", "https://www.youtube.com/results?search_query=Nuitka+onefile+vs+standalone+Windows", "Packaging tradeoff."),
        ("Packaging Security", "Nuitka code signing Windows app distribution", "https://www.youtube.com/results?search_query=Nuitka+code+signing+Windows+app+distribution", "Signed native builds."),
        ("Packaging Security", "Microsoft SignTool code signing certificate tutorial", "https://www.youtube.com/results?search_query=Microsoft+SignTool+code+signing+certificate+tutorial", "Authenticode workflow."),
        ("Packaging Security", "Windows SmartScreen code signing reputation explained", "https://www.youtube.com/results?search_query=Windows+SmartScreen+code+signing+reputation+explained", "Distribution trust model."),
        ("Packaging Security", "MSIX packaging and code signing desktop apps", "https://www.youtube.com/results?search_query=MSIX+packaging+and+code+signing+desktop+apps", "MSIX path."),
        ("Design Tokens", "CSS Color 4 OKLCH explained", "https://www.youtube.com/results?search_query=CSS+Color+4+OKLCH+explained", "Modern perceptual color."),
        ("Design Tokens", "OKLab OKLCH color spaces design systems", "https://www.youtube.com/results?search_query=OKLab+OKLCH+color+spaces+design+systems", "Future palette accuracy."),
        ("Design Tokens", "APCA contrast explained WCAG 3", "https://www.youtube.com/results?search_query=APCA+contrast+explained+WCAG+3", "Emerging contrast model."),
        ("Design Tokens", "WCAG 2.2 contrast non text contrast examples", "https://www.youtube.com/results?search_query=WCAG+2.2+contrast+non+text+contrast+examples", "UI boundaries and controls."),
        ("Design Tokens", "Material 3 dynamic color HCT explained", "https://www.youtube.com/results?search_query=Material+3+dynamic+color+HCT+explained", "Modern dynamic color systems."),
        ("Design Tokens", "Material color utilities tutorial", "https://www.youtube.com/results?search_query=Material+color+utilities+tutorial", "Reference implementation ideas."),
        ("Design Tokens", "Fluent 2 color tokens tutorial", "https://www.youtube.com/results?search_query=Fluent+2+color+tokens+tutorial", "Microsoft token model."),
        ("Design Tokens", "Design tokens W3C format tutorial", "https://www.youtube.com/results?search_query=Design+tokens+W3C+format+tutorial", "Portable theme exports."),
        ("Design Tokens", "Style Dictionary design tokens pipeline", "https://www.youtube.com/results?search_query=Style+Dictionary+design+tokens+pipeline", "Token build pipelines."),
        ("Design Tokens", "Design tokens Figma to code workflow", "https://www.youtube.com/results?search_query=Design+tokens+Figma+to+code+workflow", "Design-to-code workflow."),
        ("Design Tokens", "Dark mode tokens accessibility contrast", "https://www.youtube.com/results?search_query=Dark+mode+tokens+accessibility+contrast", "Dark palette quality."),
        ("UX Experimentation", "UX A/B testing Nielsen Norman Group", "https://www.youtube.com/results?search_query=UX+A%2FB+testing+Nielsen+Norman+Group", "Theme comparison methodology."),
        ("UX Experimentation", "UX experimentation platform Microsoft ExP", "https://www.youtube.com/results?search_query=UX+experimentation+platform+Microsoft+ExP", "Controlled experimentation."),
        ("UX Experimentation", "Controlled experiments product design", "https://www.youtube.com/results?search_query=Controlled+experiments+product+design", "Evidence-backed product changes."),
        ("UX Experimentation", "Quantitative UX research metrics tutorial", "https://www.youtube.com/results?search_query=Quantitative+UX+research+metrics+tutorial", "Measure theme performance."),
        ("UX Experimentation", "Task success rate UX testing", "https://www.youtube.com/results?search_query=Task+success+rate+UX+testing", "Workflow metrics."),
        ("UX Experimentation", "SUS score usability testing tutorial", "https://www.youtube.com/results?search_query=SUS+score+usability+testing+tutorial", "Usability questionnaire."),
        ("UX Experimentation", "Preference testing vs usability testing", "https://www.youtube.com/results?search_query=Preference+testing+vs+usability+testing", "Avoid shallow preference-only decisions."),
        ("UX Experimentation", "First click testing UX research", "https://www.youtube.com/results?search_query=First+click+testing+UX+research", "Navigation evaluation."),
        ("UX Experimentation", "Tree testing information architecture UX", "https://www.youtube.com/results?search_query=Tree+testing+information+architecture+UX", "Resource-library structure testing."),
        ("UX Experimentation", "Feature flag experiments desktop software", "https://www.youtube.com/results?search_query=Feature+flag+experiments+desktop+software", "Experiment rollout patterns."),
        ("UX Experimentation", "Telemetry privacy UX experimentation desktop apps", "https://www.youtube.com/results?search_query=Telemetry+privacy+UX+experimentation+desktop+apps", "Privacy-conscious measurement."),
    ]
)


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    pid: int = 0
    process: str = ""
    path: str = ""
    class_name: str = ""

    @property
    def display(self):
        process = self.process or "unknown"
        return f"{self.title}  [{process}, PID {self.pid}, 0x{self.hwnd:08X}]"


if IS_WINDOWS:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.IsHungAppWindow.argtypes = [wintypes.HWND]
    user32.IsHungAppWindow.restype = wintypes.BOOL
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
    if ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_longlong):
        user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.GetWindowLongPtrW.restype = ctypes.c_longlong
    else:
        user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.GetWindowLongW.restype = ctypes.c_long
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetForegroundWindow.argtypes = []
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
    user32.SetWindowTextW.restype = wintypes.BOOL

    dwmapi.DwmSetWindowAttribute.argtypes = [
        wintypes.HWND,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long
    dwmapi.DwmGetWindowAttribute.argtypes = [
        wintypes.HWND,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    dwmapi.DwmGetWindowAttribute.restype = ctypes.c_long
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
else:
    user32 = None
    dwmapi = None
    kernel32 = None
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
        self.experiment_variants = []
        self.favorite_rules = []
        self.recent_applies = []
        self.undo_stack = []
        self.live_job_id = None
        self.preview_update_job = None
        self.undo_snapshot = []
        self.last_apply_cache = {}

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
        self.target_search_var = tk.StringVar()
        self.interval_var = tk.StringVar(value="2.0")
        self.status_var = tk.StringVar(value="Ready")
        self.contrast_var = tk.StringVar()
        self.video_search_var = tk.StringVar()
        self.video_category_var = tk.StringVar(value="All")
        self.research_search_var = tk.StringVar()
        self.enforce_contrast_var = tk.BooleanVar(value=True)
        self.auto_fix_contrast_var = tk.BooleanVar(value=True)
        self.confirm_broad_apply_var = tk.BooleanVar(value=True)

        self.load_profiles()
        self.load_target_data()
        self.create_gui()
        self.apply_profile("Research blue")
        self.refresh_windows()
        self.refresh_video_list()
        self.refresh_research_list()
        self.update_preview()

    def create_gui(self):
        self.configure_style()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.skin_tab = ttk.Frame(notebook, padding=10)
        self.experiments_tab = ttk.Frame(notebook, padding=10)
        self.targets_tab = ttk.Frame(notebook, padding=10)
        self.videos_tab = ttk.Frame(notebook, padding=10)
        self.research_tab = ttk.Frame(notebook, padding=10)
        self.log_tab = ttk.Frame(notebook, padding=10)

        notebook.add(self.skin_tab, text="Skin Studio")
        notebook.add(self.experiments_tab, text="Experiments")
        notebook.add(self.targets_tab, text="Targets")
        notebook.add(self.videos_tab, text="Videos")
        notebook.add(self.research_tab, text="Research")
        notebook.add(self.log_tab, text="Log")

        self.create_skin_tab()
        self.create_experiments_tab()
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
            variable.trace_add("write", lambda *_: self.schedule_preview_update())
        self.video_search_var.trace_add("write", lambda *_: self.refresh_video_list())
        self.video_category_var.trace_add("write", lambda *_: self.refresh_video_list())
        self.research_search_var.trace_add("write", lambda *_: self.refresh_research_list())
        self.target_search_var.trace_add("write", lambda *_: self.refresh_target_tree())

        self.root.bind("<Control-r>", lambda _event: self.refresh_windows())
        self.root.bind("<Control-Return>", lambda _event: self.apply_once())
        self.root.bind("<Escape>", lambda _event: self.stop_live())
        self.root.bind("<Control-s>", lambda _event: self.save_profile())

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
        ttk.Button(profile_frame, text="Import", command=self.import_profiles).grid(row=1, column=2, padx=3, pady=(8, 0))
        ttk.Button(profile_frame, text="Export", command=self.export_profiles).grid(row=1, column=3, padx=3, pady=(8, 0))
        ttk.Button(profile_frame, text="Copy summary", command=self.copy_theme_summary).grid(
            row=1, column=4, padx=3, pady=(8, 0)
        )

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

        ttk.Checkbutton(
            controls,
            text="Require AA title contrast before apply",
            variable=self.enforce_contrast_var,
        ).grid(row=10, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Checkbutton(
            controls,
            text="Auto-fix low contrast with readable text color",
            variable=self.auto_fix_contrast_var,
        ).grid(row=11, column=0, columnspan=3, sticky="w")
        ttk.Checkbutton(
            controls,
            text="Confirm broad target scopes",
            variable=self.confirm_broad_apply_var,
        ).grid(row=12, column=0, columnspan=3, sticky="w")

        actions = ttk.Frame(controls)
        actions.grid(row=13, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        actions.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(actions, text="Apply once", style="Accent.TButton", command=self.apply_once).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(actions, text="Start live", command=self.start_live).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(actions, text="Stop", command=self.stop_live).grid(row=0, column=2, sticky="ew", padx=(4, 0))
        ttk.Button(actions, text="Preview targets", command=self.preview_targets).grid(
            row=1, column=0, sticky="ew", padx=(0, 4), pady=(8, 0)
        )
        ttk.Button(actions, text="Undo last apply", command=self.undo_last_apply).grid(
            row=1, column=1, sticky="ew", padx=4, pady=(8, 0)
        )
        ttk.Button(actions, text="Reset selected", command=self.reset_selected).grid(
            row=1, column=2, sticky="ew", padx=(4, 0), pady=(8, 0)
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
        palette_actions = ttk.Frame(preview)
        palette_actions.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        palette_actions.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(palette_actions, text="Complement border", command=self.derive_border_color).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(palette_actions, text="Random AA palette", command=self.generate_accessible_palette).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(palette_actions, text="Mutate palette", command=self.mutate_palette).grid(
            row=0, column=2, sticky="ew", padx=(4, 0)
        )

    def color_row(self, parent, row, label, variable):
        ttk.Label(parent, text=f"{label} color").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=4)
        ttk.Button(parent, text="Pick", command=lambda: self.pick_color(variable)).grid(
            row=row, column=2, padx=(8, 0), pady=4
        )

    def create_experiments_tab(self):
        self.experiments_tab.columnconfigure(0, weight=1)
        self.experiments_tab.rowconfigure(1, weight=1)

        toolbar = ttk.LabelFrame(self.experiments_tab, text="Palette Generator", padding=10)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar.columnconfigure((0, 1, 2, 3), weight=1)

        ttk.Button(toolbar, text="Generate 16 variants", command=self.generate_experiments).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(toolbar, text="Apply selected", command=self.apply_selected_experiment).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(toolbar, text="Save selected profile", command=self.save_selected_experiment).grid(
            row=0, column=2, sticky="ew", padx=4
        )
        ttk.Button(toolbar, text="Copy selected summary", command=self.copy_selected_experiment).grid(
            row=0, column=3, sticky="ew", padx=(4, 0)
        )

        self.experiment_tree = ttk.Treeview(
            self.experiments_tab,
            columns=("name", "caption", "text", "border", "contrast", "mode"),
            show="headings",
            height=18,
        )
        for column, heading, width in (
            ("name", "Variant", 220),
            ("caption", "Caption", 95),
            ("text", "Text", 95),
            ("border", "Border", 95),
            ("contrast", "Contrast", 90),
            ("mode", "DWM", 160),
        ):
            self.experiment_tree.heading(column, text=heading)
            self.experiment_tree.column(column, width=width, stretch=column == "name")
        self.experiment_tree.grid(row=1, column=0, sticky="nsew")
        self.experiment_tree.bind("<Double-1>", lambda _event: self.apply_selected_experiment())

        yscroll = ttk.Scrollbar(self.experiments_tab, orient="vertical", command=self.experiment_tree.yview)
        yscroll.grid(row=1, column=1, sticky="ns")
        self.experiment_tree.configure(yscrollcommand=yscroll.set)

        note = (
            "Variants keep title text at WCAG AA contrast or better, rotate hue in structured steps, "
            "and preserve current corner/backdrop choices so experiments stay safe to apply."
        )
        ttk.Label(self.experiments_tab, text=note, wraplength=900, justify="left", style="Muted.TLabel").grid(
            row=2, column=0, sticky="ew", pady=(10, 0)
        )
        self.generate_experiments()

    def create_targets_tab(self):
        self.targets_tab.columnconfigure(0, weight=1)
        self.targets_tab.rowconfigure(1, weight=1)

        scope = ttk.LabelFrame(self.targets_tab, text="Apply Scope", padding=10)
        scope.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for column in range(5):
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
        ttk.Radiobutton(scope, text="Favorite rules", variable=self.target_mode_var, value="favorites").grid(
            row=0, column=4, sticky="w"
        )
        ttk.Label(scope, text="Title filter").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(scope, textvariable=self.title_filter_var).grid(
            row=1, column=1, columnspan=4, sticky="ew", pady=(8, 0)
        )

        list_frame = ttk.LabelFrame(self.targets_tab, text="Visible Windows", padding=10)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)

        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        search_frame.columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Search targets").grid(row=0, column=0, sticky="w")
        ttk.Entry(search_frame, textvariable=self.target_search_var).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        self.target_tree = ttk.Treeview(
            list_frame,
            columns=("title", "process", "pid", "class", "hwnd"),
            show="headings",
            selectmode="extended",
            height=16,
        )
        for column, heading, width, stretch in (
            ("title", "Title", 360, True),
            ("process", "Process", 170, False),
            ("pid", "PID", 80, False),
            ("class", "Class", 170, False),
            ("hwnd", "HWND", 110, False),
        ):
            self.target_tree.heading(column, text=heading)
            self.target_tree.column(column, width=width, stretch=stretch)
        self.target_tree.grid(row=1, column=0, sticky="nsew")
        self.target_tree.bind("<Double-1>", lambda _event: self.apply_once())
        yscroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.target_tree.yview)
        yscroll.grid(row=1, column=1, sticky="ns")
        self.target_tree.configure(yscrollcommand=yscroll.set)

        target_actions = ttk.Frame(list_frame)
        target_actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        target_actions.columnconfigure((0, 1, 2, 3), weight=1)
        ttk.Button(target_actions, text="Refresh", command=self.refresh_windows).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(target_actions, text="Pick foreground in 2s", command=self.select_foreground_window).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(target_actions, text="Apply to selected", command=self.apply_once).grid(
            row=0, column=2, sticky="ew", padx=4
        )
        ttk.Button(target_actions, text="Copy target info", command=self.copy_selected_target_info).grid(
            row=0, column=3, sticky="ew", padx=(4, 0)
        )
        ttk.Button(target_actions, text="Favorite selected", command=self.favorite_selected_targets).grid(
            row=1, column=0, sticky="ew", padx=(0, 4), pady=(8, 0)
        )
        ttk.Button(target_actions, text="Remove favorite", command=self.remove_selected_favorites).grid(
            row=1, column=1, sticky="ew", padx=4, pady=(8, 0)
        )
        ttk.Button(target_actions, text="Apply favorites", command=self.apply_favorites).grid(
            row=1, column=2, sticky="ew", padx=4, pady=(8, 0)
        )
        ttk.Button(target_actions, text="Undo history", command=self.show_undo_history).grid(
            row=1, column=3, sticky="ew", padx=(4, 0), pady=(8, 0)
        )

        history_frame = ttk.LabelFrame(list_frame, text="Favorite Rules and Recent Applies", padding=8)
        history_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        history_frame.columnconfigure(0, weight=1)
        history_frame.columnconfigure(1, weight=1)

        self.favorite_tree = ttk.Treeview(
            history_frame,
            columns=("process", "class", "title"),
            show="headings",
            height=4,
            selectmode="extended",
        )
        for column, heading, width in (("process", "Process", 140), ("class", "Class", 140), ("title", "Title contains", 240)):
            self.favorite_tree.heading(column, text=heading)
            self.favorite_tree.column(column, width=width, stretch=column == "title")
        self.favorite_tree.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.recent_tree = ttk.Treeview(
            history_frame,
            columns=("time", "profile", "result", "targets"),
            show="headings",
            height=4,
        )
        for column, heading, width in (
            ("time", "Time", 90),
            ("profile", "Profile", 140),
            ("result", "Result", 90),
            ("targets", "Targets", 260),
        ):
            self.recent_tree.heading(column, text=heading)
            self.recent_tree.column(column, width=width, stretch=column == "targets")
        self.recent_tree.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.refresh_favorite_tree()
        self.refresh_recent_tree()

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
        self.research_tab.rowconfigure(1, weight=1)

        filters = ttk.Frame(self.research_tab)
        filters.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        filters.columnconfigure(1, weight=1)
        ttk.Label(filters, text="Search").grid(row=0, column=0, sticky="w")
        ttk.Entry(filters, textvariable=self.research_search_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(filters, text="Copy selected link", command=self.copy_selected_research_link).grid(
            row=0, column=2, sticky="e"
        )

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
        self.research_tree.grid(row=1, column=0, sticky="nsew")
        self.research_tree.bind("<Double-1>", lambda _event: self.open_selected_research())

        research_scroll = ttk.Scrollbar(self.research_tab, orient="vertical", command=self.research_tree.yview)
        research_scroll.grid(row=1, column=1, sticky="ns")
        self.research_tree.configure(yscrollcommand=research_scroll.set)

        notes = ttk.LabelFrame(self.research_tab, text="Implementation Notes", padding=10)
        notes.grid(row=2, column=0, sticky="ew", pady=(10, 0))
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
        log_actions = ttk.Frame(self.log_tab)
        log_actions.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        log_actions.columnconfigure((0, 1, 2, 3), weight=1)
        ttk.Button(log_actions, text="Run diagnostics", command=self.run_diagnostics).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(log_actions, text="Copy log", command=self.copy_log).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(log_actions, text="Save log", command=self.save_log).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(log_actions, text="Clear log", command=self.clear_log).grid(
            row=0, column=3, sticky="ew", padx=(4, 0)
        )

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

    def schedule_preview_update(self):
        if self.preview_update_job:
            self.root.after_cancel(self.preview_update_job)
        self.preview_update_job = self.root.after(80, self.update_preview)

    def update_preview(self):
        self.preview_update_job = None
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
        self.text_color_var.set(best_text_hex(caption_rgb))

    def derive_border_color(self):
        try:
            caption_rgb = hex_to_rgb(self.caption_color_var.get())
        except ValueError:
            messagebox.showerror(APP_NAME, "Enter a valid caption color first.")
            return
        hue, lightness, saturation = rgb_to_hls(caption_rgb)
        border = hls_to_hex((hue + 0.5) % 1.0, clamp(lightness + 0.12, 0.28, 0.76), clamp(saturation, 0.35, 0.82))
        self.border_color_var.set(border)

    def generate_accessible_palette(self):
        hue = random.random()
        lightness = random.choice((0.18, 0.24, 0.72, 0.82))
        saturation = random.uniform(0.42, 0.78)
        caption = hls_to_hex(hue, lightness, saturation)
        text = best_text_hex(hex_to_rgb(caption))
        border = hls_to_hex((hue + random.choice((0.33, 0.5, 0.66))) % 1.0, 0.58, clamp(saturation + 0.1, 0.35, 0.9))
        self.caption_color_var.set(caption)
        self.text_color_var.set(text)
        self.border_color_var.set(border)

    def mutate_palette(self):
        try:
            caption_rgb = hex_to_rgb(self.caption_color_var.get())
        except ValueError:
            self.generate_accessible_palette()
            return
        hue, lightness, saturation = rgb_to_hls(caption_rgb)
        hue = (hue + random.choice((-0.17, -0.08, 0.08, 0.17, 0.33))) % 1.0
        lightness = clamp(lightness + random.choice((-0.16, -0.08, 0.08, 0.16)), 0.16, 0.84)
        saturation = clamp(saturation + random.choice((-0.18, -0.08, 0.08, 0.18)), 0.32, 0.86)
        caption = hls_to_hex(hue, lightness, saturation)
        self.caption_color_var.set(caption)
        self.text_color_var.set(best_text_hex(hex_to_rgb(caption)))
        self.derive_border_color()

    def generate_experiments(self):
        if not hasattr(self, "experiment_tree"):
            return
        try:
            base_rgb = hex_to_rgb(self.caption_color_var.get())
        except ValueError:
            base_rgb = hex_to_rgb("#154c79")
        base_hue, base_lightness, base_saturation = rgb_to_hls(base_rgb)
        recipes = [
            ("Deep focus", 0.00, 0.20, 0.68, "Mica"),
            ("High-contrast signal", 0.03, 0.12, 0.92, "None"),
            ("Quiet graphite", 0.06, 0.24, 0.26, "Tabbed"),
            ("Readable light", 0.00, 0.82, 0.38, "Auto"),
            ("Complement lab", 0.50, 0.28, 0.68, "Mica"),
            ("Triad A", 0.33, 0.24, 0.72, "Mica"),
            ("Triad B", 0.66, 0.24, 0.72, "Mica"),
            ("Analog warm", 0.08, 0.30, 0.64, "Acrylic"),
            ("Analog cool", -0.08, 0.30, 0.64, "Acrylic"),
            ("Soft editorial", 0.12, 0.74, 0.34, "Auto"),
            ("Command surface", 0.42, 0.18, 0.58, "Tabbed"),
            ("Contrast stripe", 0.58, 0.16, 0.84, "None"),
        ]
        while len(recipes) < 16:
            recipes.append(
                (
                    f"Seeded variant {len(recipes) - 11}",
                    random.uniform(-0.45, 0.45),
                    random.choice((0.18, 0.24, 0.34, 0.72, 0.82)),
                    random.uniform(0.38, 0.82),
                    random.choice(list(BACKDROP_OPTIONS)),
                )
            )

        self.experiment_variants = []
        for name, hue_delta, lightness, saturation, backdrop in recipes:
            hue = (base_hue + hue_delta) % 1.0
            caption = hls_to_hex(hue, clamp(lightness, 0.12, 0.86), clamp(saturation, 0.20, 0.90))
            text = best_text_hex(hex_to_rgb(caption))
            border = hls_to_hex((hue + 0.5) % 1.0, clamp(base_lightness + 0.18, 0.36, 0.72), clamp(base_saturation + 0.12, 0.34, 0.86))
            ratio = contrast_ratio(hex_to_rgb(caption), hex_to_rgb(text))
            self.experiment_variants.append(
                {
                    "name": name,
                    "caption_color": caption,
                    "text_color": text,
                    "border_color": border,
                    "dark_mode": relative_luminance(hex_to_rgb(caption)) < 0.45,
                    "corner": self.corner_var.get(),
                    "backdrop": backdrop if backdrop in BACKDROP_OPTIONS else self.backdrop_var.get(),
                    "close_symbol": self.close_symbol_var.get()[:3] or "X",
                    "contrast": ratio,
                }
            )

        for item in self.experiment_tree.get_children():
            self.experiment_tree.delete(item)
        for index, variant in enumerate(self.experiment_variants):
            mode = f"{'Dark' if variant['dark_mode'] else 'Light'} / {variant['backdrop']}"
            self.experiment_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    variant["name"],
                    variant["caption_color"],
                    variant["text_color"],
                    variant["border_color"],
                    f"{variant['contrast']:.2f}:1",
                    mode,
                ),
            )
        self.status_var.set(f"Generated {len(self.experiment_variants)} accessible palette variants.")

    def selected_experiment(self):
        selection = self.experiment_tree.selection()
        if not selection:
            messagebox.showinfo(APP_NAME, "Select an experiment first.")
            return None
        return self.experiment_variants[int(selection[0])]

    def apply_selected_experiment(self):
        variant = self.selected_experiment()
        if not variant:
            return
        self.caption_color_var.set(variant["caption_color"])
        self.text_color_var.set(variant["text_color"])
        self.border_color_var.set(variant["border_color"])
        self.dark_mode_var.set(variant["dark_mode"])
        self.corner_var.set(variant["corner"])
        self.backdrop_var.set(variant["backdrop"])
        self.close_symbol_var.set(variant["close_symbol"])
        self.profile_var.set(f"Experiment: {variant['name']}")
        self.log(f"Applied experiment to composer: {variant['name']}")

    def save_selected_experiment(self):
        variant = self.selected_experiment()
        if not variant:
            return
        name = f"Experiment - {variant['name']}"
        counter = 2
        unique_name = name
        while unique_name in self.profiles:
            unique_name = f"{name} {counter}"
            counter += 1
        self.profiles[unique_name] = {
            key: variant[key]
            for key in ("caption_color", "text_color", "border_color", "dark_mode", "corner", "backdrop", "close_symbol")
        }
        self.user_profile_names.add(unique_name)
        self.persist_profiles()
        self.update_profile_values()
        self.profile_var.set(unique_name)
        self.log(f"Saved experiment profile: {unique_name}")

    def copy_selected_experiment(self):
        variant = self.selected_experiment()
        if not variant:
            return
        summary = self.format_theme_summary(variant, name=variant["name"])
        self.root.clipboard_clear()
        self.root.clipboard_append(summary)
        self.status_var.set("Copied experiment summary to clipboard.")


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

    def load_target_data(self):
        if not TARGET_RULES_PATH.exists():
            return
        try:
            payload = json.loads(TARGET_RULES_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.log(f"Could not load target state: {exc}")
            return
        if not isinstance(payload, dict):
            return
        favorites = payload.get("favorites", [])
        recents = payload.get("recents", [])
        if isinstance(favorites, list):
            self.favorite_rules = [rule for rule in (self.sanitize_target_rule(item) for item in favorites) if rule]
        if isinstance(recents, list):
            self.recent_applies = [item for item in recents if isinstance(item, dict)][:MAX_RECENT_APPLIES]

    def persist_target_data(self):
        payload = {
            "version": 1,
            "favorites": self.favorite_rules,
            "recents": self.recent_applies[:MAX_RECENT_APPLIES],
        }
        TARGET_RULES_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def sanitize_target_rule(self, rule):
        if not isinstance(rule, dict):
            return None
        process = str(rule.get("process", "")).strip()
        class_name = str(rule.get("class_name", "")).strip()
        title_contains = str(rule.get("title_contains", "")).strip()
        path = str(rule.get("path", "")).strip()
        if not any((process, class_name, title_contains, path)):
            return None
        return {
            "process": process,
            "class_name": class_name,
            "title_contains": title_contains,
            "path": path,
        }

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

    def export_profiles(self):
        file_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export OpenSkin profiles",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="openskin_profiles_export.json",
        )
        if not file_path:
            return
        payload = {
            "version": PROFILE_EXPORT_VERSION,
            "app": APP_NAME,
            "profiles": self.profiles,
            "user_profiles": sorted(self.user_profile_names),
        }
        try:
            Path(file_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not export profiles: {exc}")
            return
        self.status_var.set(f"Exported {len(self.profiles)} profile(s).")
        self.log(f"Exported profiles to {file_path}")

    def import_profiles(self):
        file_path = filedialog.askopenfilename(
            parent=self.root,
            title="Import OpenSkin profiles",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror(APP_NAME, f"Could not import profiles: {exc}")
            return
        incoming = payload.get("profiles", payload) if isinstance(payload, dict) else {}
        if not isinstance(incoming, dict):
            messagebox.showerror(APP_NAME, "Import file does not contain a profiles object.")
            return

        imported = 0
        skipped = 0
        for raw_name, raw_settings in incoming.items():
            if not isinstance(raw_name, str) or not isinstance(raw_settings, dict):
                skipped += 1
                continue
            try:
                settings = self.sanitize_profile_settings(raw_settings)
            except ValueError:
                skipped += 1
                continue
            name = raw_name.strip() or f"Imported profile {imported + 1}"
            if name in BUILT_IN_PROFILES:
                name = f"{name} imported"
            unique_name = name
            counter = 2
            while unique_name in self.profiles:
                unique_name = f"{name} {counter}"
                counter += 1
            self.profiles[unique_name] = settings
            self.user_profile_names.add(unique_name)
            imported += 1

        if imported:
            self.persist_profiles()
            self.update_profile_values()
        self.status_var.set(f"Imported {imported} profile(s); skipped {skipped}.")
        self.log(f"Imported profiles from {file_path}: {imported} imported, {skipped} skipped")

    def sanitize_profile_settings(self, settings):
        sanitized = {
            "caption_color": normalize_hex(settings.get("caption_color", "#154c79"), "Caption color"),
            "text_color": normalize_hex(settings.get("text_color", "#ffffff"), "Text color"),
            "border_color": normalize_hex(settings.get("border_color", "#4db6ac"), "Border color"),
            "dark_mode": bool(settings.get("dark_mode", True)),
            "corner": settings.get("corner", "Rounded"),
            "backdrop": settings.get("backdrop", "Mica"),
            "close_symbol": str(settings.get("close_symbol", "X"))[:3] or "X",
            "texture_path": str(settings.get("texture_path", "")),
        }
        if sanitized["corner"] not in CORNER_OPTIONS:
            sanitized["corner"] = "Rounded"
        if sanitized["backdrop"] not in BACKDROP_OPTIONS:
            sanitized["backdrop"] = "Mica"
        return sanitized

    def copy_theme_summary(self):
        try:
            settings = self.snapshot_settings()
        except ValueError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        summary = self.format_theme_summary(settings, name=self.profile_var.get().strip() or "Unsaved profile")
        self.root.clipboard_clear()
        self.root.clipboard_append(summary)
        self.status_var.set("Copied theme summary to clipboard.")

    def format_theme_summary(self, settings, name="Theme"):
        ratio = contrast_ratio(hex_to_rgb(settings["caption_color"]), hex_to_rgb(settings["text_color"]))
        return "\n".join(
            [
                f"OpenSkin theme: {name}",
                f"Caption: {settings['caption_color']}",
                f"Text: {settings['text_color']}",
                f"Border: {settings['border_color']}",
                f"Contrast: {ratio:.2f}:1",
                f"Dark mode: {settings.get('dark_mode', False)}",
                f"Corners: {settings.get('corner', 'Rounded')}",
                f"Backdrop: {settings.get('backdrop', 'Mica')}",
            ]
        )

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
        self.refresh_target_tree()
        self.status_var.set(f"Found {len(self.visible_windows)} visible titled windows.")
        self.log(f"Refreshed windows: {len(self.visible_windows)} visible titled windows")

    def refresh_target_tree(self):
        if not hasattr(self, "target_tree"):
            return
        for item in self.target_tree.get_children():
            self.target_tree.delete(item)
        query = self.target_search_var.get().strip().casefold()
        shown = 0
        for index, window in enumerate(self.visible_windows):
            if query and not self.window_matches_target_search(window, query):
                continue
            self.target_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    window.title,
                    window.process or "unknown",
                    window.pid or "",
                    window.class_name or "",
                    f"0x{window.hwnd:08X}",
                ),
            )
            shown += 1
        if query:
            self.status_var.set(f"Showing {shown}/{len(self.visible_windows)} target window(s).")

    def window_matches_target_search(self, window, query):
        haystack = " ".join(
            [
                window.title,
                window.process,
                str(window.pid),
                window.class_name,
                f"0x{window.hwnd:08X}",
                window.path,
            ]
        ).casefold()
        return query in haystack

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
            if not user32.IsWindow(hwnd) or not user32.IsWindowVisible(hwnd):
                return True
            hwnd_int = int(hwnd)
            if own_hwnd and hwnd_int == own_hwnd:
                return True
            if self.is_tool_window(hwnd_int) or self.is_cloaked_window(hwnd_int) or user32.IsHungAppWindow(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value.strip()
            if title and title != APP_NAME:
                pid, process, path = self.window_process_info(hwnd_int)
                windows.append(
                    WindowInfo(
                        hwnd=hwnd_int,
                        title=title,
                        pid=pid,
                        process=process,
                        path=path,
                        class_name=self.window_class_name(hwnd_int),
                    )
                )
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
        self.target_tree.selection_remove(self.target_tree.selection())
        for index, item in enumerate(self.visible_windows):
            if item.hwnd == hwnd:
                iid = str(index)
                if not self.target_tree.exists(iid):
                    self.target_search_var.set("")
                    self.refresh_target_tree()
                self.target_tree.selection_set(iid)
                self.target_tree.see(iid)
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
            return [hwnd] if hwnd and not self.is_own_window(hwnd) else []
        if mode == "title_contains":
            needle = self.title_filter_var.get().strip().casefold()
            if not needle:
                raise ValueError("Enter text for the title filter.")
            return [
                item.hwnd
                for item in self.visible_windows
                if needle in item.title.casefold() and self.is_valid_target_hwnd(item.hwnd)
            ]
        if mode == "all_visible":
            return [item.hwnd for item in self.visible_windows if self.is_valid_target_hwnd(item.hwnd)]
        if mode == "favorites":
            return [item.hwnd for item in self.favorite_target_windows()]

        return [window.hwnd for window in self.selected_window_infos() if self.is_valid_target_hwnd(window.hwnd)]

    def favorite_target_windows(self):
        matches = []
        seen = set()
        for window in self.visible_windows:
            if not self.is_valid_target_hwnd(window.hwnd):
                continue
            if any(self.window_matches_rule(window, rule) for rule in self.favorite_rules):
                if window.hwnd not in seen:
                    matches.append(window)
                    seen.add(window.hwnd)
        return matches

    def window_matches_rule(self, window, rule):
        process = rule.get("process", "").casefold()
        class_name = rule.get("class_name", "").casefold()
        title_contains = rule.get("title_contains", "").casefold()
        path = rule.get("path", "").casefold()
        if process and process != (window.process or "").casefold():
            return False
        if class_name and class_name != (window.class_name or "").casefold():
            return False
        if title_contains and title_contains not in (window.title or "").casefold():
            return False
        if path and path != (window.path or "").casefold():
            return False
        return True

    def selected_window_infos(self):
        if not hasattr(self, "target_tree"):
            return []
        windows = []
        for iid in self.target_tree.selection():
            try:
                windows.append(self.visible_windows[int(iid)])
            except (ValueError, IndexError):
                continue
        return windows

    def is_own_window(self, hwnd):
        try:
            return int(hwnd) == int(self.root.winfo_id()) or self.window_title_for_hwnd(hwnd) == APP_NAME
        except tk.TclError:
            return False

    def is_valid_target_hwnd(self, hwnd):
        if not IS_WINDOWS or not user32.IsWindow(wintypes.HWND(hwnd)):
            return False
        if self.is_own_window(hwnd):
            return False
        if self.is_cloaked_window(hwnd) or self.is_tool_window(hwnd):
            return False
        return True

    def copy_selected_target_info(self):
        selected = self.selected_window_infos()
        if not selected:
            messagebox.showinfo(APP_NAME, "Select at least one target window first.")
            return
        lines = []
        for window in selected:
            lines.extend(
                [
                    f"Title: {window.title}",
                    f"Process: {window.process or 'unknown'}",
                    f"PID: {window.pid or 'unknown'}",
                    f"Class: {window.class_name or 'unknown'}",
                    f"HWND: 0x{window.hwnd:08X}",
                    f"Path: {window.path or 'unavailable'}",
                    "",
                ]
            )
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(lines).strip())
        self.status_var.set(f"Copied {len(selected)} target record(s).")

    def favorite_selected_targets(self):
        selected = self.selected_window_infos()
        if not selected:
            messagebox.showinfo(APP_NAME, "Select at least one target window first.")
            return
        added = 0
        for window in selected:
            rule = {
                "process": window.process,
                "class_name": window.class_name,
                "title_contains": compact_title_pattern(window.title),
                "path": window.path,
            }
            if not any(target_rules_equal(rule, existing) for existing in self.favorite_rules):
                self.favorite_rules.append(rule)
                added += 1
        self.persist_target_data()
        self.refresh_favorite_tree()
        self.status_var.set(f"Added {added} favorite target rule(s).")

    def remove_selected_favorites(self):
        if not hasattr(self, "favorite_tree"):
            return
        selected = sorted((int(iid) for iid in self.favorite_tree.selection()), reverse=True)
        if not selected:
            messagebox.showinfo(APP_NAME, "Select at least one favorite rule first.")
            return
        for index in selected:
            if 0 <= index < len(self.favorite_rules):
                del self.favorite_rules[index]
        self.persist_target_data()
        self.refresh_favorite_tree()
        self.status_var.set(f"Removed {len(selected)} favorite rule(s).")

    def apply_favorites(self):
        self.target_mode_var.set("favorites")
        self.apply_once()

    def refresh_favorite_tree(self):
        if not hasattr(self, "favorite_tree"):
            return
        for item in self.favorite_tree.get_children():
            self.favorite_tree.delete(item)
        for index, rule in enumerate(self.favorite_rules):
            self.favorite_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    rule.get("process", "") or "*",
                    rule.get("class_name", "") or "*",
                    rule.get("title_contains", "") or "*",
                ),
            )

    def refresh_recent_tree(self):
        if not hasattr(self, "recent_tree"):
            return
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        for index, item in enumerate(self.recent_applies[:MAX_RECENT_APPLIES]):
            self.recent_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    item.get("time", ""),
                    item.get("profile", ""),
                    item.get("result", ""),
                    item.get("targets", ""),
                ),
            )

    def preview_targets(self):
        if not IS_WINDOWS:
            messagebox.showerror(APP_NAME, "OpenSkin can only resolve targets on Windows.")
            return
        try:
            settings = self.prepare_settings_for_apply(self.snapshot_settings())
            targets = self.target_windows()
        except ValueError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        if not targets:
            messagebox.showinfo(APP_NAME, "No target windows match the current scope.")
            return
        target_lines = self.describe_targets(targets, limit=24)
        ratio = contrast_ratio(hex_to_rgb(settings["caption_color"]), hex_to_rgb(settings["text_color"]))
        messagebox.showinfo(
            APP_NAME,
            f"{len(targets)} window(s) would be changed.\n"
            f"Contrast: {ratio:.2f}:1\n"
            f"Scope: {self.target_mode_var.get()}\n\n{target_lines}",
        )

    def apply_once(self, quiet=False):
        if not IS_WINDOWS:
            messagebox.showerror(APP_NAME, "OpenSkin can only apply skins on Windows.")
            return
        try:
            settings = self.prepare_settings_for_apply(self.snapshot_settings())
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

        if not quiet and not self.confirm_target_scope(targets):
            self.status_var.set("Apply cancelled.")
            return

        successes = 0
        failures = []
        signature = settings_signature(settings)
        if quiet and targets and all(self.last_apply_cache.get(hwnd) == signature for hwnd in targets):
            self.status_var.set(f"Live apply skipped; {len(targets)} window(s) already match.")
            return
        self.capture_undo_snapshot(targets)
        for hwnd in targets:
            if quiet and self.last_apply_cache.get(hwnd) == signature:
                successes += 1
                continue
            ok, messages = self.apply_to_window(hwnd, settings)
            if ok:
                successes += 1
                self.last_apply_cache[hwnd] = signature
            else:
                failures.append(f"0x{hwnd:08X}: {'; '.join(messages)}")

        summary = f"Applied skin to {successes}/{len(targets)} window(s)."
        if failures:
            summary += f" {len(failures)} failure(s); see log."
            for failure in failures[:8]:
                self.log(f"Apply failed: {failure}")
        self.status_var.set(summary)
        self.log(summary)
        self.record_recent_apply(targets, successes, failures)

    def prepare_settings_for_apply(self, settings):
        ratio = contrast_ratio(hex_to_rgb(settings["caption_color"]), hex_to_rgb(settings["text_color"]))
        if ratio >= MIN_TEXT_CONTRAST or not self.enforce_contrast_var.get():
            return settings
        if self.auto_fix_contrast_var.get():
            fixed_text = best_text_hex(hex_to_rgb(settings["caption_color"]))
            settings["text_color"] = fixed_text
            self.text_color_var.set(fixed_text)
            self.log(f"Auto-fixed title text color for AA contrast: {fixed_text}")
            return settings
        raise ValueError(f"Title contrast is {ratio:.2f}:1; AA normal text target is {MIN_TEXT_CONTRAST}:1.")

    def confirm_target_scope(self, targets):
        mode = self.target_mode_var.get()
        if not self.confirm_broad_apply_var.get():
            return True
        if mode not in ("all_visible", "title_contains") and len(targets) <= BROAD_TARGET_LIMIT:
            return True
        target_lines = self.describe_targets(targets, limit=12)
        return messagebox.askyesno(
            APP_NAME,
            f"Apply to {len(targets)} window(s)?\n\n{target_lines}\n\nThis can affect unrelated apps.",
        )

    def describe_targets(self, targets, limit=12):
        lines = []
        for hwnd in targets[:limit]:
            title = self.window_title_for_hwnd(hwnd) or "(untitled)"
            pid, process, _path = self.window_process_info(hwnd)
            class_name = self.window_class_name(hwnd)
            identity = process or class_name or "unknown"
            lines.append(f"0x{hwnd:08X} - {identity} PID {pid or '?'} - {title}")
        if len(targets) > limit:
            lines.append(f"...and {len(targets) - limit} more")
        return "\n".join(lines)

    def record_recent_apply(self, targets, successes, failures):
        target_names = []
        for hwnd in targets[:4]:
            pid, process, _path = self.window_process_info(hwnd)
            title = self.window_title_for_hwnd(hwnd)
            target_names.append(f"{process or 'unknown'}:{title[:40] or hex(hwnd)}")
        if len(targets) > 4:
            target_names.append(f"+{len(targets) - 4} more")
        record = {
            "time": time.strftime("%H:%M:%S"),
            "profile": self.profile_var.get().strip() or "Unsaved",
            "result": f"{successes}/{len(targets)}",
            "targets": "; ".join(target_names),
            "failures": len(failures),
        }
        self.recent_applies.insert(0, record)
        self.recent_applies = self.recent_applies[:MAX_RECENT_APPLIES]
        self.persist_target_data()
        self.refresh_recent_tree()

    def capture_undo_snapshot(self, targets):
        snapshot = []
        for hwnd in targets:
            item = {
                "hwnd": hwnd,
                "title": self.window_title_for_hwnd(hwnd),
                "attrs": {},
            }
            for attr in (
                DWMWA_CAPTION_COLOR,
                DWMWA_TEXT_COLOR,
                DWMWA_BORDER_COLOR,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                DWMWA_SYSTEMBACKDROP_TYPE,
            ):
                ok, value = self.dwm_get_dword(hwnd, attr)
                if ok:
                    item["attrs"][attr] = value
            snapshot.append(item)
        self.undo_snapshot = snapshot
        self.undo_stack.insert(
            0,
            {
                "time": time.strftime("%H:%M:%S"),
                "profile": self.profile_var.get().strip() or "Unsaved",
                "targets": len(targets),
                "snapshot": snapshot,
            },
        )
        self.undo_stack = self.undo_stack[:MAX_UNDO_STACK]

    def undo_last_apply(self):
        if not IS_WINDOWS:
            messagebox.showerror(APP_NAME, "OpenSkin undo is only available on Windows.")
            return
        if not self.undo_stack and not self.undo_snapshot:
            messagebox.showinfo(APP_NAME, "There is no apply operation to undo.")
            return
        entry = self.undo_stack.pop(0) if self.undo_stack else {"snapshot": self.undo_snapshot}
        snapshot = entry.get("snapshot", [])
        failures = []
        for item in snapshot:
            hwnd = item["hwnd"]
            if not user32.IsWindow(wintypes.HWND(hwnd)):
                failures.append(f"0x{hwnd:08X}: window no longer exists")
                continue
            if item.get("title"):
                user32.SetWindowTextW(wintypes.HWND(hwnd), item["title"])
            for attr, value in item.get("attrs", {}).items():
                ok, message = self.dwm_set_dword(hwnd, attr, value)
                if not ok:
                    failures.append(f"0x{hwnd:08X}: {message}")
            self.last_apply_cache.pop(hwnd, None)
        summary = f"Undid last apply for {len(snapshot)} window(s)."
        if failures:
            summary += f" {len(failures)} restore warning(s); see log."
            for failure in failures[:8]:
                self.log(f"Undo warning: {failure}")
        self.status_var.set(summary)
        self.log(summary)
        self.undo_snapshot = self.undo_stack[0].get("snapshot", []) if self.undo_stack else []

    def show_undo_history(self):
        if not self.undo_stack:
            messagebox.showinfo(APP_NAME, "Undo history is empty.")
            return
        lines = [
            f"{index + 1}. {entry.get('time', '')} - {entry.get('profile', '')} - {entry.get('targets', 0)} target(s)"
            for index, entry in enumerate(self.undo_stack)
        ]
        messagebox.showinfo(APP_NAME, "\n".join(lines))

    def apply_to_window(self, hwnd, settings):
        messages = []
        success = True
        if not self.is_valid_target_hwnd(hwnd):
            return False, ["Target window is no longer valid or is filtered for safety."]

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
            self.last_apply_cache.pop(hwnd, None)
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
        try:
            targets = self.target_windows()
        except ValueError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        if not targets:
            messagebox.showinfo(APP_NAME, "Choose at least one target window before starting live apply.")
            return
        if not self.confirm_target_scope(targets):
            self.status_var.set("Live apply cancelled.")
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

    def window_title_for_hwnd(self, hwnd):
        if not IS_WINDOWS:
            return ""
        length = user32.GetWindowTextLengthW(wintypes.HWND(hwnd))
        if length <= 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(wintypes.HWND(hwnd), buffer, length + 1)
        return buffer.value.strip()

    def window_class_name(self, hwnd):
        if not IS_WINDOWS:
            return ""
        buffer = ctypes.create_unicode_buffer(256)
        length = user32.GetClassNameW(wintypes.HWND(hwnd), buffer, len(buffer))
        return buffer.value[:length] if length > 0 else ""

    def window_process_info(self, hwnd):
        if not IS_WINDOWS:
            return 0, "", ""
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(pid))
        process_path = self.process_path_for_pid(pid.value)
        process_name = Path(process_path).name if process_path else ""
        return int(pid.value), process_name, process_path

    def process_path_for_pid(self, pid):
        if not IS_WINDOWS or not pid:
            return ""
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return ""
        try:
            size = wintypes.DWORD(32768)
            buffer = ctypes.create_unicode_buffer(size.value)
            if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                return buffer.value[: size.value]
            return ""
        finally:
            kernel32.CloseHandle(handle)

    def window_ex_style(self, hwnd):
        if not IS_WINDOWS:
            return 0
        if ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_longlong):
            return int(user32.GetWindowLongPtrW(wintypes.HWND(hwnd), GWL_EXSTYLE))
        return int(user32.GetWindowLongW(wintypes.HWND(hwnd), GWL_EXSTYLE))

    def is_tool_window(self, hwnd):
        return bool(self.window_ex_style(hwnd) & WS_EX_TOOLWINDOW)

    def is_cloaked_window(self, hwnd):
        ok, value = self.dwm_get_dword(hwnd, DWMWA_CLOAKED)
        return ok and value != 0

    def dwm_get_dword(self, hwnd, attr):
        data = wintypes.DWORD()
        result = dwmapi.DwmGetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(attr),
            ctypes.byref(data),
            ctypes.sizeof(data),
        )
        if result != 0:
            return False, 0
        return True, int(data.value)

    def dwm_set_dword(self, hwnd, attr, value):
        data = wintypes.DWORD(value & 0xFFFFFFFF)
        result = dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(attr),
            ctypes.byref(data),
            ctypes.sizeof(data),
        )
        if result != 0:
            return False, f"DwmSetWindowAttribute({attr}) failed: {format_hresult(result)}"
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
            return False, f"DwmSetWindowAttribute({attr}) failed: {format_hresult(result)}"
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

    def refresh_research_list(self):
        if not hasattr(self, "research_tree"):
            return
        for item in self.research_tree.get_children():
            self.research_tree.delete(item)
        query = self.research_search_var.get().strip().casefold()
        count = 0
        for index, item in enumerate(RESEARCH_LINKS):
            haystack = f"{item.get('title', '')} {item.get('note', '')} {item.get('url', '')}".casefold()
            if query and query not in haystack:
                continue
            self.research_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(item.get("title", ""), item.get("note", ""), item.get("url", "")),
            )
            count += 1
        if query:
            self.status_var.set(f"Showing {count}/{len(RESEARCH_LINKS)} research source(s).")

    def selected_research_url(self):
        selection = self.research_tree.selection()
        if not selection:
            return None
        index = int(selection[0])
        return RESEARCH_LINKS[index]["url"]

    def copy_selected_research_link(self):
        url = self.selected_research_url()
        if not url:
            messagebox.showinfo(APP_NAME, "Select a research source first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.status_var.set("Copied research link to clipboard.")

    def open_selected_research(self):
        url = self.selected_research_url()
        if not url:
            messagebox.showinfo(APP_NAME, "Select a research source first.")
            return
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

    def log_contents(self):
        self.log_text.configure(state="normal")
        contents = self.log_text.get("1.0", tk.END).strip()
        self.log_text.configure(state="disabled")
        return contents

    def copy_log(self):
        contents = self.log_contents()
        if not contents:
            self.status_var.set("Log is empty.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(contents)
        self.status_var.set("Copied log to clipboard.")

    def save_log(self):
        file_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save OpenSkin log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"openskin-log-{time.strftime('%Y%m%d-%H%M%S')}.txt",
        )
        if not file_path:
            return
        try:
            Path(file_path).write_text(self.log_contents() + "\n", encoding="utf-8")
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not save log: {exc}")
            return
        self.status_var.set(f"Saved log to {file_path}")

    def run_diagnostics(self):
        self.log("Diagnostics started")
        self.log(f"Platform: os.name={os.name}; Windows APIs loaded={IS_WINDOWS}")
        self.log(f"Profiles: {len(self.profiles)} total, {len(self.user_profile_names)} user")
        self.log(f"Resources: {len(VIDEO_LIBRARY)} videos/searches, {len(RESEARCH_LINKS)} research links")
        try:
            settings = self.snapshot_settings()
            ratio = contrast_ratio(hex_to_rgb(settings["caption_color"]), hex_to_rgb(settings["text_color"]))
            self.log(f"Current theme contrast: {ratio:.2f}:1")
        except ValueError as exc:
            self.log(f"Current theme invalid: {exc}")
        if IS_WINDOWS:
            self.log(f"OpenSkin HWND: 0x{int(self.root.winfo_id()):08X}")
            selected = self.selected_window_infos()
            self.log(f"Visible target rows: {len(self.visible_windows)}; selected rows: {len(selected)}")
            for window in selected[:8]:
                self.log(
                    "Target: "
                    f"0x{window.hwnd:08X}, pid={window.pid}, process={window.process or 'unknown'}, "
                    f"class={window.class_name or 'unknown'}, title={window.title}"
                )
        self.log("Diagnostics complete")

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
    value = str(value).strip().lower()
    if not is_hex_color(value):
        raise ValueError(f"{label} must be a #RRGGBB color.")
    return value


def hex_to_rgb(value):
    value = normalize_hex(value, "Color")
    return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)


def colorref_from_hex(value):
    red, green, blue = hex_to_rgb(value)
    return red | (green << 8) | (blue << 16)


def rgb_to_hex(rgb):
    red, green, blue = (int(clamp(component, 0, 255)) for component in rgb)
    return f"#{red:02x}{green:02x}{blue:02x}"


def rgb_to_hls(rgb):
    red, green, blue = (component / 255 for component in rgb)
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    return hue, lightness, saturation


def hls_to_hex(hue, lightness, saturation):
    red, green, blue = colorsys.hls_to_rgb(hue % 1.0, clamp(lightness, 0, 1), clamp(saturation, 0, 1))
    return rgb_to_hex((round(red * 255), round(green * 255), round(blue * 255)))


def best_text_hex(background_rgb):
    black_ratio = contrast_ratio(background_rgb, (0, 0, 0))
    white_ratio = contrast_ratio(background_rgb, (255, 255, 255))
    return "#000000" if black_ratio >= white_ratio else "#ffffff"


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


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


def format_hresult(result):
    code = result & 0xFFFFFFFF
    known = {
        0x80070005: "access denied; the target may be elevated or protected",
        0x80070006: "invalid handle; the window may have closed",
        0x80070057: "invalid argument; this DWM attribute may not apply to the target",
        0x88980778: "DWM composition is unavailable or the target cannot be composed",
    }
    detail = known.get(code)
    if detail:
        return f"HRESULT 0x{code:08X} ({detail})"
    return f"HRESULT 0x{code:08X}"


def compact_title_pattern(title):
    words = [word for word in str(title).replace("-", " ").split() if len(word) > 2]
    if not words:
        return str(title)[:40]
    return " ".join(words[:4])[:60]


def target_rules_equal(first, second):
    keys = ("process", "class_name", "title_contains", "path")
    return all(str(first.get(key, "")).casefold() == str(second.get(key, "")).casefold() for key in keys)


def settings_signature(settings):
    return json.dumps(settings, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    app = OpenSkinLab()
    app.run()
