from CookerFunctions import *
import time, argparse
from os import remove, path

def main(args):
    if args.imagetodds and not args.input_texture.endswith(".dds"):
        if os.path.isfile("bin\\magick.exe") == False:
            print("Magick.exe is missing! IMAGETODDS Flag not supported!\nClosing in 5 seconds.")
            time.sleep(5)
            exit()
    TextureCooker.Cook(input_texture=args.input_texture, output_texture=args.output_texture, platformType=args.platform)
    time.sleep(args.nvcompress_wait_time) # Giving NVCompress time to convert the image

    shutil.rmtree(r"C:\Temp")
    if args.imagetodds: remove("temp.png")

parser = argparse.ArgumentParser(description="Just Dance Multi-Platform Texture Cooker implementation in Python.")

parser.add_argument("--input_texture", "-i", help="Specify a input texture.")
parser.add_argument("--output_texture", "-o", help="Specify a output texture.")
parser.add_argument("--imagetodds", help="Use if the input texture is not a DDS.", action="store_true", default=True)
parser.add_argument("--platform", "-p", help="Specify a platform to cook the texture for, default is NX.", default="NX")
parser.add_argument("--nvcompress_wait_time", "-nvtime", help="Specify NVCompress Wait Time, default is 0.5.", default=0.5)

args = parser.parse_args()

main(args)