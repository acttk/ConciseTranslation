"""Windows global hotkey via RegisterHotKey + WM_HOTKEY."""
import ctypes
import ctypes.wintypes

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY = 0x0312
VK_F1 = 0x70
HOTKEY_ID = 1

user32 = ctypes.windll.user32


def register_hotkey(hwnd):
    """Register F1 as a global hotkey. hwnd is the tkinter window handle."""
    ok = user32.RegisterHotKey(hwnd, HOTKEY_ID, MOD_NOREPEAT, VK_F1)
    if not ok:
        raise OSError("RegisterHotKey failed. F1 may already be registered by another app.")
    return True


def unregister_hotkey(hwnd):
    user32.UnregisterHotKey(hwnd, HOTKEY_ID)


def is_hotkey(msg):
    """Check if a WM message is our hotkey."""
    return msg == WM_HOTKEY
