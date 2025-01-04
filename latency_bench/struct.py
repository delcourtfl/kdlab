from ctypes import WINFUNCTYPE, c_long, c_int, Structure, c_size_t, Union, POINTER
from ctypes.wintypes import LPARAM, WPARAM, DWORD, WORD, ULONG, LONG

# Structure for the hook message data
class KEYBDINPUT(Structure):
    _fields_ = [
        ('wVk' , WORD),
        ('wScan', WORD),
        ('dwFlags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', POINTER(ULONG))
    ]

class MOUSEINPUT(Structure):
    _fields_ = [
        ('dx' , LONG),
        ('dy', LONG),
        ('mouseData', DWORD),
        ('dwFlags', DWORD),
        ('time', DWORD),
        ('dwExtraInfo', c_size_t)
    ]

class HARDWAREINPUT(Structure):
    _fields_ = [
        ('uMsg', DWORD),
        ('wParamL', WORD),
        ('wParamH', DWORD)
    ]

class DUMMYUNIONNAME(Union):
    _fields_ = [
        ('mi', MOUSEINPUT),
        ('ki', KEYBDINPUT),
        ('hi', HARDWAREINPUT)
    ]

class INPUT(Structure):
    _anonymous_ = ['u']
    _fields_ = [
        ('type', DWORD),
        ('u', DUMMYUNIONNAME)
    ]

class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("vkCode", DWORD),
        ("scanCode", DWORD),
        ("flags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", LPARAM)
    ]



