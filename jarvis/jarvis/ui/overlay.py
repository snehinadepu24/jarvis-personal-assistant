from __future__ import annotations

import sys

if sys.platform != "win32":
    raise ImportError("overlay.py is Windows-only (Tk overlay, click-through)")

import tkinter as tk

import win32gui
import win32con

WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WDA_EXCLUDEFROMCAPTURE = 0x11

MARK_BG = "#FFB224"
MARK_FG = "#0B0F14"


class Overlay:
    def __init__(self, marks: list[tuple[int, int, int, int, int]]):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")
        self.windows: list[tk.Toplevel] = []
        self.marks = marks

    def draw(self) -> None:
        for l, t, r, b, mark in self.marks:
            win = tk.Toplevel(self.root, bg="#010101")
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            lbl = tk.Label(win, text=str(mark), bg=MARK_BG, fg=MARK_FG, font=("Segoe UI", 10, "bold"))
            lbl.pack()
            win.geometry(f"+{l}+{t}")
            hwnd = win32gui.GetParent(win.winfo_id())
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
            win32gui.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            self.windows.append(win)

    def run(self) -> None:
        self.root.after(3000, self.root.destroy)
        self.root.mainloop()
