from ctypes import WINFUNCTYPE, c_long, c_int, Structure, c_size_t, Union
from ctypes.wintypes import LPARAM, WPARAM, DWORD, WORD, ULONG_PTR

# Structure for the hook message data
class KEYBDINPUT(Structure):
    _fields_ = [
        ('wVk' , WORD),
        ('wScan', WORD),
        ('dwFlags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', c_size_t)
    ]

class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("vkCode", DWORD),
        ("scanCode", DWORD),
        ("flags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", LPARAM)
    ]

class INPUT(Structure):
    class _INPUT(Union):
        _fields_ = [
            ("ki", KEYBDINPUT),
        ]
    
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", DWORD),
        ("_input", _INPUT)
    ]