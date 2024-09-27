import tkinter as tk
from tkinter import scrolledtext, font
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
import time
import os
import keyboard


def find_window(title):
    windows = gw.getWindowsWithTitle(title)
    return windows[0] if windows else None


def screenshot(window):
    try:
        window.activate()
        time.sleep(0.1)
    except Exception as e:
        log_to_console(f"Failed to activate window: {e}")
    return np.array(
        pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
    )


def find_image(screenshot, target_path):
    target = cv2.imread(target_path, cv2.IMREAD_COLOR)
    result = cv2.matchTemplate(screenshot, target, cv2.TM_CCOEFF_NORMED)
    if (max_val := result.max()) >= 0.8:
        return (
            np.unravel_index(result.argmax(), result.shape),
            target.shape[1],
            target.shape[0],
        )
    return None, None, None


def click_image(location, window, width, height):
    if location is not None:
        center_x = location[1] + width // 2
        center_y = location[0] + height // 2
        click_x = window.left + center_x
        click_y = window.top + center_y
        pyautogui.moveTo(click_x, click_y, duration=0.05)
        pyautogui.click(click_x, click_y)
        log_to_console(f"Clicked on the location ({click_x}, {click_y})")


def find_and_click_images(screenshot, window, folder_path):
    for img_name in os.listdir(folder_path):
        if img_name.endswith((".png", ".jpg", ".jpeg")):
            location, width, height = find_image(
                screenshot, os.path.join(folder_path, img_name)
            )
            if location:
                click_image(location, window, width, height)
                return location, width, height
    return None, None, None


def handle_dialog():
    time.sleep(0.5)
    new_window = next(
        (
            w
            for w in gw.getAllWindows()
            if "Dialog" in w.title or "Football Manager" in w.title
        ),
        None,
    )
    if new_window:
        new_window.activate()
        screenshot_img = screenshot(new_window)
        options_folder = "images"
        location = find_and_click_images(screenshot_img, new_window, options_folder)
        if not location:
            log_to_console("No option found in new window.")
        time.sleep(0.5)
        location, width, height = find_image(screenshot(new_window), "images/step3.jpg")
        if location:
            click_image(location, new_window, width, height)


def start_clicking():
    global running
    running = True
    log_to_console("Starting to automatically click...")
    process_clicking()


def stop_clicking():
    global running
    running = False
    log_to_console("Auto-clicking has been stopped.")


def scroll_and_search(window, direction="down"):
    pyautogui.moveTo(1408, 605)
    for _ in range(3):
        if direction == "down":
            pyautogui.scroll(-300)
            log_to_console("Scrolled down the screen.")
        else:
            pyautogui.scroll(300)
            log_to_console("Scrolled screen up.")
        time.sleep(0.5)
        screenshot_img = screenshot(window)
        if find_image(screenshot_img, "images/pray.jpg")[0]:
            return True
    return False


def process_clicking():
    global last_location, last_width, last_height
    if not running:
        return

    game_title = "Football Manager 2024"
    window = find_window(game_title)

    if window:
        screenshot_img = screenshot(window)
        location, width, height = find_image(screenshot_img, "images/pray.jpg")

        if location:
            last_location = location
            last_width = width
            last_height = height
            click_image(location, window, width, height)
            handle_dialog()
        else:
            if last_location and last_width and last_height:
                if scroll_and_search(window, "down") or scroll_and_search(window, "up"):
                    click_image(last_location, window, last_width, last_height)
                    handle_dialog()
            else:
                if not scroll_and_search(window, "down"):
                    scroll_and_search(window, "up")

    if keyboard.is_pressed("q"):
        stop_clicking()
        log_to_console("The program was terminated with the key 'q'.")
        root.quit()
        return

    root.after(1000, process_clicking)


def log_to_console(message):
    console_text.config(state=tk.NORMAL)
    console_text.insert(tk.END, f"{message}\n")
    console_text.yview(tk.END)
    console_text.config(state=tk.DISABLED)


def create_control_panel():
    global root, console_text
    root = tk.Tk()
    root.title("Football Manager 24 Training")

    root.configure(bg="#2E3B4E")

    title_label = tk.Label(
        root,
        text="Football Manager 24 Training",
        font=("Helvetica", 16, "bold"),
        bg="#2E3B4E",
        fg="#FFFFFF",
    )
    title_label.pack(pady=10)

    start_button = tk.Button(
        root,
        text="Start",
        command=start_clicking,
        bg="#28A745",
        fg="#FFFFFF",
        font=("Helvetica", 12),
        width=15,
    )
    start_button.pack(pady=5)

    stop_button = tk.Button(
        root,
        text="Stop",
        command=stop_clicking,
        bg="#DC3545",
        fg="#FFFFFF",
        font=("Helvetica", 12),
        width=15,
    )
    stop_button.pack(pady=5)

    console_text = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        height=10,
        width=50,
        bg="#FFFFFF",
        fg="#000000",
        font=("Helvetica", 12),
    )
    console_text.pack(pady=10)
    console_text.config(state=tk.DISABLED)

    quit_button = tk.Button(
        root,
        text="Finish",
        command=quit_program,
        bg="#007BFF",
        fg="#FFFFFF",
        font=("Helvetica", 12),
        width=15,
    )
    quit_button.pack(pady=5)

    window_width = 400
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()


def quit_program():
    stop_clicking()
    log_to_console("Program completed.")
    root.quit()


running = False
last_location = None
last_width = None
last_height = None

create_control_panel()
