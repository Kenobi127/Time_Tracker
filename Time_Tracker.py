import keyboard
import win32gui
import win32con
import time
from datetime import datetime, timedelta
import ctypes
import os
import csv

ctypes.windll.kernel32.SetConsoleTitleW("Time Tracker App")
time.sleep(0.1)
hwnd = win32gui.FindWindow(None, "Time Tracker App")

START_HOTKEY = "+"
END_HOTKEY = "-"
BREAK_HOTKEY = "*"

running_task = False
running_break = False
task_name = ""

task_start_time = None
task_end_time = None

break_start_time = None
break_end_time = None
total_break_time = timedelta(0)

TIME_FORMAT = "%H:%M:%S"

CSV_FILE = "tasks.csv"
file_exists = os.path.exists(CSV_FILE)

input("hello")


try:
    # Check if the file already exists
    file_exists = os.path.exists(CSV_FILE)

    # Open the file in append mode
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header only if file didn't exist
        if not file_exists:
            writer.writerow(["Task", "Start Time", "End Time", "Total Time (min)", "Break Time (min)", "Date"])


except Exception as e:
    print(f"Error writing to {CSV_FILE}: {e}")



input("hello")



def short_restore():
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(3)
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def minimize():
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def restore():
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

def save_task():
    global total_break_time
    total_task_time = (task_end_time - task_start_time).total_seconds() / 60
    total_break_minutes = total_break_time.total_seconds() / 60
    date = task_start_time.strftime("%m-%d-%Y")
    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            task_name,
            task_start_time.strftime(TIME_FORMAT),
            task_end_time.strftime(TIME_FORMAT),
            round(total_task_time,2),
            round(total_break_minutes,2),
            date
        ])
    print(f"{datetime.now().strftime(TIME_FORMAT)}: Task '{task_name}' saved! Total: {round(total_task_time,2)} min, Break: {round(total_break_minutes,2)} min")
    total_break_time = timedelta(0)

def start_task():
    global running_task, task_name, task_start_time
    if running_task:
        restore()
        input(f"{datetime.now().strftime(TIME_FORMAT)}: Task running, press {END_HOTKEY} to end task first.")
        minimize()
        return
    running_task = True
    restore()
    task_name = input(f"{datetime.now().strftime(TIME_FORMAT)}: Enter new task name: ")
    task_start_time = datetime.now()
    print(f"{task_start_time.strftime(TIME_FORMAT)}: New task '{task_name}' started.")
    minimize()

def end_task():
    global running_task, running_break, task_end_time
    if not running_task:
        restore()
        print(f"{datetime.now().strftime(TIME_FORMAT)}: No task is currently running. Press {START_HOTKEY} to start a task.")
        time.sleep(1.5)
        minimize()
        return
    if running_break:
        stop_break()
    restore()
    task_end_time = datetime.now()
    save_task()
    input(f"{datetime.now().strftime(TIME_FORMAT)}: Press enter to minimize.")
    running_task = False
    minimize()

def toggle_break():
    global running_break, break_start_time, total_break_time
    if not running_task:
        restore()
        print(f"{datetime.now().strftime(TIME_FORMAT)}: No task running.")
        time.sleep(1.5)
        minimize()
        return
    restore()
    if running_break:
        stop_break()
    else:
        running_break = True
        break_start_time = datetime.now()
        print(f"{datetime.now().strftime(TIME_FORMAT)}: Break started.")
        time.sleep(1)
        minimize()

def stop_break():
    global running_break, break_start_time, total_break_time
    if running_break:
        running_break = False
        now = datetime.now()
        total_break_time += now - break_start_time
        print(f"{datetime.now().strftime(TIME_FORMAT)}: Break stopped, total break: {round(total_break_time.total_seconds()/60,2)} min")
        time.sleep(1)
        minimize()

keyboard.add_hotkey(START_HOTKEY, start_task)
keyboard.add_hotkey(END_HOTKEY, end_task)
keyboard.add_hotkey(BREAK_HOTKEY, toggle_break)

print(f"Press {START_HOTKEY} to start, {END_HOTKEY} to end, {BREAK_HOTKEY} to toggle break.")
print("Press Ctrl+C in this console to exit.")

keyboard.wait()
