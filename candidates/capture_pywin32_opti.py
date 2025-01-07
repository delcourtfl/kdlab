import win32gui
import win32ui
import win32con

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
FONT_NAME = "Arial"
FONT_SIZE = 300
WHITE = 0xFFFFFF
BLACK = 0x000000

def create_gdi_objects():
    """Create and cache GDI objects."""

    font = win32ui.CreateFont({
        "name": FONT_NAME,
        "height": FONT_SIZE,
        "weight": win32con.FW_NORMAL
        })

    brush = win32ui.CreateBrush(win32con.BS_SOLID, WHITE, 0)

    return font, brush

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
    
    # Get GDI resources
    font, brush = create_gdi_objects()

    # Clear the screen
    rect = win32gui.GetClientRect(hwnd)
    win32gui.FillRect(hdc.GetHandleOutput(), rect, brush.GetSafeHandle())
    
    # Select font
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

    if msg == win32con.WM_DESTROY:
        win32gui.PostQuitMessage(0)
    elif msg == win32con.WM_KEYDOWN:
        win32gui.InvalidateRect(hwnd, None, True)  # Force a redraw
        current_key = chr(w_param).lower()  # Get the key as a character
        draw_text(hwnd, current_key)  # Redraw the screen
    # elif msg == win32con.WM_PAINT:
    #     pass

    return win32gui.DefWindowProc(hwnd, msg, w_param, l_param)

def main():
    """Main function to run the application."""
    # print("Creating window...")
    hwnd = create_window()
    # print("Window created. Press keys to display them.")
    win32gui.PumpMessages()

if __name__ == "__main__":
    main()
