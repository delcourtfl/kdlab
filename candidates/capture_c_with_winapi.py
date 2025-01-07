import ctypes

# Load the DLL
keypress_display = ctypes.CDLL('./candidates/keypress_display_win32.dll')

# Call the `main` function from the C code to create the window and start the message loop
keypress_display.main()