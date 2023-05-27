from threading import Thread
import ctypes
import time
import tkinter as tk
from tkinter import filedialog
from tkinter.colorchooser import askcolor
from ctypes import WINFUNCTYPE, c_bool, c_void_p, c_int, c_long, POINTER


WNDENUMPROC = WINFUNCTYPE(c_bool, c_void_p, c_long)


class WindowCustomizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Window Customizer")

        self.titlebar_color_var = tk.StringVar()
        self.text_color_var = tk.StringVar()
        self.window_title_var = tk.StringVar()
        self.close_button_unicode_var = tk.StringVar()
        self.skin_texture_path = None

        self.running = False

        self.create_gui()

    def create_gui(self):
        # Titlebar Color
        titlebar_color_label = tk.Label(self.root, text="Titlebar Color:")
        titlebar_color_label.grid(row=0, column=0)
        titlebar_color_entry = tk.Entry(self.root, textvariable=self.titlebar_color_var)
        titlebar_color_entry.grid(row=0, column=1)
        titlebar_color_button = tk.Button(self.root, text="Pick Color", command=self.pick_titlebar_color)
        titlebar_color_button.grid(row=0, column=2)

        # Text Color
        text_color_label = tk.Label(self.root, text="Text Color:")
        text_color_label.grid(row=1, column=0)
        text_color_entry = tk.Entry(self.root, textvariable=self.text_color_var)
        text_color_entry.grid(row=1, column=1)
        text_color_button = tk.Button(self.root, text="Pick Color", command=self.pick_text_color)
        text_color_button.grid(row=1, column=2)

        # Window Title
        window_title_label = tk.Label(self.root, text="Window Title:")
        window_title_label.grid(row=2, column=0)
        window_title_entry = tk.Entry(self.root, textvariable=self.window_title_var)
        window_title_entry.grid(row=2, column=1)

        # Close Button Unicode
        close_button_unicode_label = tk.Label(self.root, text="Close Button Unicode:")
        close_button_unicode_label.grid(row=3, column=0)
        close_button_unicode_entry = tk.Entry(self.root, textvariable=self.close_button_unicode_var)
        close_button_unicode_entry.grid(row=3, column=1)

        # Skin Texture
        skin_texture_label = tk.Label(self.root, text="Skin Texture:")
        skin_texture_label.grid(row=4, column=0)
        skin_texture_button = tk.Button(self.root, text="Upload", command=self.upload_skin_texture)
        skin_texture_button.grid(row=4, column=1)

        # Apply Button
        apply_button = tk.Button(self.root, text="Apply Changes", command=self.apply_changes)
        apply_button.grid(row=5, column=0)

        # Stop Button
        stop_button = tk.Button(self.root, text="Stop", command=self.stop_customizer)
        stop_button.grid(row=5, column=1)

    def pick_titlebar_color(self):
        color = askcolor()[0]
        self.titlebar_color_var.set(','.join(map(str, color)))

    def pick_text_color(self):
        color = askcolor()[0]
        self.text_color_var.set(','.join(map(str, color)))

    def upload_skin_texture(self):
        file_path = filedialog.askopenfilename()
        self.skin_texture_path = file_path

    def set_window_colors(self, window_handle, titlebar_color, text_color):
        user32 = ctypes.windll.user32
        user32.SetSysColors(1, ctypes.byref(ctypes.c_int(1)), ctypes.byref(ctypes.c_ulong(titlebar_color)))

    def set_window_close_button(self, window_handle, close_button_unicode):
        close_button_unicode = int(close_button_unicode, 16)
        user32 = ctypes.windll.user32
        dw_style = user32.GetWindowLongW(window_handle, ctypes.c_int(-16))
        dw_style = dw_style | 0x00080000  # WS_CAPTION (0x00C00000) + WS_SYSMENU (0x00080000)
        user32.SetWindowLongW(window_handle, ctypes.c_int(-16), dw_style)
        user32.DrawMenuBar(window_handle)

    def set_window_transparent(self, window_handle):
        user32 = ctypes.windll.user32
        user32.SetWindowLongW(window_handle, -20, 524288 | 32)
        user32.SetLayeredWindowAttributes(window_handle, 0, 255, 2)

    def set_window_fullscreen(self, window_handle):
        user32 = ctypes.windll.user32
        user32.ShowWindow(window_handle, 3)

    def set_window_title_font(self, window_handle, font_name, font_size):
        gdi32 = ctypes.windll.gdi32
        user32 = ctypes.windll.user32
        h_font = gdi32.CreateFontW(-int(font_size), 0, 0, 0, 700, False, False, False, 0, 0, 0, 0, 0, font_name)
        user32.SendMessageW(window_handle, 48, h_font, True)

    def set_window_skin_texture(self, window_handle, skin_texture_path):
        user32 = ctypes.windll.user32
        user32.SetWindowTheme(window_handle, "", "")

        # Load the skin texture
        if skin_texture_path:
            user32.SetWindowTheme(window_handle, skin_texture_path, "")

    def modify_window(self, window_handle):
        titlebar_color = self.get_titlebar_color()
        text_color = self.get_text_color()
        window_title = self.window_title_var.get()
        close_button_unicode = self.close_button_unicode_var.get()
        skin_texture_path = self.skin_texture_path

        self.set_window_colors(window_handle, titlebar_color, text_color)
        self.set_window_close_button(window_handle, close_button_unicode)
        self.set_window_title_font(window_handle, "Arial", 16)

        if skin_texture_path:
            self.set_window_skin_texture(window_handle, skin_texture_path)

        user32 = ctypes.windll.user32
        user32.RedrawWindow(window_handle, None, None, 0x0401)

    def modify_all_windows(self):
        def enum_windows_callback(window_handle, _):
            self.modify_window(window_handle)
            return True

        user32 = ctypes.windll.user32
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

    def apply_changes(self):
        if self.running:
            return

        self.running = True
        thread = Thread(target=self.modify_all_windows)
        thread.start()

    def stop_customizer(self):
        self.running = False

    def get_titlebar_color(self):
        return tuple(map(int, self.titlebar_color_var.get().split(',')))

    def get_text_color(self):
        return tuple(map(int, self.text_color_var.get().split(',')))


if __name__ == '__main__':
    customizer = WindowCustomizer()
    customizer.root.mainloop()
