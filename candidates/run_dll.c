#include <windows.h>
#include <stdio.h>

typedef int (*MainFunc)();  // Define the function signature of 'main' in the DLL

int main() {
    // Load the DLL
    HMODULE hDll = LoadLibrary("keypress_display_win32.dll");  // Path to your DLL
    if (hDll == NULL) {
        printf("Unable to load DLL: %lu\n", GetLastError());
        return 1;
    }

    // Get the function pointer to the 'main' function from the DLL
    MainFunc mainFunc = (MainFunc)GetProcAddress(hDll, "main");
    if (mainFunc == NULL) {
        printf("Unable to find the 'main' function in DLL\n");
        FreeLibrary(hDll);
        return 1;
    }

    // Call the 'main' function from the DLL
    int result = mainFunc();  // Call the function like a regular C function
    printf("DLL main function returned: %d\n", result);

    // Free the DLL after use
    FreeLibrary(hDll);
    return 0;
}
