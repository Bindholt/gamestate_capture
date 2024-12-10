import os
import threading
from datetime import datetime
from time import sleep
import mss
import mss.tools
from pynput import keyboard

# Define a list to represent the state of the keys: [w, a, s, d, e]
key_states = [0, 0, 0, 0, 0]
key_mapping = {'w': 0, 'a': 1, 's': 2, 'd': 3, 'e': 4}


# Key press handler
def on_press(key):
    try:
        if key.char in key_mapping:
            key_states[key_mapping[key.char]] = 1
            if key.char == 'e':
                capture_game_state()
    except AttributeError:
        pass


# Key release handler
def on_release(key):
    try:
        if key.char in key_mapping:
            key_states[key_mapping[key.char]] = 0
    except AttributeError:
        pass


def get_key_state_folder():
    """Generate folder name based on the current key states."""
    return "_".join(map(str, key_states))


def ensure_folder_exists(folder_path):
    """Ensure the specified folder exists."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def capture_game_state():
    """Capture a screenshot and save it in a folder named after the key states."""
    # Get the current key state folder name
    folder_name = f"screenshots/{get_key_state_folder()}"
    ensure_folder_exists(folder_name)

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]  # Add milliseconds
    screenshot_file = f"{folder_name}/{timestamp}.png"

    # Capture and save the screenshot
    capture_screenshot(screenshot_file)
    print(f"Screenshot saved: {screenshot_file}", end='\r')  # Optional: Show the log in the terminal


def capture_screenshot(file_path):
    """Capture a screenshot of the game region."""
    with mss.mss() as sct:
        # Define the region to capture
        region = {"top": 160, "left": 0, "width": 1000, "height": 400}

        # Capture the screen
        screenshot = sct.grab(region)

        # Save the screenshot
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=file_path)


def log_inputs_to_files():
    """Continuously log key states and screenshots based on key states."""
    try:
        while True:
            # Get the current key state folder name
            folder_name = f"screenshots/{get_key_state_folder()}"
            ensure_folder_exists(folder_name)

            # Only save a screenshot if any key is pressed
            if any(state == 1 for state in key_states):
                # Get the current timestamp and file path
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
                screenshot_file = f"{folder_name}/{timestamp}.png"

                # Capture and save the screenshot
                capture_screenshot(screenshot_file)
                print(f"Screenshot saved: {screenshot_file}", end='\r')
            sleep(1 / 3)  # Log 3 times a second
    except KeyboardInterrupt:
        print("\nExiting...")


# Listener setup
def start_listener():
    """Start the keyboard listener."""
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    # Use threading to run the listener and logger simultaneously
    threading.Thread(target=start_listener, daemon=True).start()
    log_inputs_to_files()
