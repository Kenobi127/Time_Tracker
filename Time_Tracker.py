# Time_Tracker.py
# By: Mateo Lopez Moncaleano
# Description: A Windows task tracker that logs tasks, breaks, and total time into a CSV file.
# Created: 2025-11-09
# Version: 1.0

import keyboard
import win32gui
import win32con
import time
from datetime import datetime, timedelta
import ctypes
import os
import csv
import sys

ctypes.windll.kernel32.SetConsoleTitleW("Time Tracker App")
time.sleep(0.1) #sometimes the title wont be set before hwnd happens, so small delay
hwnd = win32gui.FindWindow(None, "Time Tracker App")

START_HOTKEY = "f1"
END_HOTKEY = "f2"
BREAK_HOTKEY = "f3"
DELAY_TIME = 2 #seconds

running_task = False
running_break = False
task_name = ""

task_start_time = None
task_end_time = None

break_start_time = None
break_end_time = None
total_break_time = timedelta(0)

TIME_FORMAT = "%H:%M:%S"

if getattr(sys, 'frozen', False):
    #directory of the .exe
    BASE_DIR = os.path.dirname(sys.executable)  
else:
    #path of the current folder as a python file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(BASE_DIR, "task.csv")

file_exists = os.path.exists(CSV_FILE)

while True:
    try:
        #open the file in append mode
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            print(f"CSV file path: {CSV_FILE}")
            #write header only if file didn't exist
            if not file_exists:
                writer.writerow(["Task", "Start Time", "End Time", "Total Time", "Break Time", "Date"])
            break

    #openign file error handler
    except Exception as e:
        print(f"Error writing to {CSV_FILE}: {e}")
        input("Close any programs using the CSV and press Enter to try again...")


def update_settings():
    global START_HOTKEY, END_HOTKEY, BREAK_HOTKEY, DELAY_TIME

    while True:
        START_HOTKEY = get_valid_hotkey("Enter START hotkey: ")
        print(f"START hotkey set to: {START_HOTKEY}")
        if input("Enter Y to save: ").upper() == "Y":
            break

    while True:
        END_HOTKEY = get_valid_hotkey("Enter STOP hotkey: ")
        print(f"END hotkey set to: {END_HOTKEY}")
        if input("Enter Y to save: ").upper() == "Y":
            break

    while True:
        BREAK_HOTKEY = get_valid_hotkey("Enter BREAK hotkey: ")
        print(f"BREAK hotkey set to: {BREAK_HOTKEY}")
        if input("Enter Y to save: ").upper() == "Y":
            break

    while True:
        try:
            DELAY_TIME = float(input("Enter how many seconds you want the terminal to pop-up: "))
            print(f"Delay time set to: {DELAY_TIME} seconds")
            if input("Enter Y to save: ").upper() == "Y":
                break
        except ValueError:
            print("Please enter a valid number.")
        
    
def get_valid_hotkey(prompt):
    while True:
        key = input(prompt).strip().lower()
        try:
            #test if it works by trying to add a temporary hotkey
            keyboard.add_hotkey(key, lambda: None)
            keyboard.remove_hotkey(key)
            return key
        except (ValueError, keyboard.KeyboardEvent):
            print(f"'{key}' is not a valid key. Try again.")

#short delay restore and minimize
def short_restore():
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(DELAY_TIME)
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def minimize():
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def restore():
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)  #get keyboard focus

#saves the task into a csv file
def save_task():
    global total_break_time
    total_task_time = timedelta(seconds=int((task_end_time - task_start_time).total_seconds())) #calculate total time and remove microseconds
    total_break_time = timedelta(seconds=int(total_break_time.total_seconds()))  #remove microseconds
    date = task_start_time.strftime("%Y-%m-%d")

    while True:
        try:
            with open(CSV_FILE, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    task_name,
                    task_start_time.strftime(TIME_FORMAT),
                    task_end_time.strftime(TIME_FORMAT),
                    total_task_time,
                    total_break_time,
                    date
                ])
            print(f"{datetime.now().strftime(TIME_FORMAT)}: Task '{task_name}' saved! Total: {total_task_time}, Break: {total_break_time}")
            total_break_time = timedelta(0)
            break
        except Exception as e:
            print(f"{datetime.now().strftime(TIME_FORMAT)}: Failed to save task '{task_name}': {e}")
            input("Close any programs using the CSV and press Enter to try again...")

#prompts the user to enter a task name, takes the time and minimizes
def start_task():
    global running_task, task_name, task_start_time
    restore()
    if running_task:
        restore()
        print(f"{datetime.now().strftime(TIME_FORMAT)}: Task running, press {END_HOTKEY} first to end task.")
        time.sleep(DELAY_TIME)
        minimize()
        return
    running_task = True
    task_name = input(f"{datetime.now().strftime(TIME_FORMAT)}: Enter new task name: ")
    task_start_time = datetime.now()
    print(f"{task_start_time.strftime(TIME_FORMAT)}: New task '{task_name}' started.")
    minimize()

#checks if there is a current task, ends it and calls save task
def end_task():
    global running_task, running_break, task_end_time
    restore()
    if not running_task:
        print(f"{datetime.now().strftime(TIME_FORMAT)}: No task is currently running. Press {START_HOTKEY} to start a task.")
    else:
        if running_break:
            stop_break()  # stop break if running
        task_end_time = datetime.now()
        save_task()
        running_task = False

    time.sleep(DELAY_TIME)
    minimize()
    
#checks if running break, stops it or starts it
def toggle_break():
    global running_break, break_start_time, total_break_time
    restore()
    if not running_task:
        print(f"{datetime.now().strftime(TIME_FORMAT)}: No task running.")
    elif running_break:
        stop_break()
        return
    else:
        running_break = True
        break_start_time = datetime.now()
        print(f"{datetime.now().strftime(TIME_FORMAT)}: Break started.")

    time.sleep(DELAY_TIME)
    minimize()

#stops break and calculates total_break_time
def stop_break():
    global running_break, break_start_time, total_break_time
    if running_break:
        running_break = False
        now = datetime.now()
        total_break_time += now - break_start_time
        total_break_time = timedelta(seconds=int(total_break_time.total_seconds()))
        print(f"{now.strftime(TIME_FORMAT)}: Break stopped, total break: {total_break_time}")
        time.sleep(DELAY_TIME)
        minimize()


if input("Do you want to update the hotkeys and delay time of the console? Y/N or Enter to continue with defaults: ").upper() == "Y":
    update_settings()
    os.system('cls')

keyboard.add_hotkey(START_HOTKEY, start_task)
keyboard.add_hotkey(END_HOTKEY, end_task)
keyboard.add_hotkey(BREAK_HOTKEY, toggle_break)

print(f"Press {START_HOTKEY} to start, {END_HOTKEY} to end, {BREAK_HOTKEY} to toggle break.")
print("Press Ctrl+C in this console to exit.")

keyboard.wait()
