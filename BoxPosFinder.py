import pyautogui


img = 'EmptySlot.png'
box = pyautogui.locateOnScreen(img, confidence=0.7, grayscale=True)
print(box)