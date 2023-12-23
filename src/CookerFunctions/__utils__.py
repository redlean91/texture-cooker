import subprocess
from os import path, system
from PIL import Image

def convert_to(image_path, 
               output_texture, 
               binary_path="bin",  
               program="magick"):
    
    alpha = has_transparency(image_path)
    if program == "nvcompress": compression = '-bc3' if alpha else "-bc1"
    else: compression = "DXT3" if alpha else "DXT1"

    if program=="magick": 
        command = f'{binary_path}\\magick.exe convert "{image_path}" "{output_texture}"'
    else: 
        command = f"{binary_path}\\{program}.exe {compression}"
        command += f' "{image_path}" "{path.abspath(output_texture)}"'
    system(command)

def resolveChannel(image_path, binary_path="bin"):
    completed_process = subprocess.Popen(
        f'''{binary_path}\\magick.exe identify -format '%[channels]' "{image_path}"''',
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )

    stdout_output, stderr_output = completed_process.communicate()

    if completed_process.returncode == 0:
        output = stdout_output
    else:
        output = stderr_output

    output = output.replace("  3.0", "").replace("'", "")
    return output

def has_transparency(image_path):
    MagickOutput=resolveChannel(image_path=image_path)

    if "srgba" in MagickOutput:
        return True
    elif "srgb" in MagickOutput and "srgba" not in MagickOutput:
        return False
    elif "rgba" in MagickOutput:
        return True
    elif "rgb" in MagickOutput and "rgba" not in MagickOutput:
        return False
    elif "p" in MagickOutput:
        return True
    
def get_platform(platform: str):
    return {
        "nx": "nx",
        "ps4": "orbis",
        "orbis": "orbis",
        "xone": "durango",
        "durango": "durango",
        "xboxsx": "scarlett",
        "scarlett": "scarlett",
        "wii": "wii",
        "wiiu": "wiiu",
        "cafe": "wiiu",
        "ps3": "ps3",
        "x360": "x360"
    }[platform.lower()]

def clear():
    import os
    if os.name == "nt":
        os.system("cls")
    elif os.name == "posix":
        os.system("clear")

def makeTemp(folder=r"C:\Temp"):
    import os
    isPath = os.path.isdir(folder)
    if isPath:
        pass
    if not isPath:
        os.mkdir(folder)
