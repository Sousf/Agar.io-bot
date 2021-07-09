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
    pyautogui.click('space')
    
    pass


# TODO: fix cell movement base on mouse position
def img_grab():
    # Grab pixel colour on screen
    # RGB Colour of the splitter is (51, 255, 51)

    # the box for grab() is set to None to capture the entire monitor screen as an image.
    screenImage = ImageGrab.grab(None)
    splitter_colour = (51, 255, 51)
    print(screenImage)

     # Grab the colour of the green splitter (No longer required)
    # splitter_colour = screenImage.getpixel((1720,1087))
    # print(splitter_colour)

    splitter_found = False
    for x in range(0,2560):
        for y in range(0,1440):
            if (screenImage.getpixel((x,y)) == splitter_colour):
                moveMouseCursor(x,y)
                splitter_found = True
                break
        if (splitter_found):
            # splitter_found == False
            return splitter_found




def moveMouseCursor(x,y):
    pyautogui.moveTo(x, y)

# time.sleep(4)
# pressPlay()
time.sleep(4)
pressPlay()
while True:
    # time.sleep(4)
    img_grab()
    # stop_condition = img_grab()
    # if (stop_condition):
    #     break
    
