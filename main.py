"""Screenshot Translator — floating trigger button."""
import threading
import tkinter as tk
from config import load_config
from translate import translate
from ocr import recognize_english
from screenshot import RegionSelector


class App:
    def __init__(self):
        self.config = load_config()
        self._processing = False
        self.floating = None

        # Settings window
        from settings_window import SettingsWindow
        self.settings = SettingsWindow(on_minimize=self._on_minimize)

        # Floating trigger button — small, always-on-top
        self._create_trigger()

    def _create_trigger(self):
        btn = tk.Toplevel(self.settings.root)
        btn.title('')
        # Start at top-right area of screen
        btn.geometry('64x64+1000+100')
        btn.attributes('-topmost', True)
        btn.overrideredirect(True)
        btn.configure(bg='#cba6f7', highlightbackground='#f5c2e7', highlightthickness=2)

        # Big camera emoji + text label
        frame = tk.Frame(btn, bg='#cba6f7')
        frame.pack(expand=True, fill=tk.BOTH)
        self.trigger_label = tk.Label(frame, text='📷', font=('Segoe UI', 20),
                                      bg='#cba6f7', fg='#1e1e2e')
        self.trigger_label.pack()
        hint = tk.Label(frame, text='Screenshot', font=('Segoe UI', 7, 'bold'),
                        bg='#cba6f7', fg='#1e1e2e')
        hint.pack()

        # Drag tracking
        self._drag_start = {'x': 0, 'y': 0}
        self._drag_dist = 0

        # Drag on all elements
        for widget in (frame, self.trigger_label, hint):
            widget.bind('<ButtonPress-1>', self._on_drag_start)
            widget.bind('<B1-Motion>', self._on_drag_move)
            widget.bind('<ButtonRelease-1>', self._on_drag_end)
        self.trigger_btn = btn

    def _on_drag_start(self, event):
        self._drag_start = {'x': event.x_root, 'y': event.y_root}
        self._drag_dist = 0

    def _on_drag_move(self, event):
        dx = event.x_root - self._drag_start['x']
        dy = event.y_root - self._drag_start['y']
        self._drag_dist = abs(dx) + abs(dy)
        x = self.trigger_btn.winfo_x() + dx
        y = self.trigger_btn.winfo_y() + dy
        self.trigger_btn.geometry(f'+{x}+{y}')
        self._drag_start = {'x': event.x_root, 'y': event.y_root}

    def _on_drag_end(self, event):
        if self._drag_dist < 5:
            # Was a click, not a drag
            self._start_screenshot()

    def _on_minimize(self):
        pass

    def _start_screenshot(self):
        if self._processing:
            return
        self._processing = True
        self.config = load_config()

        was_visible = self.settings.root.state() != 'withdrawn'
        if was_visible:
            self.settings.root.withdraw()
        self.trigger_btn.withdraw()
        self.settings.root.update_idletasks()

        def on_done(image):
            if was_visible:
                self.settings.root.deiconify()
            self.trigger_btn.deiconify()
            self._on_region_selected(image)

        self.settings.root.after(150, lambda: RegionSelector(self.settings.root, on_done))

    def _on_region_selected(self, image):
        if image is None:
            self._processing = False
            return

        self.config = load_config()

        from floating_window import FloatingWindow
        # Center the floating window on screen
        sw = self.settings.root.winfo_screenwidth()
        sh = self.settings.root.winfo_screenheight()
        cx = max(0, (sw - 400) // 2)
        cy = max(0, (sh - 300) // 2)
        self.floating = FloatingWindow(parent_x=cx, parent_y=cy)
        self.floating.show_loading()
        self.floating.root.lift()
        self.floating.root.focus_force()

        threading.Thread(target=self._process_image, args=(image,), daemon=True).start()

    def _process_image(self, image):
        try:
            blocks = recognize_english(image)

            if not blocks:
                self.floating.root.after(0, lambda: self.floating.show_error(
                    'No English text found in the screenshot.'))
                self._processing = False
                return

            self.floating.root.after(0, self.floating.show_translating)

            translations = []
            for block in blocks:
                try:
                    translation = translate(block['text'], self.config)
                except Exception:
                    translation = '[Translation failed]'
                translations.append({
                    'original': block['text'],
                    'translation': translation
                })

            self.floating.root.after(0, lambda: self.floating.show_results(translations))

        except Exception as e:
            self.floating.root.after(0, lambda: self.floating.show_error(str(e)))
        finally:
            self._processing = False

    def start(self):
        self.settings.root.mainloop()


if __name__ == '__main__':
    app = App()
    app.start()
