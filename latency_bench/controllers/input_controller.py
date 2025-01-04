from ctypes import POINTER, sizeof, WinError, get_last_error, windll, c_int
from ctypes.wintypes import UINT
import time

from latency_bench.struct import INPUT, KEYBDINPUT

# Define constants for key codes
INPUT_KEYBOARD = 1
KEYEVENTF_KEYDOWN = 0
KEYEVENTF_KEYUP = 2

# Virtual Key Codes (some examples)
VK_A = 0x41
VK_B = 0x42
VK_ENTER = 0x0D
VK_SPACE = 0x20

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
    
    def send_key_event(self, vk_code, event_type=KEYEVENTF_KEYDOWN):
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

    def post_key_msg(self, vk_code, event_type=KEYEVENTF_KEYDOWN):
        # Not working ?
        if not self.hwnd:
            raise ValueError("No window handle provided.")
        self.post_message(self.hwnd, event_type, vk_code, 0)
    
    def press_key(self, vk_code):
        self.send_key_event(vk_code, KEYEVENTF_KEYDOWN)
    
    def release_key(self, vk_code):
        self.send_key_event(vk_code, KEYEVENTF_KEYUP)

    def toggle_key(self, vk_code):
        self.press_key(vk_code)
        # time.sleep(0.5)
        self.release_key(vk_code)