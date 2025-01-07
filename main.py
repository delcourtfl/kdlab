

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
from datetime import datetime

import pstats

# Benchmarking
# Keypress event
# Display change event

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the path to the 'data' folder relative to the root directory
data_folder = Path(ROOT_DIR) / "data"
# Ensure the 'data' folder exists
data_folder.mkdir(parents=True, exist_ok=True)

# Create subfolders 'img/' and 'perf/'
img_folder = data_folder / "img"
perf_folder = data_folder / "perf"

img_folder.mkdir(parents=True, exist_ok=True)
perf_folder.mkdir(parents=True, exist_ok=True)

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

        self.results = {}

    def run_all(self):
        for file in self.candidate_files:
            print(f"Running benchmark for file: {file}")
            self.run(file)

    def run(self, script_path=None):

        if not script_path:
            raise ValueError("Script path not provided.")
        

        save_path = img_folder / script_path.stem  # Get the file name without extension
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
            self.input_controller.toggle_key_scancode(0x10)
            time.sleep(0.5)
            self.display_recorder.set_objective()
            self.display_recorder.capture_window(save_path)

            # Press the space key to reset the display
            win32gui.SetForegroundWindow(self.display_recorder.hwnd)
            self.input_controller.toggle_key_scancode(0x39)
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
                # print("Terminating subprocess...")
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
            # print("Subprocess terminated.")
            if stdout:
                print("Output:", stdout)
            if stderr:
                print("Errors:", stderr)


    def run_all_with_cprofile(self):
        for file in self.candidate_files:
            print(f"Running benchmark with profiler for file: {file}")
            self.run_with_cprofile(file)

    def run_with_cprofile(self, script_path=None):

        if not script_path:
            raise ValueError("Script path not provided.")
        

        file_path = img_folder / script_path.stem  # Get the file name without extension
        save_path = file_path.with_suffix(".png")   # Change the extension to '.png'
        file_path = perf_folder / script_path.stem
        prof_path = file_path.with_suffix(".prof")   # Change the extension to '.prof'

        # Run the script in a subprocess
        try:
            process = subprocess.Popen(
                ["python", "-m", "cProfile", "-o", str(prof_path), str(script_path)],
                stdout=subprocess.PIPE,  # Capture stdout if needed
                stderr=subprocess.PIPE,  # Capture stderr if needed
                text=True                # Output as strings, not bytes
            )

            time.sleep(5)
            self.display_recorder = DisplayRecorder("Keypress Display")
            self.input_controller = InputController(self.display_recorder.hwnd)

            # Press the 'a' key to reset the display
            win32gui.SetForegroundWindow(self.display_recorder.hwnd)
            self.input_controller.toggle_key_scancode(0x10)
            time.sleep(0.5)
            self.display_recorder.set_objective()
            self.display_recorder.capture_window(save_path)

            # Press the space key to reset the display
            win32gui.SetForegroundWindow(self.display_recorder.hwnd)
            self.input_controller.toggle_key_scancode(0x39)
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
                self.results[script_path.stem] = average_time
            finally:
                if gcold:
                    gc.enable()

            self.input_controller.send_close_signal()
            time.sleep(1)
            
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
                print("Killing subprocess...")
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
            self.input_controller.toggle_key_scancode(0x10)
            ns_end = self.display_recorder.start_monitoring()

            self.input_controller.toggle_key_scancode(0x39)
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
            self.input_controller.toggle_key_scancode(0x10)
            ns_end = self.display_recorder.start_monitoring()
            time_taken = ns_end - ns_start
            # print(f"Time taken: {time_taken} ns")
            average_time = (average_time * (cnt - 1) + time_taken) / cnt

            self.input_controller.toggle_key_scancode(0x39)
            self.display_recorder.start_monitoring_initial()

        return average_time

    def process_prof_files(self):
        """Process all .prof files in the 'data' folder."""
        # Loop through the 'data' folder to find .prof files
        for prof_file in perf_folder.iterdir():
            if prof_file.suffix == ".prof":

                print(f"Processing {prof_file}")
                # Create the output file path
                output_file = perf_folder / f"{prof_file.stem}.txt"
                try:
                    # Open the .prof file and use pstats to process it
                    p = pstats.Stats(str(prof_file))
                    
                    # Save the result to a file instead of printing it
                    with open(output_file, 'w') as f:
                        # Redirect the output to the file
                        p.sort_stats('tottime').stream = f
                        p.print_stats(10)
                        
                    print(f"Output saved to {output_file}")
                except Exception as e:
                    print(f"Error processing {prof_file}: {e}")

    def save_results(self):
        print("Saving results...")
        sorted_results = sorted(self.results.items(), key=lambda item: item[1])
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        result_file = data_folder / f"results_{current_time}.txt"

        with open(result_file, "w") as f:
            f.write("Benchmark Results (ordered by latency):\n")
            for key, value in sorted_results:
                print(f"{key}: {value} ns")
                f.write(f"{key}: {value} ns\n")


def main():
    benchmark = Benchmark()
    benchmark.run_all_with_cprofile()
    # Iterate through each .prof file
    benchmark.process_prof_files()

    benchmark.save_results()

if __name__ == "__main__":
    main()