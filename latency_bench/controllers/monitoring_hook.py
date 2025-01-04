from ctypes import WinError, get_last_error, WINFUNCTYPE, c_long, c_int, Structure, cast, POINTER, windll, byref, c_longlong, c_void_p
from ctypes.wintypes import LPARAM, WPARAM, DWORD, HANDLE, HWND, MSG, ULONG, LONG
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

    #################################################################################
    ### Event hook for monitoring window redraw events, but doesn't work properly ###

    @WINFUNCTYPE(None, HANDLE, DWORD, HWND, LONG, LONG, DWORD, DWORD)
    def event_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        print(f"Event: {hex(event)}, hwnd: {hwnd}, idObject: {idObject}, idChild: {idChild}, dwEventThread: {dwEventThread}, dwmsEventTime: {dwmsEventTime}")

    def set_process_hook(self, process):
        process_id = process.pid

        EVENT_OBJECT_LOCATIONCHANGE = 0x800B
        WINEVENT_OUTOFCONTEXT = 0x0000
        WINEVENT_SKIPOWNTHREAD = 0x0001
        WINEVENT_SKIPOWNPROCESS = 0x0002
        WINEVENT_INCONTEXT = 0x0004

        # Set up the event hook
        self.event_hook = windll.user32.SetWinEventHook(
            0x8000,  # Min-Max Events to monitor
            0x8010,  
            None,                  # No DLL module handle
            MonitoringHook.event_callback,          # Callback function
            process_id,            # Process ID (0 means all processes)
            0,                     # Thread ID (0 means all threads)
            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS  # Flags: Out of context
        )

        if not self.event_hook:
            raise WinError(get_last_error())
        
    def run_process_hook(self, process):
        try:
            msg = MSG()
            timeout = 60
            start_time = time.time()
            PM_REMOVE = 0x0001

            while True:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    print("Timeout reached. Exiting...")
                    break

                if windll.user32.PeekMessageW(byref(msg), None, 0, 0, PM_REMOVE):
                    windll.user32.TranslateMessage(byref(msg))
                    windll.user32.DispatchMessageW(byref(msg))

                # if user32.GetMessageW(byref(msg), None, 0, 0) > 0:
                #     user32.TranslateMessage(byref(msg))
                #     user32.DispatchMessageW(byref(msg))
                # else:
                #     break  # Exit if no messages are pending

        except KeyboardInterrupt:
            print("Exiting...")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            windll.user32.UnhookWinEvent(self.event_hook)
