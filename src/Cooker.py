from CookerFunctions import *
from os import makedirs, listdir
import time, json, shutil

try: settings = json.load(open("settings.json"))
except: 
    print("INFO: Settings not found! Using default ones.")
    settings = {"PLATFORM": "NX","IMAGETODDS_FLAG": True}

PLATFORM = settings["PLATFORM"]
IMAGETODDS = settings["IMAGETODDS_FLAG"]

makedirs("toCook", exist_ok=True)
makedirs(f"cooked\\{PLATFORM.lower()}", exist_ok=True)

clear()
print("UbiArt Multi-Platform Texture Cooker by Sen\n\nThis tool was last modified on: 2 April 2024 - 12:16\n")

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
    TextureCooker.Cook(input_texture=input_texture, output_texture=output_texture, platformType=PLATFORM, IMAGETODDS=IMAGETODDS)

shutil.rmtree(r"C:\Temp")