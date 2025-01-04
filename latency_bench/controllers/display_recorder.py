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
import hashlib
from PIL import Image

class DisplayRecorder:

    def __init__(self, window_title):
        self.window_title = window_title
        self.hwnd = None
        self.thread_id = None
        self.process_id = None

        self.initial_hash = None

        # Initialize window
        self.setup_window()

    def setup_window(self):
        # Find the window by title
        self.hwnd = win32gui.FindWindow(None, self.window_title)
        if not self.hwnd:
            raise ValueError(f"Window with title '{self.window_title}' not found.")

        # Get window details
        self.thread_id, self.process_id = win32process.GetWindowThreadProcessId(self.hwnd)
        print(f"Thread ID: {self.thread_id}, Process ID: {self.process_id}")

    def capture_window(self):
        
        windll.user32.SetProcessDPIAware()

        # Get the window dimensions
        left, top, right, bot = win32gui.GetClientRect(self.hwnd)
        width = right - left
        height = bot - top

        if width <= 0 or height <= 0:
            raise ValueError("Invalid window dimensions.")
        print(f"Window dimensions: {width}x{height}")

        # Get the device contexts
        hdesktop = win32gui.GetDesktopWindow()
        hwindc = win32gui.GetWindowDC(self.hwnd)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()

        # Create a bitmap object
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)

        # Copy the screen content into the bitmap
        result = memdc.BitBlt((0, 0), (width, height), srcdc, (0, 0), win32con.SRCCOPY)

        # Save bitmap data as bytes
        bmp_info = bmp.GetInfo()
        bmp_data = bmp.GetBitmapBits(True)

        im = Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_data, 'raw', 'BGRX', 0, 1
        )

        # Clean up
        win32gui.DeleteObject(bmp.GetHandle())
        memdc.DeleteDC()
        srcdc.DeleteDC()
        win32gui.ReleaseDC(hdesktop, hwindc)

        if result is None:
            # PrintWindow Succeeded
            im.save("test.png")

        return bmp_data, bmp_info

    def hash_image(self, data):
        return hashlib.sha256(data).hexdigest()
    
    def set_initial_hash(self):
        initial_data, _ = self.capture_window()
        self.initial_hash = self.hash_image(initial_data)
        return self.initial_hash
    
    def set_objective_hash(self):
        objective_data, _ = self.capture_window()
        self.objective_hash = self.hash_image(objective_data)
        return self.objective_hash

    def start_monitoring(self):
        while True:
            current_data, _ = self.capture_window()
            current_hash = self.hash_image(current_data)

            if current_hash != self.initial_hash:
                return time.perf_counter_ns()
    
    def start_monitoring_no_timer(self):
        while True:
            current_data, _ = self.capture_window()
            current_hash = self.hash_image(current_data)
            if current_hash != self.initial_hash:
                return True
        return False