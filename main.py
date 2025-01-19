import os
import threading
from datetime import datetime
from time import sleep
import mss
import mss.tools
from pynput import keyboard, mouse

# Define a list to represent the state of the keys: [w, a, s, d, e]
key_states = [0, 0, 0, 0, 0]
key_mapping = {'w': 0, 'a': 1, 's': 2, 'd': 3, 'e': 4}

# Initialize global variable for region
region = {"top": 0, "left": 0, "width": 0, "height": 0}
region_defined = threading.Event()  # Event to signal that region has been defined


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
    folder_name = f"test/{get_key_state_folder()}"
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
        # Check if region is defined
        if region["width"] == 0 or region["height"] == 0:
            raise ValueError("Region has not been defined. Please define the region first.")

        # Capture the screen
        screenshot = sct.grab(region)

        # Save the screenshot
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=file_path)


def define_region():
    """Capture two mouse clicks to define the screenshot region."""
    global region
    coordinates = []

    def on_click(x, y, button, pressed):
        if pressed:
            print(f"Mouse clicked at ({x}, {y})")
            coordinates.append((x, y))
            if len(coordinates) == 2:
                # Calculate region from the two points
                x1, y1 = coordinates[0]
                x2, y2 = coordinates[1]
                region["top"] = min(y1, y2)
                region["left"] = min(x1, x2)
                region["width"] = abs(x2 - x1)
                region["height"] = abs(y2 - y1)
                print(f"Region defined: {region}")
                region_defined.set()  # Signal that the region has been defined
                return False  # Stop listening after 2 clicks

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()


def log_inputs_to_files():
    """Continuously log key states and screenshots based on key states."""
    try:
        while True:
            # Wait until region is defined
            region_defined.wait()

            # Get the current key state folder name
            folder_name = f"test/{get_key_state_folder()}"
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
def start_keyboard_listener():
    """Start the keyboard listener."""
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    print("Please click twice on the screen to define the screenshot region.")
    threading.Thread(target=define_region, daemon=True).start()

    # Start the keyboard listener in a separate thread
    threading.Thread(target=start_keyboard_listener, daemon=True).start()

    # Start logging inputs to files
    log_inputs_to_files()
