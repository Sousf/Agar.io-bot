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
    # RGB Colour of the splitter is (51, 255, 51)

    # the box for grab() is set to None to capture the entire monitor screen as an image.
    screenImage = ImageGrab.grab(None)
    print(screenImage)
     # Grab the colour of the green splitter (No longer required)
    splitter_colour = screenImage.getpixel((1720,1087))
    print(splitter_colour)





def moveMouseCursor():
    pass

# time.sleep(4)
# pressPlay()
img_grab()