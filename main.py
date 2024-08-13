from pynput import keyboard
import tkinter as tk
import os
import datetime
from io import BytesIO
import time
from pystyle import *
from PIL import ImageDraw, ImageFont
import win32clipboard 
from PIL import Image, ImageTk, ImageFilter
import mss
from plyer import notification
def send_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Cool screenshot tool',
            timeout=4  # Duration in seconds
        )
    except Exception as e:
        print(f"Error while sending notification: {e}")



# Set the directory where screenshots will be saved
SAVE_DIRECTORY = "screenshots"

# Create the directory if it doesn't exist
os.makedirs(SAVE_DIRECTORY, exist_ok=True)

def on_press(key):
    if key == keyboard.Key.f10:
        capture_and_edit()

def capture_and_edit():
    with mss.mss() as sct:
        # Get the dimensions of the entire virtual screen
        virtual_screen = {
            'left': min(monitor['left'] for monitor in sct.monitors),
            'top': min(monitor['top'] for monitor in sct.monitors),
            'width': max(monitor['left'] + monitor['width'] for monitor in sct.monitors) - min(monitor['left'] for monitor in sct.monitors),
            'height': max(monitor['top'] + monitor['height'] for monitor in sct.monitors) - min(monitor['top'] for monitor in sct.monitors),
        }
        
        # Capture the entire virtual screen
        full_screenshot = sct.grab(virtual_screen)
        img = Image.frombytes("RGB", (full_screenshot.width, full_screenshot.height), full_screenshot.rgb)

        # Create a copy of the original image to use later
        original_img = img.copy()

        draw = ImageDraw.Draw(img)
        font_path = "arial.ttf"  # Make sure this font is available on your system
        font_size = 40  # Specify the font size
        font = ImageFont.truetype(font_path, font_size)

        # Add text to the image
        draw.text((30, 30), "Make a shape to screenshot", fill="white", font=font)
        filtered_img = img

    # Initialize Tkinter for displaying the screenshot and drawing the selection
    root = tk.Tk()
    root.geometry(f"{virtual_screen['width']}x{virtual_screen['height']}+{virtual_screen['left']}+{virtual_screen['top']}")
    root.attributes('-alpha', 1.8)  # Ensure full opacity
    root.attributes('-topmost', True)  # Ensure it stays on top
    root.overrideredirect(True)  # Remove window decorations

    # Convert filtered screenshot to ImageTk format for display
    screenshot_image = ImageTk.PhotoImage(filtered_img)

    # Canvas to display the screenshot and draw the selection rectangle
    canvas = tk.Canvas(root, width=virtual_screen['width'], height=virtual_screen['height'])
    canvas.pack()

    # Display the filtered screenshot on the canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_image)

    # Variables to track rectangle
    rect = None
    start_x, start_y = 0, 0

    def on_button_press(event):
        nonlocal start_x, start_y, rect
        # Revert to the original image to remove the text
        clear_image = original_img.copy()
        clear_screenshot = ImageTk.PhotoImage(clear_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=clear_screenshot)

        # Set the initial position for the rectangle
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

    def on_move_press(event):
        nonlocal rect
        # Update the size of the rectangle
        cur_x, cur_y = (event.x, event.y)
        canvas.coords(rect, start_x, start_y, cur_x, cur_y)

    def on_button_release(event):
        nonlocal start_x, start_y, rect
        # Capture the region inside the rectangle
        end_x, end_y = event.x, event.y
        # Ensure start coordinates are less than end coordinates
        left, top = min(start_x, end_x), min(start_y, end_y)
        right, bottom = max(start_x, end_x), max(start_y, end_y)

        # Capture the selected area from the original image
        cropped_img = original_img.crop((left, top, right, bottom))

        
        def save_and_close(cropped_img):
            the = time.time()
            root.destroy()  # Remove the window

            # Save to file
            start_time = time.time()
            # Create filename
            filename = os.path.join(SAVE_DIRECTORY, f'screenshot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png')
            try:
                cropped_img.save(filename)
                end_time = time.time()
                duration = end_time - start_time
                print(Colorate.Horizontal(Colors.green_to_blue, f'Screenshot saved as {filename} in {SAVE_DIRECTORY}, took {duration:.2f} seconds.'))
            except Exception as e:
                print(Colorate.Horizontal(Colors.red_to_yellow, f"Error while saving file: {e}"))


            
            # Save to clipboard
            def send_to_clipboard(clip_type, data):
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(clip_type, data)
                win32clipboard.CloseClipboard()

            image = Image.open(filename)

            output = BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            start_time = time.time()
            try:
                send_to_clipboard(win32clipboard.CF_DIB, data)
                end_time = time.time()
                duration = end_time - start_time
                print(Colorate.Horizontal(Colors.green_to_blue, f"Saved To Clipboard, took {duration:.2f} seconds."))
            except Exception as e:
                print(Colorate.Horizontal(Colors.red_to_yellow, f"Error while copying to clipboard: {e}"))


            the_end = time.time()
            total_duration = the_end - the
            try:
                send_notification("Screenshot saved successfully", f"Took {total_duration} seconds")
                print(Colorate.Horizontal(Colors.green_to_blue, f"Sent toast notification."))
                print("")
            except Exception as e:
                print(Colorate.Horizontal(Colors.red_to_yellow, f"Error while sending notification: {e}\n\n"))

        save_and_close(cropped_img)

    def exit1(): 
        root.destroy()
        exit()

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move_press)
    canvas.bind("<ButtonRelease-1>", on_button_release)
    ext = tk.Button(root, text="close", command=exit1)
    ext.pack()
    root.mainloop()

if __name__ == "__main__":
    print(Colorate.Horizontal(Colors.rainbow, "Welcom to cool screenshot tool, press f10 to take a screenshot"))
    # Collect events until released
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()