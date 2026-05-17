import tkinter as tk


class FloatingWindow:
    """Always-on-top floating window showing translation results."""

    def __init__(self, parent_x=100, parent_y=100):
        self.root = tk.Toplevel()
        self.root.title('Translation')
        self.root.geometry(f'380x300+{parent_x}+{parent_y}')
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#1e1e2e')
        self.root.minsize(300, 200)

        self.all_translations = []

        self._build_ui()
        self._make_draggable()

    def _build_ui(self):
        # Header (draggable)
        header = tk.Frame(self.root, bg='#313244', height=32)
        header.pack(fill=tk.X)

        title = tk.Label(header, text='Translation', bg='#313244', fg='#f5c2e7',
                         font=('Segoe UI', 10, 'bold'))
        title.pack(side=tk.LEFT, padx=10, pady=4)

        close_btn = tk.Button(header, text='✕', bg='#313244', fg='#cdd6f4',
                              relief='flat', font=('Segoe UI', 10),
                              command=self.close, bd=0)
        close_btn.pack(side=tk.RIGHT, padx=4, pady=2)
        copy_btn = tk.Button(header, text='📋', bg='#313244', fg='#cdd6f4',
                             relief='flat', font=('Segoe UI', 10),
                             command=self.copy, bd=0)
        copy_btn.pack(side=tk.RIGHT, padx=2, pady=2)

        # Content area
        self.content = tk.Frame(self.root, bg='#1e1e2e')
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.content, bg='#1e1e2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg='#1e1e2e')
        self.scroll_frame.bind('<Configure>',
                               lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Loading label
        self.loading_label = tk.Label(self.scroll_frame, text='Recognizing text...',
                                      bg='#1e1e2e', fg='#a6adc8',
                                      font=('Segoe UI', 11))
        self.loading_label.pack(pady=20)

    def _make_draggable(self):
        self._drag_data = {'x': 0, 'y': 0}

        def start_drag(event):
            self._drag_data['x'] = event.x
            self._drag_data['y'] = event.y

        def do_drag(event):
            x = self.root.winfo_x() + (event.x - self._drag_data['x'])
            y = self.root.winfo_y() + (event.y - self._drag_data['y'])
            self.root.geometry(f'+{x}+{y}')

        # Make header draggable
        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame):
                child.bind('<Button-1>', start_drag)
                child.bind('<B1-Motion>', do_drag)
                for sub in child.winfo_children():
                    sub.bind('<Button-1>', start_drag)
                    sub.bind('<B1-Motion>', do_drag)

    def show_loading(self):
        self.loading_label.configure(text='Recognizing text...')
        self.loading_label.pack(pady=20)
        for w in self.scroll_frame.winfo_children():
            if w != self.loading_label:
                w.destroy()
        self.all_translations = []

    def show_translating(self):
        self.loading_label.configure(text='Translating...')

    def show_results(self, translations):
        self.loading_label.pack_forget()
        self.all_translations = translations

        for item in translations:
            block = tk.Frame(self.scroll_frame, bg='#1e1e2e')
            block.pack(fill=tk.X, pady=(0, 10))

            orig = tk.Label(block, text=item['original'], bg='#1e1e2e', fg='#6c7086',
                            font=('Segoe UI', 9), wraplength=340, justify=tk.LEFT, anchor=tk.W)
            orig.pack(fill=tk.X)

            trans = tk.Label(block, text=item['translation'], bg='#1e1e2e', fg='#cdd6f4',
                             font=('Segoe UI', 13, 'bold'), wraplength=340,
                             justify=tk.LEFT, anchor=tk.W)
            trans.pack(fill=tk.X)

            sep = tk.Frame(block, bg='#313244', height=1)
            sep.pack(fill=tk.X, pady=(6, 0))

    def show_error(self, message):
        self.loading_label.pack_forget()
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        tk.Label(self.scroll_frame, text=message, bg='#1e1e2e', fg='#f38ba8',
                 font=('Segoe UI', 11), wraplength=340).pack(pady=20)

    def copy(self):
        if self.all_translations:
            text = '\n'.join(t['translation'] for t in self.all_translations)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)

    def close(self):
        self.root.destroy()

    def lift(self):
        self.root.lift()
        self.root.focus_force()
