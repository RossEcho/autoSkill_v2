"""
Auto Skill Presser for Diablo IV
Copyright 2023 PeachBlack

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import pyautogui
import threading
import time
import keyboard
from PIL import Image

class AutoKeyPresser(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Auto Key Presser")
        self.geometry("350x650")

        self.key_to_press = [tk.StringVar(self) for _ in range(5)]
        self.frequency = [tk.DoubleVar(self) for _ in range(5)]
        self.hp_key = tk.StringVar(self)
        self.hp_level = tk.DoubleVar(self, value=80)
        self.threads = []
        self.entries = []

        for i in range(5):
            tk.Label(self, text=f"Key to Press {i+1}:").pack()
            entry = tk.Entry(self, textvariable=self.key_to_press[i])
            entry.pack()

            tk.Label(self, text=f"Frequency {i+1} (seconds):").pack()
            entry = tk.Entry(self, textvariable=self.frequency[i])
            entry.pack()

        tk.Label(self, text="HP Key:").pack()
        entry = tk.Entry(self, textvariable=self.hp_key)
        entry.pack()

        tk.Label(self, text="HP Bar Image Similarity:").pack()
        self.hp_scale = tk.Scale(self, from_=0, to=100, length=200, orient=tk.HORIZONTAL,
                                 variable=self.hp_level, resolution=1, sliderlength=30,
                                 troughcolor='gray', sliderrelief='raised')
        self.hp_scale.pack()

        # HP bar setup instructions
        tk.Label(self, text="To set up the HP bar region, go to your game window and:\n"
                            "Press F1 at the start of the HP bar.\n"
                            "Press F2 at the end of the HP bar.").pack()

        self.monitor_hp = tk.BooleanVar(self)
        self.hp_checkbox = tk.Checkbutton(self, text="Monitor HP", variable=self.monitor_hp)
        self.hp_checkbox.pack()

        tk.Button(self, text="Start", command=self.start).pack()
        tk.Button(self, text="Stop", command=self.stop).pack()

        self.should_press = threading.Event()

        keyboard.add_hotkey('F1', self.set_hp_bar_start)
        keyboard.add_hotkey('F2', self.set_hp_bar_end)
        keyboard.add_hotkey('F3', self.toggle_script)

        self.full_bar_reference = None
        self.gray_bar_reference = cv2.imread("gray_hp.png")
        self.reference_height, self.reference_width = self.gray_bar_reference.shape[:2]

        self.hp_bar_x1 = None
        self.hp_bar_y1 = None
        self.hp_bar_x2 = None
        self.hp_bar_y2 = None


    def toggle_script(self):
        if self.should_press.is_set():
            self.stop_pressing()
        else:
            self.start_pressing()

    def start(self):
        for entry in self.entries:
            entry.config(state='disabled')
        self.hp_checkbox.config(state='disabled')
        self.start_pressing()

        hp_monitor_thread = threading.Thread(target=self.monitor_hp_and_press_key)

        if self.monitor_hp.get():
            self.scan_full_hp_bar(20)
            hp_monitor_thread.start()

        messagebox.showinfo("Started", "Key pressing has started.")

    def start_pressing(self):
        self.should_press.set()
        for i in range(5):
            t = threading.Thread(target=self.press_key, args=(i,))
            t.start()
            self.threads.append(t)

    def press_key(self, index):
        while self.should_press.is_set():
            pyautogui.press(self.key_to_press[index].get())
            time.sleep(self.frequency[index].get())

    def monitor_hp_and_press_key(self):
        while self.should_press.is_set():
            hp_percentage = self.get_hp_percentage()
            scaled_hp_percentage = self.scale_percentage(hp_percentage)
            print(f'Current HP similarity: {scaled_hp_percentage}%')
            if scaled_hp_percentage is not None and scaled_hp_percentage < self.hp_level.get():
                pyautogui.press(self.hp_key.get())
                time.sleep(1)
            time.sleep(0.1)

    def stop(self):
        threading.Thread(target=self.stop_pressing).start()

    def stop_pressing(self):
        for entry in self.entries:
            entry.config(state='normal')
        self.hp_checkbox.config(state='normal')
        self.should_press.clear()
        for t in self.threads:
            t.join()
        self.threads = []
        messagebox.showinfo("Stopped", "Key pressing has stopped.")

    def close_window(self):
        threading.Thread(target=self.stop_pressing).start()
        self.destroy()

    def set_hp_bar_start(self):
        x, y = pyautogui.position()
        self.hp_bar_x1 = x
        self.hp_bar_y1 = y
        messagebox.showinfo("Info", f"Start point of HP bar set to: {x}, {y}")

    def set_hp_bar_end(self):
        x, y = pyautogui.position()
        if x < self.hp_bar_x1:
            self.hp_bar_x1, x = x, self.hp_bar_x1
        if y < self.hp_bar_y1:
            self.hp_bar_y1, y = y, self.hp_bar_y1
        self.hp_bar_x2 = x
        self.hp_bar_y2 = y
        messagebox.showinfo("Info", f"End point of HP bar set to: {x}, {y}")


    def scan_full_hp_bar(self, duration):
        print("Scanning for full HP bar color range...")
        end_time = time.time() + duration
        frames = []
        while time.time() < end_time:
            screenshot = pyautogui.screenshot()
            hp_bar_region = screenshot.crop((self.hp_bar_x1, self.hp_bar_y1, self.hp_bar_x2, self.hp_bar_y2))
            frames.append(np.array(hp_bar_region))
            time.sleep(1)
        self.full_bar_reference = np.median(frames, axis=0).astype(np.uint8)
        print("Full HP bar color range scan completed.")

    def get_hp_percentage(self):
        hp_bar_pixels = self.capture_hp_bar()
        result = cv2.matchTemplate(self.gray_bar_reference, hp_bar_pixels, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return max_val * 100

    def capture_hp_bar(self):
        screenshot = pyautogui.screenshot()
        hp_bar_region = screenshot.crop((self.hp_bar_x1, self.hp_bar_y1, self.hp_bar_x2, self.hp_bar_y2))
        hp_bar_region_resized = hp_bar_region.resize((self.reference_width, self.reference_height), 3)  # 3 corresponds to ANTIALIAS
        return np.array(hp_bar_region_resized)


    def scale_percentage(self, value):
        old_min, old_max = -20, 27
        new_min, new_max = 0, 100
        old_range = old_max - old_min
        new_range = new_max - new_min
        scaled_value = (((value - old_min) * new_range) / old_range) + new_min
        return scaled_value

    def run(self):
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        super().mainloop()

if __name__ == "__main__":
    app = AutoKeyPresser()
    app.run()
