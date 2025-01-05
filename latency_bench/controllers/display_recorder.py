from ctypes import WINFUNCTYPE, c_int, Structure, cast, POINTER, windll, byref, sizeof, c_longlong, c_long, c_void_p, create_string_buffer, c_buffer
from ctypes.wintypes import LPARAM, WPARAM, DWORD, LONG, BOOL, MSG, RECT
from struct import pack, calcsize
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

        # Get the window dimensions
        self.left, self.top, self.right, self.bot = win32gui.GetClientRect(self.hwnd)

        self.width = self.right - self.left
        self.height = self.bot - self.top

        if self.width <= 0 or self.height <= 0:
            raise ValueError("Invalid window dimensions.")
        print(f"Window dimensions: {self.width}x{self.height}")
        print(f"Window position: ({self.left}, {self.top})")

        # # Get the device contexts
        # self.hwindc = win32gui.GetWindowDC(self.hwnd)
        # self.srcdc = win32ui.CreateDCFromHandle(self.hwindc)
        # self.memdc = self.srcdc.CreateCompatibleDC()

        # # Create a bitmap object
        # self.bmp = win32ui.CreateBitmap()
        # self.bmp.CreateCompatibleBitmap(self.srcdc, self.width, self.height)
        # self.memdc.SelectObject(self.bmp)

    def capture_window(self):

        rect = RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        result = windll.dwmapi.DwmGetWindowAttribute(self.hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, byref(rect), sizeof(rect))
        print(result)
        print(rect.left, rect.top, rect.right, rect.bottom)

        # Get the device contexts
        self.hwindc = win32gui.GetWindowDC(self.hwnd)
        self.srcdc = win32ui.CreateDCFromHandle(self.hwindc)
        self.memdc = self.srcdc.CreateCompatibleDC()

        # Create a bitmap object
        self.bmp = win32ui.CreateBitmap()
        self.bmp.CreateCompatibleBitmap(self.srcdc, self.width, self.height)
        self.memdc.SelectObject(self.bmp)

        # Copy the screen content into the bitmap (with offset for obscure win11 reasons ¯\_(ツ)_/¯)
        result = self.memdc.BitBlt((0, 0), (self.width, self.height), self.srcdc, (8, 32), win32con.SRCCOPY)

        # Save bitmap data as bytes
        bmp_info = self.bmp.GetInfo()
        bmp_data = self.bmp.GetBitmapBits(True)

        im = Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_data, 'raw', 'BGRX', 
            0,
            1,
        )

        # Clean up
        self.memdc.DeleteDC()
        self.srcdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwindc)
        win32gui.DeleteObject(self.bmp.GetHandle())

        if result is None:
            # PrintWindow Succeeded
            im.save("maybe_test.png")

        return bmp_data, bmp_info
    
    def old_capture_window(self):
        ###########################
        L,T,R,B = win32gui.GetClientRect(self.hwnd)
        w,h = R-L,B-T

        dc = windll.user32.GetWindowDC(self.hwnd)
        dc1 = windll.gdi32.CreateCompatibleDC(dc)
        bmp1 = windll.gdi32.CreateCompatibleBitmap(dc, w, h)

        PW_CLIENTONLY, PW_RENDERFULLCONTENT = 1, 2

        obj1 = windll.gdi32.SelectObject(dc1,bmp1) # select bmp into dc
        windll.user32.PrintWindow(self.hwnd, dc1, PW_CLIENTONLY|PW_RENDERFULLCONTENT) # render window to dc1
        windll.gdi32.SelectObject(dc1, obj1) # restore dc's default obj

        data = create_string_buffer((w*4)*h)
        bmi = c_buffer(pack("IiiHHIIiiII",calcsize("IiiHHIIiiII"),w,-h,1,32,0,0,0,0,0,0))
        windll.gdi32.GetDIBits(dc1,bmp1,0,h,byref(data),byref(bmi),win32con.DIB_RGB_COLORS)
        img = Image.frombuffer('RGB',(w,h),data,'raw','BGRX')
        img.save("new_test.png")

        windll.gdi32.DeleteDC(dc1) # delete created dc
        windll.user32.ReleaseDC(self.hwnd,dc) # release retrieved dc
        return
        ###########################

    def compare_images(self, image1, image2):
        return image1 == image2

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