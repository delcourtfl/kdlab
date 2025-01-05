

from latency_bench.controllers.monitoring_hook import MonitoringHook
from latency_bench.controllers.input_controller import InputController
from latency_bench.controllers.display_recorder import DisplayRecorder

import win32gui
import win32con
import subprocess
from pathlib import Path
import time
import gc
import os

# Benchmarking
# Keypress event
# Display change event

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the path to the 'data' folder relative to the root directory
data_folder = Path(ROOT_DIR) / "data"
# Ensure the 'data' folder exists
data_folder.mkdir(parents=True, exist_ok=True)

class Benchmark:
    def __init__(self):
        # Define the path to the "candidates" folder
        self.candidates_path = Path(__file__).resolve().parent / "candidates"
        
        # Check if the folder exists
        if not self.candidates_path.exists():
            raise FileNotFoundError(f"Candidates folder not found at path: {self.candidates_path}")
        
        # Load all file paths in the folder
        self.candidate_files = [file for file in self.candidates_path.iterdir() if file.is_file()]
        print(f"Found {len(self.candidate_files)} files in candidates folder.")

    def run_all(self):
        for file in self.candidate_files:
            print(f"Running benchmark for file: {file}")
            self.run(file)
            # return

    def run(self, script_path=None):

        if not script_path:
            raise ValueError("Script path not provided.")
        

        save_path = data_folder / script_path.stem  # Get the file name without extension
        save_path = save_path.with_suffix(".png")   # Change the extension to '.png'

        # Run the script in a subprocess
        try:
            process = subprocess.Popen(
                ["python", str(script_path)],
                stdout=subprocess.PIPE,  # Capture stdout if needed
                stderr=subprocess.PIPE,  # Capture stderr if needed
                text=True                # Output as strings, not bytes
            )

            time.sleep(5)
            self.display_recorder = DisplayRecorder("Keypress Display")
            self.input_controller = InputController(self.display_recorder.hwnd)

            # Press the 'a' key to reset the display
            win32gui.SetForegroundWindow(self.display_recorder.hwnd)
            self.input_controller.toggle_key(0x41)
            time.sleep(0.5)
            self.display_recorder.set_objective()
            self.display_recorder.capture_window(save_path)

            # Press the space key to reset the display
            win32gui.SetForegroundWindow(self.display_recorder.hwnd)
            self.input_controller.toggle_key(0x20)
            time.sleep(0.5)
            self.display_recorder.set_initial()

            if self.display_recorder.initial_data == self.display_recorder.objective_data:
                raise ValueError("Failed to send key press event.")

            print("Sending key press event")

            # Disable garbage collection (see timeit.py library)
            gcold = gc.isenabled()
            gc.disable()
            try:
                # Warmup
                self.warmup()
                # Benchmark
                average_time = self.benchmark()
                print(f"Average time: {average_time} ns")
            finally:
                if gcold:
                    gc.enable()
            
           # Gracefully terminate the process
            if process.poll() is None:  # Check if process is still running
                print("Terminating subprocess...")
                process.terminate()  # Send SIGTERM signal
                process.wait(timeout=2)

        except subprocess.CalledProcessError as e:
            print(f"Script failed with error code {e.returncode}")
            print("Error output:")
            print(e.stderr)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if process.poll() is None:  # Ensure process is terminated
                process.kill()
                process.wait()

            stdout, stderr = process.communicate()
            print("Subprocess terminated.")
            if stdout:
                print("Output:", stdout)
            if stderr:
                print("Errors:", stderr)

    def warmup(self, max_iter=1000):
        """
        Function to benchmark the time taken to send a key press event and monitor the display.
        """
        cnt = 0
        while cnt < max_iter:
            cnt += 1
            win32gui.SetForegroundWindow(self.display_recorder.hwnd)

            ns_start = time.perf_counter_ns()
            self.input_controller.toggle_key(0x41)
            ns_end = self.display_recorder.start_monitoring()

            self.input_controller.toggle_key(0x20)
            self.display_recorder.start_monitoring_initial()

    def benchmark(self, max_iter=1000):
        """
        Function to benchmark the time taken to send a key press event and monitor the display.
        """
        cnt = 0
        average_time = 0

        while cnt < max_iter:
            cnt += 1
            win32gui.SetForegroundWindow(self.display_recorder.hwnd)

            ns_start = time.perf_counter_ns()
            self.input_controller.toggle_key(0x41)
            ns_end = self.display_recorder.start_monitoring()
            time_taken = ns_end - ns_start
            # print(f"Time taken: {time_taken} ns")
            average_time = (average_time * (cnt - 1) + time_taken) / cnt

            self.input_controller.toggle_key(0x20)
            self.display_recorder.start_monitoring_initial()

        return average_time


def main():
    benchmark = Benchmark()
    benchmark.run_all()

if __name__ == "__main__":
    main()