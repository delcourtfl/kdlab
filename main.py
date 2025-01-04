

from latency_bench.controllers.monitoring_hook import MonitoringHook
from latency_bench.controllers.input_controller import InputController
from latency_bench.controllers.display_recorder import DisplayRecorder

from ctypes import windll, byref, c_longlong, WINFUNCTYPE, c_int, cast, POINTER, c_long, c_void_p, c_int, c_size_t, Union, POINTER, sizeof, WinError, get_last_error
from ctypes.wintypes import LPARAM, WPARAM, DWORD, WORD, ULONG, LONG, MSG, HWND, HANDLE
import win32gui
import win32con
import subprocess
from pathlib import Path
import time
import timeit

# Benchmarking

# Keypress event
# Display change event

class Benchmark:
    def __init__(self):

        # QueryPerformanceCounter and Frequency Setup

        # self.monitoring_hook = MonitoringHook()

        # self.input_controller = InputController()
        # self.display_recorder = DisplayRecorder("Keypress Display")

        pass

    def send_and_monitor(self):
        """
        Function to send key press and monitor the display.
        This function will be timed using timeit.
        """
        self.input_controller.toggle_key(0x20)  # Press 'Space'
        self.input_controller.toggle_key(0x41)  # Press 'A'
        self.display_recorder.start_monitoring_no_timer()  # Monitor screen
        # self.input_controller.press_key(0x20)  # Press 'Space'
        return True

    def run(self):
        
        # Define the path to the script
        script_path = Path(__file__).resolve().parent / "candidates" / "capture_tkinter.py"

        # Run the script in a subprocess
        try:
            process = subprocess.Popen(
                ["python", str(script_path)],
                stdout=subprocess.PIPE,  # Capture stdout if needed
                stderr=subprocess.PIPE,  # Capture stderr if needed
                text=True                # Output as strings, not bytes
            )

            time.sleep(2)

            self.display_recorder = DisplayRecorder("Keypress Display")
            self.input_controller = InputController(self.display_recorder.hwnd)

            # Press the space key to reset the display
            self.input_controller.toggle_key(0x20)
            time.sleep(0.5)
            self.display_recorder.set_initial_hash()


            ns_start = time.perf_counter_ns()
            self.input_controller.press_key(0x41)
            ns_end = self.display_recorder.start_monitoring()
            print(f"Time taken: {ns_end - ns_start} ns")

            # print("Sending key press event")
            # while True:
            #     ns_start = time.perf_counter_ns()
            #     self.input_controller.press_key(0x41)
            #     ns_end = self.display_recorder.start_monitoring()
            #     print(f"Time taken: {ns_end - ns_start} ns")

            #     time.sleep(0.5)
            #     self.input_controller.press_key(0x20)
            #     time.sleep(0.5)

            # event_time = timeit.timeit(self.send_and_monitor, number=5000)
            # print(f"Event time: {event_time}")

            print("Sending key press event")
            while True:
                ns_start = time.perf_counter_ns()
                self.input_controller.press_key(0x41)
                ns_end = self.display_recorder.start_monitoring()
                print(f"Time taken: {ns_end - ns_start} ns")

                self.input_controller.press_key(0x20)
                time.sleep(0.5)

                return
            
            stdout, stderr = process.communicate()
            print("Subprocess completed.")
            print("Output:", stdout)
            print("Errors:", stderr)

        except subprocess.CalledProcessError as e:
            print(f"Script failed with error code {e.returncode}")
            print("Error output:")
            print(e.stderr)       # Print the script's standard error
        except Exception as e:
            print(f"An error occurred: {e}")


def main():
    benchmark = Benchmark()
    benchmark.run()

if __name__ == "__main__":
    main()