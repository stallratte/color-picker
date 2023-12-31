import queue

import pyautogui
from pynput import mouse
import tkinter as tk
from threading import Thread
from queue import Queue
from ttkthemes import ThemedStyle
from tkinter import ttk
import pyperclip


class ColorPickerGUI(tk.Tk):

    def __init__(self):
        super().__init__()

        style = ThemedStyle(self)
        style.set_theme("clam")

        self.resizable(False, False)

        self.title("Color Picker")
        self.geometry("190x90")

        frame = ttk.Frame(self, padding="10")
        frame.grid(row=0, column=0)

        # Create a label to display text
        self.text_label = ttk.Label(frame, text="#")
        self.text_label.grid(row=0, column=0, padx=0, pady=10, sticky="w")

        self.entry = ttk.Entry(frame)
        self.entry.grid(row=0, column=1, padx=0, pady=10)

        self.color_label = ttk.Label(frame, width=5)
        self.color_label.grid(row=0, column=2)

        self.color_button = ttk.Button(frame, text="Pick Color", command=self.pick_color)
        self.color_button.grid(row=1, columnspan=3)

        self.mouse_listener = None
        self.queue = Queue()

        self.bind("<Destroy>", self.cleanup)

    def pick_color(self):

        self.mouse_listener = MouseListenerThread(self.queue)
        self.mouse_listener.start()
        self.after(100, self.check_queue)

        self.iconify()

    def check_queue(self):
        try:
            hex_color = self.queue.get_nowait()
            hex_color_without_hashtag = hex_color[1:]

            self.color_label.config(background=hex_color)
            self.attributes("-topmost", True)

            self.entry.delete(0, tk.END)
            self.entry.insert(0, hex_color_without_hashtag)
            pyperclip.copy(hex_color_without_hashtag)

            self.deiconify()
        except queue.Empty:
            pass

        self.after(100, self.check_queue)

    def cleanup(self, event):
        if self.mouse_listener:
            self.mouse_listener.join()  # Wait for the listener thread to finish


class MouseListenerThread(Thread):
    def __init__(self, color_queue):
        super().__init__()
        self.queue = color_queue

    def run(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        if pressed:
            # Get the pixel color at the current mouse position
            pixel_color = pyautogui.pixel(x, y)
            hex_color = rgb_to_hex(pixel_color)
            self.queue.put(hex_color)
            return False


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def main():
    gui = ColorPickerGUI()
    gui.mainloop()


if __name__ == "__main__":
    main()
