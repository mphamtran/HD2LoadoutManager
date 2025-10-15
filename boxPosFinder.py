import pyautogui


img = 'readyUp.png'
box = pyautogui.locateOnScreen(img, confidence=0.7, grayscale=True)
print(box)