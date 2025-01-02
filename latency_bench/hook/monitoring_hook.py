from ctypes import WINFUNCTYPE, c_long, c_int, Structure, cast, POINTER, windll, byref, c_longlong, c_void_p
from ctypes.wintypes import LPARAM, WPARAM, DWORD
import win32con
import win32gui
import win32api
import traceback
import time

from latency_bench.struct import KBDLLHOOKSTRUCT

class MonitoringHook:

    def __init__(self):
        # QueryPerformanceCounter and Frequency Setup
        self.qpc = windll.kernel32.QueryPerformanceCounter
        self.qpf = windll.kernel32.QueryPerformanceFrequency
        self.frequency = c_longlong()
        self.qpf(byref(self.frequency))
        
        self.hook_id = None
        self.hook_id = None
        self.keyboard_proc = None

    def get_hook_proc(self):
        # Hook callback function to process keyboard events
        @WINFUNCTYPE(LPARAM, c_int, WPARAM, LPARAM)
        def hook_proc(nCode, wParam, lParam):
            if nCode == 0:  # HC_ACTION (process the event)
                keyboard_event = cast(lParam, POINTER(KBDLLHOOKSTRUCT)).contents

                high_res_time = c_longlong()
                self.qpc(byref(high_res_time))

                # Calculate timestamp in milliseconds
                timestamp_ms = (high_res_time.value * 1000) / self.frequency.value

                ns_end = time.perf_counter_ns()
                print(f"Time: {ns_end} ns")
                print(f"time={keyboard_event.time} : Key {keyboard_event.vkCode} pressed.")
                print(f"High-resolution time={timestamp_ms:.6f} ms : Key {keyboard_event.vkCode} pressed.")

                if keyboard_event.vkCode == win32con.VK_RETURN:  # VK_RETURN is the Enter key
                    print("Enter key pressed. Exiting...")
                    win32gui.PostQuitMessage(0)
                    return 0

            # Avoid propagation of events for now
            # return 1
            return windll.user32.CallNextHookEx(None, c_int(nCode), WPARAM(wParam), LPARAM(lParam))

        return hook_proc

    def set_hook(self):

        self.hook_proc = self.get_hook_proc()
        HOOKPROC = WINFUNCTYPE(c_long, c_int, WPARAM, LPARAM)
        self.keyboard_proc = HOOKPROC(self.hook_proc)
        module_handle = c_void_p(win32api.GetModuleHandle(None))
        self.hook_id = windll.user32.SetWindowsHookExW(
            win32con.WH_KEYBOARD_LL, self.keyboard_proc, module_handle, 0
        )

        if not self.hook_id:
            error_code = windll.kernel32.GetLastError()
            raise RuntimeError(f"Failed to set hook. Error code: {error_code}")

    def remove_hook(self):
        if self.hook_id:
            windll.user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None

    def run(self):
        try:
            print("Hooking keyboard events...")
            self.set_hook()
            print("Entering message loop...")
            win32gui.PumpMessages()
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
        finally:
            self.remove_hook()
            print("Hook removed and exiting.")
