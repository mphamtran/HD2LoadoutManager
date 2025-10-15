import pyautogui
import time
import sys
import shutil


while True:
    x, y = pyautogui.position()
    msg = f"Mouse position: X={x:4d}, Y={y:4d}"
    width = shutil.get_terminal_size().columns
    sys.stdout.write("\r" + msg.ljust(width))
    sys.stdout.flush()
    time.sleep(0.03)
