from pynput import keyboard
from time import sleep
from datetime import datetime
import threading
import pyautogui
import os

# Define a list to represent the state of the keys: [w, a, s, d, e]
key_states = [0, 0, 0, 0, 0]
key_mapping = {'w': 0, 'a': 1, 's': 2, 'd': 3, 'e': 4}

# Key press handler
def on_press(key):
    try:
        if key.char in key_mapping:
            key_states[key_mapping[key.char]] = 1
    except AttributeError:
        pass

# Key release handler
def on_release(key):
    try:
        if key.char in key_mapping:
            key_states[key_mapping[key.char]] = 0
    except AttributeError:
        pass


def capture_screenshot(timestamp):
    region = (0, 120, 800, 370)
    # Take screenshot
    screenshot = pyautogui.screenshot(region=region)

    # File name for the screenshot with timestamp
    screenshot_file = f"screenshots/{timestamp}.png"

    # Save the screenshot
    screenshot.save(screenshot_file)


def log_inputs_to_files():
    try:
        while True:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]  # Add milliseconds
            # File name for the current log
            file_name = f"keylog/{timestamp}.txt"

            print(key_states) # DOESN'T WORK WITHOUT THIS PRINT STATEMENT DO NOT TOUCH!
            if any(state == 1 for state in key_states):
                # Capture screenshot with the same timestamp
                capture_screenshot(timestamp)
                # Write the key states to the file
                with open(file_name, "w") as file:
                    file.write(f"{key_states}")
                print(f"Logged: {file_name}", end='\r')  # Optional: Show the log in the terminal
            sleep(1 / 3)  # Log 3 times a second
    except KeyboardInterrupt:
        print("\nExiting...")


# Listener setup
def start_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    # Use threading to run the listener and logger simultaneously
    threading.Thread(target=start_listener, daemon=True).start()
    log_inputs_to_files()