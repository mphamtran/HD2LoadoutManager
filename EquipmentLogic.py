# equipment logic
import pyautogui
import pydirectinput as pdi
import time
import keyboard
from pathlib import Path
import numpy as np

# don't raise exception if an image isn't found just return None
pyautogui.useImageNotFoundException(False)
# empty slot icon
numberOfScrolls = 4
boosterSlot = 4


def click(px, py):
    pdi.mouseDown(x=px, y=py, button='left')
    time.sleep(0.06)
    pdi.mouseUp(button='left')


def equip(equipmentImage):
    print("Equipping...")

    # equipment slot coordinates, stratagem / booster images
    slots = [
        # equipment
        ((85, 875), equipmentImage[0]),
        ((185, 875), equipmentImage[1]),
        ((265, 875), equipmentImage[2]),
        ((350, 875), equipmentImage[3]),
        # booster
        ((430, 875), equipmentImage[4])
    ]
    # wait to enter equipment screen (by finding ready up button)
    while True:
        if keyboard.is_pressed('f8'):
            print("Stopped by user (F8).")
            exit()

        if pyautogui.locateOnScreen('ReadyUp.png', region=(53, 927, 420, 42), confidence=0.7):
            break

        time.sleep(0.2)

    emptySlot = False

    # make sure window is focused
    for i in range(3):
        click(950, 60)

    # check if the first slot is empty or not
    # original function (not enough variation since EmptySlot.png is basically just gray box)
    # if pyautogui.locateOnScreen('EmptySlot.png', region=(58, 840, 73, 73), confidence=0.06):
    #     emptySlot = True
    firstSlotImg = pyautogui.screenshot(region=(58, 840, 73, 73))
    # convert to numpy array (H, W, Color Channel)
    firstSlotImgArray = np.array(firstSlotImg)
    # find standard deviation
    stdDev = firstSlotImgArray.std()

    print("Std Dev:", stdDev)

    # Low std dev: pixels are very similar (gray box empty slot), High std dev: pixels vary a lot
    if stdDev < 10:
        emptySlot = True

    print("There is an empty slot:", emptySlot)

    # loop through each slot, i counter
    for i, ((x, y), imageName) in enumerate(slots):
        # debugging
        print(f"Equipment slot {i + 1}: {imageName.replace('.png', '')}")

        # convert to larger equipped icon, if found then its already equipped, check the next one
        equippedImage = f"equippedicons/{Path(imageName).name}"
        if pyautogui.locateCenterOnScreen(equippedImage, region=(49, 834, 435, 83), confidence=0.8):
            print(i + 1, "already equipped")
            continue

        # click first equipment slot, click booster slot, click rest of slots if replacing a full loadout
        if i == 0 or i == boosterSlot or not emptySlot:
            print(">clicking box", i + 1)
            click(x, y)
            time.sleep(0.2)

        # hold coordinates of where the image is found
        equipmentCoords = pyautogui.locateCenterOnScreen(imageName, confidence=0.9)

        # if not found, scroll down until found, otherwise scroll up until found
        if not equipmentCoords:
            # 7 times, scroll 700 units down
            for scrolls in range(numberOfScrolls):
                pyautogui.scroll(-700)
                time.sleep(0.2)
                equipmentCoords = pyautogui.locateCenterOnScreen(imageName, confidence=0.9)
                #   stop scrolling if you find it
                if equipmentCoords:
                    break
            # if you still haven't found it
            if not equipmentCoords:
                for scrolls in range(round(numberOfScrolls*1.5)):
                    pyautogui.scroll(700)
                    time.sleep(0.2)
                    equipmentCoords = pyautogui.locateCenterOnScreen(imageName, confidence=0.9)
                    if equipmentCoords:
                        break

        # once found, click at stored equipment coordinates
        if equipmentCoords:
            hx, hy = equipmentCoords
            click(hx, hy)
