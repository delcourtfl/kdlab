import win32con
import win32gui
import win32ui
import win32api
import win32process
import time
import hashlib
from PIL import Image

class DisplayRecorder:

    def __init__(self, window_title):
        self.window_title = window_title
        self.hwnd = None
        self.thread_id = None
        self.process_id = None

        self.initial_hash = None
        self.initial_data = None

        self.objective_hash = None
        self.objective_data = None

        # Initialize window
        self.setup_window()

    def setup_window(self):
        # Find the window by title
        self.hwnd = win32gui.FindWindow(None, self.window_title)
        if not self.hwnd:
            raise ValueError(f"Window with title '{self.window_title}' not found.")

        # Get window details
        self.thread_id, self.process_id = win32process.GetWindowThreadProcessId(self.hwnd)
        # print(f"Thread ID: {self.thread_id}, Process ID: {self.process_id}")

        # Get the window dimensions
        self.left, self.top, self.right, self.bot = win32gui.GetClientRect(self.hwnd)

        self.width = self.right - self.left
        self.height = self.bot - self.top

        if self.width <= 0 or self.height <= 0:
            raise ValueError("Invalid window dimensions.")
        # print(f"Window dimensions: {self.width}x{self.height}")
        # print(f"Window position: ({self.left}, {self.top})")

    def capture_window(self, save_file=None):

        # Get the device contexts
        self.hwindc = win32gui.GetWindowDC(self.hwnd)
        self.srcdc = win32ui.CreateDCFromHandle(self.hwindc)
        self.memdc = self.srcdc.CreateCompatibleDC()

        # Create a bitmap object
        self.bmp = win32ui.CreateBitmap()
        self.bmp.CreateCompatibleBitmap(self.srcdc, self.width, self.height)
        self.memdc.SelectObject(self.bmp)

        # Copy the screen content into the bitmap (with offset for obscure win11 reasons ¯\_(ツ)_/¯)
        result = self.memdc.BitBlt((0, 0), (self.width, self.height), self.srcdc, (8, 31), win32con.SRCCOPY)

        # Save bitmap data as bytes
        bmp_info = self.bmp.GetInfo()
        bmp_data = self.bmp.GetBitmapBits(True)

        if save_file and result is None:
            img = Image.frombuffer(
                'RGB',
                (bmp_info['bmWidth'], bmp_info['bmHeight']),
                bmp_data, 'raw', 'BGRX', 
                0,
                1,
            )
            # PrintWindow Succeeded
            img.save(save_file)

        # Clean up
        self.memdc.DeleteDC()
        self.srcdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwindc)
        win32gui.DeleteObject(self.bmp.GetHandle())

        return bmp_data, bmp_info

    def compare_images(self, image1, image2):
        return image1 == image2

    def hash_image(self, data):
        return hashlib.sha256(data).hexdigest()
    
    def set_initial(self):
        self.initial_data, _ = self.capture_window()
        self.initial_hash = self.hash_image(self.initial_data)
        return self.initial_hash, self.initial_data
    
    def set_objective(self):
        self.objective_data, _ = self.capture_window()
        self.objective_hash = self.hash_image(self.objective_data)
        return self.objective_hash, self.objective_data

    def start_monitoring(self):
        while True:
            current_data, _ = self.capture_window()

            if self.compare_images(current_data, self.objective_data):
                return time.perf_counter_ns()
            
    def start_monitoring_initial(self):
        while True:
            current_data, _ = self.capture_window()

            if self.compare_images(current_data, self.initial_data):
                return time.perf_counter_ns()