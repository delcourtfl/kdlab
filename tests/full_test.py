from ctypes import WINFUNCTYPE, c_int, Structure, cast, POINTER, windll, byref, sizeof, c_longlong, c_long, c_void_p
from ctypes.wintypes import LPARAM, WPARAM, DWORD, LONG, BOOL, MSG
import win32con
import win32gui
import win32api
import sys
import time
from threading import Thread
import tkinter as tk
import traceback

# https://stackoverflow.com/questions/31379169/setting-up-a-windowshook-in-python-ctypes-windows-api

# Define a named mutex
# mutex_name = "Global\\CustomHookMutexBenchmark"
# mutex = windll.kernel32.CreateMutexW(None, False, mutex_name)
# if windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
#     print("Another instance of the hook is already running.")
#     sys.exit(1)

# Define a structure for the hook message data
class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("vkCode", DWORD), 
        ("scanCode", DWORD), 
        ("flags", DWORD),
        ("time", DWORD), 
        ("dwExtraInfo", LPARAM)
    ]

# QueryPerformanceCounter and Frequency Setup
qpc = windll.kernel32.QueryPerformanceCounter
qpf = windll.kernel32.QueryPerformanceFrequency
frequency = c_longlong()
qpf(byref(frequency))

# Hook callback function to process keyboard events
@WINFUNCTYPE(LPARAM, c_int, WPARAM, LPARAM)
def hookProc(nCode, wParam, lParam):
    if nCode == 0:  # HC_ACTION (process the event)
        keyboard_event = cast(lParam, POINTER(KBDLLHOOKSTRUCT)).contents
    
        high_res_time = c_longlong()
        qpc(byref(high_res_time))

        # Calculate timestamp in milliseconds
        timestamp_ms = (high_res_time.value * 1000) / frequency.value

        end = time.perf_counter()
        proc_end = time.process_time()
        print(f"Time: {end:.3f} s")
        print(f"Process time: {proc_end:.3f} s")

        print(f"time={keyboard_event.time} : Key {keyboard_event.vkCode} pressed.")
        print(f"High-resolution time={timestamp_ms:.3f} ms : Key {keyboard_event.vkCode} pressed.")

        if keyboard_event.vkCode == win32con.VK_RETURN:  # VK_RETURN is the Enter key
            print("Enter key pressed. Exiting...")
            win32gui.PostQuitMessage(0)
            return 0
    # Avoid propagation of events for now
    # return 1
    return windll.user32.CallNextHookEx(None, c_int(nCode), WPARAM(wParam), LPARAM(lParam))

# thread_id = get_window_thread_id("Tkinter Keyboard Hook")
thread_id = win32api.GetCurrentThreadId()
msgDict = {v: k for k, v in win32con.__dict__.items() if k.startswith("WM_")}

print("Hooking keyboard events...")

# Message loop to keep the hook active
try:
    # Set the hook
    HOOKPROC = WINFUNCTYPE(c_long, c_int, WPARAM, LPARAM)
    keyboard_proc = HOOKPROC(hookProc)
    module_handle = win32api.GetModuleHandle(None)
    module_handle = c_void_p(module_handle)
    hook_id = windll.user32.SetWindowsHookExW(
        win32con.WH_KEYBOARD_LL, keyboard_proc, module_handle, 0
    )

    if not hook_id:
        error_code = windll.kernel32.GetLastError()
        print(f"Failed to set hook. Error code: {error_code}")
        # windll.kernel32.ReleaseMutex(mutex)
        sys.exit(1)

    print("Entering message loop...")
    win32gui.PumpMessages()
    print("Exited message loop.")
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
finally:
    print("Finally")
    windll.user32.UnhookWindowsHookEx(hook_id)
    # windll.kernel32.ReleaseMutex(mutex)
