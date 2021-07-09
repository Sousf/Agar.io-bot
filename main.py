import pyautogui
import time
import numpy
from PIL import ImageGrab
from PIL import ImageOps


playbtn = (1285,553)

def pressPlay():
    pyautogui.click(playbtn)
    print("Start Playing")


def split():
    # Press space in the direction of mouse cursor
    
    pass

def img_grab():
    # Grab pixel colour on screen


    # Grab the colour of the green splitter (No longer required)
    splitter = (1720,1087, 1720+1,1087+1)
    splitter_img = ImageGrab.grab(splitter)
    grayImage = ImageOps.grayscale(splitter_img)
    splitter_colour = grayImage.getcolors()

    # Colour of the splitter is [(1, 171)]
    print(splitter_colour)


def moveMouseCursor():
    pass

# time.sleep(4)
# pressPlay()
img_grab()