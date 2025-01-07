import win32gui
import win32ui
import win32con
import win32api

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
FONT_NAME = "Arial"
FONT_SIZE = 300
WHITE = 0xFFFFFF
BLACK = 0x000000

# Create a global variable to store the current keypress
current_key = ""

def create_window():
    """Creates a basic Windows GUI window using pywin32."""
    class_name = "KeypressDisplay"
    
    # Register the window class
    wc = win32gui.WNDCLASS()
    wc.lpszClassName = class_name
    wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
    wc.hbrBackground = win32con.COLOR_WINDOW
    wc.lpfnWndProc = wnd_proc
    win32gui.RegisterClass(wc)
    
    # Create the window
    hwnd = win32gui.CreateWindowEx(
        0,
        class_name,
        "Keypress Display",
        win32con.WS_OVERLAPPED | win32con.WS_CAPTION | win32con.WS_SYSMENU,
        win32con.CW_USEDEFAULT,
        win32con.CW_USEDEFAULT,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        0,
        0,
        0,
        None
    )
    
    # Show the window
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.UpdateWindow(hwnd)
    return hwnd

def draw_text(hwnd, text):
    """Draws the specified text on the window."""
    hdc, paint_struct = win32gui.BeginPaint(hwnd)
    hdc = win32ui.CreateDCFromHandle(hdc)
    
    # Clear the screen
    brush = win32ui.CreateBrush(win32con.BS_SOLID, WHITE, 0)
    rect = win32gui.GetClientRect(hwnd)
    win32gui.FillRect(hdc.GetHandleOutput(), rect, brush.GetSafeHandle())
    
    # Select font
    font = win32ui.CreateFont({
        "name": FONT_NAME,
        "height": FONT_SIZE,
        "weight": win32con.FW_NORMAL
    })
    hdc.SelectObject(font)
    
    # Set text color
    hdc.SetTextColor(BLACK)
    hdc.SetBkColor(WHITE)
    
    # Get text size
    text_size = hdc.GetTextExtent(text)
    
    # Calculate center position
    x = (SCREEN_WIDTH - text_size[0]) // 2
    y = (SCREEN_HEIGHT - text_size[1]) // 2
    
    # Draw the text
    hdc.TextOut(x, y, text)
    
    # Cleanup
    win32gui.EndPaint(hwnd, paint_struct)

def wnd_proc(hwnd, msg, w_param, l_param):
    """Handles Windows messages."""
    global current_key

    if msg == win32con.WM_DESTROY:
        win32gui.PostQuitMessage(0)
    elif msg == win32con.WM_KEYDOWN:
        current_key = chr(w_param)  # Get the key as a character
        win32gui.InvalidateRect(hwnd, None, True)  # Trigger a repaint
    elif msg == win32con.WM_PAINT:
        draw_text(hwnd, current_key)  # Redraw the screen
    else:
        return win32gui.DefWindowProc(hwnd, msg, w_param, l_param)

    return 0

def main():
    """Main function to run the application."""
    hwnd = create_window()
    win32gui.PumpMessages()

if __name__ == "__main__":
    main()
