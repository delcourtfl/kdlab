import ctypes
from ctypes import wintypes
import time

# Define Windows API constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

# Define ctypes function prototypes
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Structure for keyboard events
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),  # Virtual key code
        ("scanCode", wintypes.DWORD),  # Hardware scan code
        ("flags", wintypes.DWORD),  # Event flags
        ("time", wintypes.DWORD),  # Timestamp
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),  # Extra information
    ]

# Callback function for the hook
def low_level_keyboard_proc(nCode, wParam, lParam):
    if nCode == 0:  # HC_ACTION
        kb_data = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk_code = kb_data.vkCode
        timestamp = time.perf_counter()
        if wParam == WM_KEYDOWN:
            print(f"Key {vk_code} pressed at {timestamp}")
        elif wParam == WM_KEYUP:
            print(f"Key {vk_code} released at {timestamp}")
    # Pass control to the next hook in the chain
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

# Create a hook procedure pointer
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)(low_level_keyboard_proc)

def main():
    # Set the hook
    hook_id = user32.SetWindowsHookExA(
        WH_KEYBOARD_LL, LowLevelKeyboardProc, kernel32.GetModuleHandleW(None), 0
    )

    if not hook_id:
        error_code = kernel32.GetLastError()
        print(f"Failed to set hook. Error code: {error_code}")
        return

    try:
        msg = wintypes.MSG()
        while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))
    finally:
        # Unhook the procedure
        user32.UnhookWindowsHookEx(hook_id)

if __name__ == "__main__":
    main()
