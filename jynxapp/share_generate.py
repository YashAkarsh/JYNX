from PIL import Image,ImageDraw,ImageFont
import os
import pyautogui
from JYNX import settings

# path=os.path.join(settings.BASE_DIR,'/static/image','navy_blue.png')
im=Image.open('navy_blue.png')
os.chdir(os.getcwd())
print(os.listdir())
pyautogui.displayMousePosition()