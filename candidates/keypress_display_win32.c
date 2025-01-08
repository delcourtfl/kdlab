#include <windows.h>
#include <stdio.h>
#include <ctype.h>

#define SCREEN_WIDTH 400
#define SCREEN_HEIGHT 400
#define FONT_NAME "Arial"
#define FONT_SIZE 300
#define WHITE RGB(255, 255, 255)
#define BLACK RGB(0, 0, 0)

// gcc -shared -o keypress_display_win32.dll keypress_display_win32.c -mwindows
// gcc -shared -O2 -march=native -flto -o keypress_display_win32_O2.dll keypress_display_win32.c -mwindows
// gcc -shared -O3 -march=native -flto -o keypress_display_win32_O3.dll keypress_display_win32.c -mwindows

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);
void DrawTextToWindow(HWND hwnd, const char* text, HFONT hFont);

HINSTANCE hInst;

int main() {
    WNDCLASS wc = {0};
    HWND hwnd;
    MSG Msg;

    // Register Window Class
    wc.lpfnWndProc = WndProc; // Set Window Procedure
    wc.hInstance = hInst = GetModuleHandle(NULL);
    wc.lpszClassName = "KeypressDisplay";
    wc.hbrBackground = CreateSolidBrush(WHITE);

    if (!RegisterClass(&wc)) {
        MessageBox(NULL, "Window Registration Failed!", "Error", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    // Create Window
    hwnd = CreateWindowEx(
        0,
        wc.lpszClassName,
        "Keypress Display",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, SCREEN_WIDTH, SCREEN_HEIGHT,
        NULL, NULL, hInst, NULL);

    if (hwnd == NULL) {
        MessageBox(NULL, "Window Creation Failed!", "Error", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    ShowWindow(hwnd, SW_SHOWNORMAL);
    UpdateWindow(hwnd);

    // Message Loop
    while (GetMessage(&Msg, NULL, 0, 0)) {
        TranslateMessage(&Msg);
        DispatchMessage(&Msg);
    }

    return Msg.wParam;
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static HDC hdc;
    static HFONT hFont;
    static HBRUSH hBrush;

    switch (msg) {
        case WM_CREATE:
            // Initialize GDI resources (font, brush)
            hdc = GetDC(hwnd);
            hFont = CreateFont(FONT_SIZE, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_SWISS, FONT_NAME);
            hBrush = CreateSolidBrush(WHITE);
            return 0;

        case WM_KEYDOWN:
            // Handle key press and draw the text
            char keyChar = (char)wParam;
            DrawTextToWindow(hwnd, &keyChar, hFont);  // Draw the pressed key
            return 0;

        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;

        default:
            return DefWindowProc(hwnd, msg, wParam, lParam);
    }
}

void DrawTextToWindow(HWND hwnd, const char* text, HFONT hFont) {
    HDC hdc = GetDC(hwnd);
    RECT rect;

    // Get the client rectangle of the window
    GetClientRect(hwnd, &rect);

    // Clear the background with white
    SetBkColor(hdc, WHITE);
    ExtTextOut(hdc, 0, 0, ETO_OPAQUE, &rect, NULL, 0, NULL); // This fills the rectangle with the background color

    // Set text attributes
    SetTextColor(hdc, BLACK);
    SelectObject(hdc, hFont);

    // Draw the text at the center of the window
    char firstChar[2] = {tolower(text[0]), '\0'};
    DrawTextA(hdc, firstChar, -1, &rect, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    ReleaseDC(hwnd, hdc);
}
