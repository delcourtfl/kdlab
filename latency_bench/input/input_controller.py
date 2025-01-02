import ctypes
from ctypes import wintypes, windll
import time

from latency_bench.struct import INPUT, KEYBDINPUT

# Define constants for key codes
KEY_PRESSED = 0
KEY_RELEASED = 2

# Virtual Key Codes (some examples)
VK_A = 0x41
VK_B = 0x42
VK_ENTER = 0x0D

class InputController:
    def __init__(self):
        self.send_input = windll.user32.SendInput
        pass
    
    def send_key_event(self, vk_code, event_type=KEY_PRESSED):
        # Create a KEYBDINPUT structure
        kb_input = KEYBDINPUT(
            wVk=vk_code,
            wScan=0,
            dwFlags=event_type,
            time=0,
            dwExtraInfo=0
        )
        
        # Create the INPUT structure
        input_event = INPUT(type=1, ki=kb_input)
        
        # Send the input event (simulate key press or release)
        self.send_input(1, ctypes.byref(input_event), ctypes.sizeof(INPUT))
    
    def press_key(self, vk_code):
        self.send_key_event(vk_code, KEY_PRESSED)
    
    def release_key(self, vk_code):
        self.send_key_event(vk_code, KEY_RELEASED)

    def type_text(self, text):
        for char in text:
            vk_code = ord(char.upper()) if 'a' <= char.lower() <= 'z' else None
            if vk_code:
                self.press_key(vk_code)
                time.sleep(0.05)
                self.release_key(vk_code)
            else:
                print(f"Unsupported character: {char}")
            time.sleep(0.1)  # simulate typing delay

    def press_enter(self):
        self.press_key(VK_A)
        time.sleep(0.05)
        self.release_key(VK_A)