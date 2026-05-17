import tkinter as tk
from PIL import ImageGrab, ImageTk


class RegionSelector:
    """Fullscreen overlay for selecting a screenshot region.
    Uses Toplevel so it can coexist with the settings window root."""

    def __init__(self, parent, on_select):
        self.on_select = on_select
        self.img = ImageGrab.grab(all_screens=True)

        self.top = tk.Toplevel(parent)
        self.top.attributes('-fullscreen', True)
        self.top.attributes('-topmost', True)
        self.top.configure(cursor='crosshair')

        self.tk_img = ImageTk.PhotoImage(self.img)

        self.canvas = tk.Canvas(self.top, highlightthickness=0, cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)

        w = self.top.winfo_screenwidth()
        h = self.top.winfo_screenheight()
        self.overlay = self.canvas.create_rectangle(
            0, 0, w, h, fill='', outline='', stipple='gray25')

        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        self.mask_parts = []

        self.canvas.bind('<ButtonPress-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.top.bind('<Escape>', self._on_cancel)

        self.top.focus_force()
        self.top.grab_set()

    def _clear_masks(self):
        for part in self.mask_parts:
            self.canvas.delete(part)
        self.mask_parts.clear()

    def _on_press(self, event):
        self.canvas.delete(self.overlay)
        self.overlay = None
        self.start_x, self.start_y = event.x, event.y

    def _on_drag(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self._clear_masks()

        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        w = self.top.winfo_screenwidth()
        h = self.top.winfo_screenheight()

        stipple = 'gray50'
        self.mask_parts = [
            self.canvas.create_rectangle(0, 0, w, y1, fill='black', stipple=stipple, outline=''),
            self.canvas.create_rectangle(0, y2, w, h, fill='black', stipple=stipple, outline=''),
            self.canvas.create_rectangle(0, y1, x1, y2, fill='black', stipple=stipple, outline=''),
            self.canvas.create_rectangle(x2, y1, w, y2, fill='black', stipple=stipple, outline=''),
        ]

        self.rect_id = self.canvas.create_rectangle(
            x1, y1, x2, y2, outline='#cba6f7', width=2)

    def _on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        self.top.grab_release()
        self.top.destroy()

        if x2 - x1 > 10 and y2 - y1 > 10:
            self.on_select(self.img.crop((x1, y1, x2, y2)))
        else:
            self.on_select(None)

    def _on_cancel(self, event):
        self.top.grab_release()
        self.top.destroy()
        self.on_select(None)
