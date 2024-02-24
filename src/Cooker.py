from CookerFunctions import *
from os import makedirs, listdir
import time, json, shutil

try: settings = json.load(open("settings.json"))
except: 
    print("INFO: Settings not found! Using default ones.")
    settings = {"PLATFORM": "NX", "COOKER_WAIT_TIME": 0.5, "IMAGETODDS_FLAG": True}

PLATFORM = settings["PLATFORM"]
COOKER_WAIT_TIME = settings["COOKER_WAIT_TIME"]
IMAGETODDS = settings["IMAGETODDS_FLAG"]

makedirs("toCook", exist_ok=True)
makedirs(f"cooked\\{PLATFORM.lower()}", exist_ok=True)

clear()
print("UbiArt Multi-Platform Texture Cooker by Sen\n\nCurrent Cooker Wait Time: {}\n\nThis tool was last modified on: 24 February 2024 - 12:34\n".format(str(COOKER_WAIT_TIME)))

for texture in listdir("toCook"):
    print(f"Current Texture: {texture}")
    input_texture = f"toCook\\{texture}"
    if IMAGETODDS and not texture.endswith(".dds"):
        if os.path.isfile("bin\\magick.exe") == False:
            print("Magick.exe is missing! IMAGETODDS Flag not supported!\nClosing in 5 seconds.")
            time.sleep(5)
            exit()
    if has_transparency(input_texture): output_texture = f"cooked\\{PLATFORM.lower()}\\" + texture.split(".")[0]+".png.ckd"
    else: output_texture = f"cooked\\{PLATFORM.lower()}\\" + texture.split(".")[0]+".tga.ckd"
    TextureCooker.Cook(input_texture=input_texture, output_texture=output_texture, platformType=PLATFORM, IMAGETODDS=IMAGETODDS, COOKER_WAIT_TIME=COOKER_WAIT_TIME)

shutil.rmtree(r"C:\Temp")