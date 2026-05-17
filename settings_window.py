import tkinter as tk
from tkinter import ttk
from config import load_config, save_config
from translate import translate_deepl, translate_baidu


class SettingsWindow:
    def __init__(self, on_minimize=None):
        self.on_minimize = on_minimize
        self.config = load_config()

        self.root = tk.Tk()
        self.root.title('Screenshot Translator')
        self.root.geometry('380x420')
        self.root.resizable(False, False)
        self.root.configure(bg='#1e1e2e')
        self.root.attributes('-topmost', True)

        self._build_ui()
        self._load_config_to_ui()

        self.root.protocol('WM_DELETE_WINDOW', self._on_close)

    def _build_ui(self):
        main = tk.Frame(self.root, bg='#1e1e2e')
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Title
        tk.Label(main, text='Screenshot Translator', font=('Segoe UI', 14, 'bold'),
                 fg='#f5c2e7', bg='#1e1e2e').pack(pady=(0, 14))

        # Service selector
        tk.Label(main, text='Translation Service', fg='#a6adc8', bg='#1e1e2e',
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        self.service_var = tk.StringVar(value='baidu')
        radio_frame = tk.Frame(main, bg='#1e1e2e')
        radio_frame.pack(fill=tk.X, pady=(4, 12))

        # Use tk Radiobutton (not ttk) for proper bg color
        self.deepl_rb = tk.Radiobutton(radio_frame, text='DeepL', variable=self.service_var,
                                        value='deepl', command=self._toggle_service,
                                        bg='#1e1e2e', fg='#cdd6f4', selectcolor='#313244',
                                        activebackground='#1e1e2e', activeforeground='#cba6f7')
        self.deepl_rb.pack(side=tk.LEFT)
        self.baidu_rb = tk.Radiobutton(radio_frame, text='Baidu Translate', variable=self.service_var,
                                        value='baidu', command=self._toggle_service,
                                        bg='#1e1e2e', fg='#cdd6f4', selectcolor='#313244',
                                        activebackground='#1e1e2e', activeforeground='#cba6f7')
        self.baidu_rb.pack(side=tk.LEFT, padx=(14, 0))

        # Ref position for inserting service-specific frames
        self._insert_anchor = radio_frame

        # DeepL section
        self.deepl_frame = tk.Frame(main, bg='#1e1e2e')
        tk.Label(self.deepl_frame, text='DeepL API Key', fg='#bac2de', bg='#1e1e2e',
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        key_row = tk.Frame(self.deepl_frame, bg='#1e1e2e')
        key_row.pack(fill=tk.X, pady=(2, 4))
        self.deepLKey_var = tk.StringVar()
        self.deepl_entry = tk.Entry(key_row, textvariable=self.deepLKey_var, show='*',
                                    bg='#313244', fg='#cdd6f4', insertbackground='#cdd6f4',
                                    relief='flat', font=('Segoe UI', 10))
        self.deepl_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        tk.Button(key_row, text='👁', bg='#313244', fg='#cdd6f4', relief='flat',
                  font=('Segoe UI', 8), command=self._toggle_deepl_visible).pack(side=tk.RIGHT, padx=(4, 0))
        tk.Button(self.deepl_frame, text='Test Connection', bg='#45475a', fg='#cdd6f4',
                  relief='flat', font=('Segoe UI', 9), command=self._test_deepl).pack(fill=tk.X, pady=(0, 2))
        self.deepl_status = tk.Label(self.deepl_frame, text='', fg='#a6adc8', bg='#1e1e2e',
                                      font=('Segoe UI', 9), anchor=tk.W)
        self.deepl_status.pack(fill=tk.X)

        # Baidu section
        self.baidu_frame = tk.Frame(main, bg='#1e1e2e')
        tk.Label(self.baidu_frame, text='Baidu App ID', fg='#bac2de', bg='#1e1e2e',
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        self.baiduAppId_var = tk.StringVar()
        tk.Entry(self.baidu_frame, textvariable=self.baiduAppId_var,
                 bg='#313244', fg='#cdd6f4', insertbackground='#cdd6f4',
                 relief='flat', font=('Segoe UI', 10)).pack(fill=tk.X, ipady=3, pady=(2, 6))

        tk.Label(self.baidu_frame, text='Baidu Secret Key', fg='#bac2de', bg='#1e1e2e',
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        self.baiduSecretKey_var = tk.StringVar()
        tk.Entry(self.baidu_frame, textvariable=self.baiduSecretKey_var, show='*',
                 bg='#313244', fg='#cdd6f4', insertbackground='#cdd6f4',
                 relief='flat', font=('Segoe UI', 10)).pack(fill=tk.X, ipady=3, pady=(2, 4))

        tk.Button(self.baidu_frame, text='Test Connection', bg='#45475a', fg='#cdd6f4',
                  relief='flat', font=('Segoe UI', 9), command=self._test_baidu).pack(fill=tk.X, pady=(0, 2))
        self.baidu_status = tk.Label(self.baidu_frame, text='', fg='#a6adc8', bg='#1e1e2e',
                                      font=('Segoe UI', 9), anchor=tk.W)
        self.baidu_status.pack(fill=tk.X)

        # Hint
        hint_frame = tk.Frame(main, bg='#313244', highlightbackground='#cba6f7', highlightthickness=1)
        hint_frame.pack(fill=tk.X, pady=(14, 10))
        tk.Label(hint_frame, text='Click 📷 button to screenshot & translate',
                 bg='#313244', fg='#f5c2e7', font=('Segoe UI', 11)).pack(pady=12)

        # Save button
        self.save_btn = tk.Button(main, text='Save Settings', bg='#cba6f7', fg='#1e1e2e',
                                  relief='flat', font=('Segoe UI', 11, 'bold'),
                                  command=self._save)
        self.save_btn.pack(fill=tk.X, pady=(0, 6))

        # Minimize button
        tk.Button(main, text='Hide Window', bg='#45475a', fg='#cdd6f4',
                  relief='flat', font=('Segoe UI', 10), command=self._minimize).pack(fill=tk.X)

    def _toggle_service(self):
        self.deepl_frame.pack_forget()
        self.baidu_frame.pack_forget()
        if self.service_var.get() == 'baidu':
            self.baidu_frame.pack(fill=tk.X, after=self._insert_anchor, pady=(0, 4))
        else:
            self.deepl_frame.pack(fill=tk.X, after=self._insert_anchor, pady=(0, 4))

    def _toggle_deepl_visible(self):
        if self.deepl_entry.cget('show') == '*':
            self.deepl_entry.configure(show='')
        else:
            self.deepl_entry.configure(show='*')

    def _test_deepl(self):
        key = self.deepLKey_var.get().strip()
        if not key:
            self.deepl_status.configure(text='Please enter an API key', fg='#f38ba8')
            return
        self.deepl_status.configure(text='Testing...', fg='#a6adc8')
        self.root.update()
        try:
            translate_deepl('Hello', key)
            self.deepl_status.configure(text='Connection successful', fg='#a6e3a1')
        except Exception as e:
            self.deepl_status.configure(text=str(e)[:80], fg='#f38ba8')

    def _test_baidu(self):
        app_id = self.baiduAppId_var.get().strip()
        secret = self.baiduSecretKey_var.get().strip()
        if not app_id or not secret:
            self.baidu_status.configure(text='Please enter App ID and Secret Key', fg='#f38ba8')
            return
        self.baidu_status.configure(text='Testing...', fg='#a6adc8')
        self.root.update()
        try:
            translate_baidu('Hello', app_id, secret)
            self.baidu_status.configure(text='Connection successful', fg='#a6e3a1')
        except Exception as e:
            self.baidu_status.configure(text=str(e)[:80], fg='#f38ba8')

    def _save(self):
        self.config['service'] = self.service_var.get()
        self.config['deepLKey'] = self.deepLKey_var.get()
        self.config['baiduAppId'] = self.baiduAppId_var.get()
        self.config['baiduSecretKey'] = self.baiduSecretKey_var.get()
        save_config(self.config)
        self.save_btn.configure(text='Saved!')
        self.root.after(1500, lambda: self.save_btn.configure(text='Save Settings'))

    def _load_config_to_ui(self):
        svc = self.config.get('service', 'baidu')
        self.service_var.set(svc)
        self.deepLKey_var.set(self.config.get('deepLKey', ''))
        self.baiduAppId_var.set(self.config.get('baiduAppId', ''))
        self.baiduSecretKey_var.set(self.config.get('baiduSecretKey', ''))
        self._toggle_service()

    def _minimize(self):
        self.root.withdraw()
        if self.on_minimize:
            self.on_minimize()

    def _on_close(self):
        self.root.withdraw()
        if self.on_minimize:
            self.on_minimize()

    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def destroy(self):
        self.root.destroy()
