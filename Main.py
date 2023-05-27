
from threading import Thread
import ctypes
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
        color = askcolor()[1]
        self.titlebar_color_var.set(color)

    def pick_text_color(self):
        color = askcolor()[1]
        self.text_color_var.set(color)

    def upload_skin_texture(self):
        file_path = filedialog.askopenfilename()
        self.skin_texture_path = file_path

    def rgb_to_int(self, rgb):
        return rgb[0] | (rgb[1] << 8) | (rgb[2] << 16)

    def set_window_colors(self, window_handle, titlebar_color, text_color):
        # This function is a placeholder. The actual implementation will depend on the specific method used to customize the window.
        pass

    def set_window_title(self, window_handle, title):
        # This function is a placeholder. The actual implementation will depend on the specific method used to customize the window.
        pass

    def set_close_button_unicode(self, window_handle, unicode):
        # This function is a placeholder. The actual implementation will depend on the specific method used to customize the window.
        pass

    def set_skin_texture(self, window_handle, texture_path):
        # This function is a placeholder. The actual implementation will depend on the specific method used to customize the window.
        pass

    def apply_changes(self):
        if self.running:
            return

        self.running = True
        Thread(target=self.run_customizer).start()

    def run_customizer(self):
        while self.running:
            # Enumerate all windows and apply the changes
            ctypes.windll.user32.EnumWindows(WNDENUMPROC(self.enum_windows_proc), 0)

    def enum_windows_proc(self, hwnd, lparam):
        # Apply the changes to each window
        self.set_window_colors(hwnd, self.titlebar_color_var.get(), self.text_color_var.get())
        self.set_window_title(hwnd, self.window_title_var.get())
        self.set_close_button_unicode(hwnd, self.close_button_unicode_var.get())
        self.set_skin_texture(hwnd, self.skin_texture_path)
        return True

    def stop_customizer(self):
        self.running = False

if __name__ == "__main__":
    customizer = WindowCustomizer()
    customizer.root.mainloop()

