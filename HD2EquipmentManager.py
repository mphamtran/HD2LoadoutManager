import pyautogui
import pydirectinput as pdi
import time
import keyboard


def click(px, py):
    pdi.mouseDown(x=px, y=py, button='left')
    time.sleep(0.06)
    pdi.mouseUp(button='left')


# don't raise exception if an image isn't found just return None
pyautogui.useImageNotFoundException(False)

# equipment slot coordinates, stratagem / booster images
slots = [
    ((85, 875), '1.png'),
    ((185, 875), '2.png'),
    ((285, 875), '3.png'),
    ((340, 875), '4.png'),
    ((415, 875), '5.png')
]

print("Waiting for Equipment Screen (hold F8 to stop)...")

# wait to enter equipment screen (by finding ready up button)
while True:
    if keyboard.is_pressed('f8'):
        print("Stopped by user (F8).")
        exit()

    if pyautogui.locateOnScreen('readyUp.png', region=(53, 927, 420, 42), confidence=0.7):
        print("Equipping:")
        break

    time.sleep(0.2)

# loop through each slot, i counter
for i, ((x, y), image_name) in enumerate(slots):
    print(f"Equipment slot {i + 1}: {image_name.replace('.png', '')}")
    # click on equipment slot coordinates to enter equipment slot
    click(x, y)
    time.sleep(0.15)

    # hold coordinates of where the image is found if it is found
    equipmentCoords = pyautogui.locateCenterOnScreen(image_name, confidence=0.9)

    # if not found, scroll down until found
    if not equipmentCoords:
        # 7 times, scroll 700 units down
        for scrolls in range(7):
            pyautogui.scroll(-700)
            time.sleep(0.2)
            equipmentCoords = pyautogui.locateCenterOnScreen(image_name, confidence=0.9)
            if equipmentCoords:
                break

    # once found, click at stored equipment coordinates
    if equipmentCoords:
        hx, hy = equipmentCoords
        click(hx, hy)

    # press ESC for equipment slots 1–3
    if i < 3:
        pdi.press('esc')
        time.sleep(0.15)
