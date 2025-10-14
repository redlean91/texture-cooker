from CookerFunctions import *
from os import makedirs, listdir
import time, json, shutil

try: settings = json.load(open("settings.json"))
except: 
    print("INFO: Settings not found! Using default ones.")
    settings = {"PLATFORM": "NX"}

PLATFORM = settings["PLATFORM"]

makedirs("toCook", exist_ok=True)
makedirs(os.path.join("cooked", PLATFORM.lower()), exist_ok=True)

clear()
print("UbiArt Multi-Platform Texture Cooker by Sen\n\nThis tool was last modified on: 11 October 2025 - 21:52\n")

for texture in listdir("toCook"):
    print(f"Current Texture: {texture}")
    input_texture = os.path.join("toCook", texture)
    if not texture.endswith(".dds"):
        IMAGETODDS = True
        if os.path.isfile(os.path.join("bin", "magick.exe")) == False:
            print("Magick.exe is missing! Can't convert Image to DDS not supported!\nClosing in 5 seconds.")
            time.sleep(5)
            exit()
    else: IMAGETODDS = False
    if has_transparency(input_texture): output_texture = os.path.join("cooked", PLATFORM.lower(), texture.split(".")[0]+".png.ckd")
    else: output_texture = os.path.join("cooked", PLATFORM.lower(), texture.split(".")[0]+".tga.ckd")
    TextureCooker.Cook(input_texture=input_texture, output_texture=output_texture, platformType=PLATFORM, IMAGETODDS=IMAGETODDS)

shutil.rmtree(r"temp")
