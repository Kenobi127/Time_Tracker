import keyboard
import win32gui
import win32con

hwnd = win32gui.GetForegroundWindow()  # Get the currently active window




while(True):
    if keyboard.is_pressed("+"):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    if keyboard.is_pressed("-"):
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

