import subprocess
import time
import sys

import pyautogui

# Function to launch the target script and profile latency
def profile_script(script_name):
    # Start the script as a subprocess
    # process = subprocess.Popen(
    #     [sys.executable, script_name],
    #     stdin=subprocess.PIPE,
    #     stdout=subprocess.PIPE, 
    #     stderr=subprocess.PIPE,
    #     text=True
    # )

    scalene_command = [
        'scalene', script_name
    ]
    
    process = subprocess.Popen(
        scalene_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Give the process a moment to start
    time.sleep(5)

    try:

        # Find the window associated with the subprocess (by title)
        subprocess_window = None
        windows = pyautogui.getWindowsWithTitle("Keypress Display")  # Replace with your window title
        if windows:
            subprocess_window = windows[0]
            subprocess_window.activate()  # Bring the window to the front

        if subprocess_window is None:
            print("Window not found, unable to bring to front.")
            return

        print("Got here")
        pyautogui.keyDown("a")  # Simulate key press

        output, error = process.wait(timeout=60)
        print(output)
        print(error)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the process
        process.terminate()

if __name__ == "__main__":
    script_name = "test-bench/capture_tkinter.py"  # Replace with your actual script name
    profile_script(script_name)