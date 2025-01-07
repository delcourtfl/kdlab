from ctypes import POINTER, sizeof, WinError, get_last_error, windll, c_int
from ctypes.wintypes import UINT, HWND, WPARAM, LPARAM, BOOL
import time

from latency_bench.struct import INPUT, KEYBDINPUT

### These are not working properly for every cases
# import pyautogui
# from pynput.keyboard import Key, Controller
# import win32com.client as comctl
# wsh = comctl.Dispatch("WScript.Shell")

# Define constants for key codes
INPUT_KEYBOARD = 1
KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008  # Indicate that a scan code is being sent
WM_CLOSE = 0x0010

# Virtual Key Codes (some examples)
VK_A = 0x41
VK_B = 0x42
VK_ENTER = 0x0D
VK_SPACE = 0x20

# Scan Codes (some examples)
SCAN_A = 0x10
SCAN_B = 0x30
SCAN_ENTER = 0x1C
SCAN_SPACE = 0x39

def zerocheck(result, func, args):
    if result == 0:
        raise WinError(get_last_error())
    return result

class InputController:
    def __init__(self, hwnd=None):

        self.hwnd = hwnd

        self.send_input = windll.user32.SendInput
        self.send_input.argtypes = UINT, POINTER(INPUT), c_int
        self.send_input.restype = UINT
        self.send_input.errcheck = zerocheck

        self.post_message = windll.user32.PostMessageW
        self.post_message.argtypes = HWND, UINT, WPARAM, LPARAM
        self.post_message.restype = BOOL
    
    def send_virtualkey_event(self, vk_code, event_type=KEYEVENTF_KEYDOWN):
        # Create an INPUT structure
        input_structure = INPUT()
        input_structure.type = INPUT_KEYBOARD
        input_structure.ki = KEYBDINPUT(
            wVk=vk_code,         # Virtual Key Code
            wScan=0,             # No hardware scan code
            dwFlags=event_type,  # Key press flag
            time=0,              # No specific time stamp
            dwExtraInfo=None     # No extra info
        )
        
        # Send the input event (simulate key press or release)
        self.send_input(1, POINTER(INPUT)(input_structure), sizeof(INPUT))

    def send_scancode_event(self, scan_code, event_type=KEYEVENTF_KEYDOWN):
        # Create an INPUT structure for the scan code
        input_structure = INPUT()
        input_structure.type = INPUT_KEYBOARD
        input_structure.ki = KEYBDINPUT(
            wVk=0,                  # Virtual Key Code (set to 0 when using scan codes)
            wScan=scan_code,        # Hardware scan code
            dwFlags=event_type | KEYEVENTF_SCANCODE,  # Use scan code flag
            time=0,
            dwExtraInfo=None,
        )
        
        # Send the input event
        self.send_input(1, POINTER(INPUT)(input_structure), sizeof(INPUT))

    def post_key_msg(self, vk_code, event_type=KEYEVENTF_KEYDOWN):
        # Not working ?
        if not self.hwnd:
            raise ValueError("No window handle provided.")
        
        result = self.post_message(self.hwnd, event_type, vk_code, 0)
        if not result:
            raise WinError(get_last_error())

    def send_close_signal(self):
        # Send a WM_CLOSE signal to the window to request graceful termination.
        if not self.hwnd:
            raise ValueError("No window handle provided.")
        
        result = self.post_message(self.hwnd, WM_CLOSE, 0, 0)
        if not result:
            raise WinError(get_last_error())
    
    def press_key(self, vk_code):
        self.send_virtualkey_event(vk_code, KEYEVENTF_KEYDOWN)
    
    def release_key(self, vk_code):
        self.send_virtualkey_event(vk_code, KEYEVENTF_KEYUP)

    def press_key(self, scan_code):
        self.send_scancode_event(scan_code, KEYEVENTF_KEYDOWN)
    
    def release_key(self, scan_code):
        self.send_scancode_event(scan_code, KEYEVENTF_KEYUP)

    def toggle_key_virtualkey(self, scan_code):
        self.press_key(scan_code)
        # time.sleep(0.5)
        self.release_key(scan_code)

    def toggle_key_scancode(self, scan_code):
        self.press_key(scan_code)
        # time.sleep(0.5)
        self.release_key(scan_code)