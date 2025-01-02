from ctypes import WINFUNCTYPE, c_int, Structure, cast, POINTER, windll, byref, sizeof, c_longlong, c_long, c_void_p
from ctypes.wintypes import LPARAM, WPARAM, DWORD, LONG, BOOL, MSG
import win32con
import win32gui
import win32ui
import win32api
import win32process
import sys
import time
from threading import Thread
import tkinter as tk
import traceback
import hashlib
from PIL import Image

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
        print(f"Time: {end:.6f} s")
        print(f"Process time: {proc_end:.6f} s")

        ns_end = time.perf_counter_ns()
        print(f"ns Time: {ns_end} ns")

        print(f"time={keyboard_event.time} : Key {keyboard_event.vkCode} pressed.")
        print(f"High-resolution time={timestamp_ms:.3f} ms : Key {keyboard_event.vkCode} pressed.")

        if keyboard_event.vkCode == win32con.VK_RETURN:  # VK_RETURN is the Enter key
            print("Enter key pressed. Exiting...")
            win32gui.PostQuitMessage(0)
            return 0
    # Avoid propagation of events for now
    # return 1
    return windll.user32.CallNextHookEx(None, c_int(nCode), WPARAM(wParam), LPARAM(lParam))

def capture_window(hwnd):
    # Get the window dimensions
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bot - top

    if width <= 0 or height <= 0:
        raise ValueError("Invalid window dimensions.")

    # Get the device contexts
    hdesktop = win32gui.GetDesktopWindow()
    hwindc = win32gui.GetWindowDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()

    # Create a bitmap object
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)

    # Copy the screen content into the bitmap
    result = memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    # Save bitmap data as bytes
    bmp_info = bmp.GetInfo()
    bmp_data = bmp.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmp_info['bmWidth'], bmp_info['bmHeight']),
        bmp_data, 'raw', 'BGRX', 0, 1)

    # Clean up
    win32gui.DeleteObject(bmp.GetHandle())
    memdc.DeleteDC()
    srcdc.DeleteDC()
    win32gui.ReleaseDC(hdesktop, hwindc)

    if result == None:
        #PrintWindow Succeeded
        im.save("test.png")

    return bmp_data, bmp_info

def hash_image(data):
    return hashlib.sha256(data).hexdigest()

# thread_id = get_window_thread_id("Tkinter Keyboard Hook")
thread_id = win32api.GetCurrentThreadId()
msgDict = {v: k for k, v in win32con.__dict__.items() if k.startswith("WM_")}

hwnd = win32gui.FindWindow(None, "Keypress Display")  # Replace with your window title
if not hwnd:
    raise ValueError("Window not found. Please check the window title.")
thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
print(f"Thread ID: {thread_id}, Process ID: {process_id}")

# initial_data, _ = capture_window(hwnd)
# initial_hash = hash_image(initial_data)

# # Continuously monitor the window
# while True:
#     current_data, _ = capture_window(hwnd)
#     current_hash = hash_image(current_data)

#     if current_hash != initial_hash:
#         print("Change detected!")
#         initial_hash = current_hash
#         sys.exit(0)

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
