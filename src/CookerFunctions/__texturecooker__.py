from email.mime import image
import os
import shutil
from .__utils__ import *
from .__texture__ import Texture

class TextureCooker:
    def resolveCompressionNvidia(ImageMagick_Compression):
        return {
            "rgb": "-bc1",
            "srgb": "-bc1",
            "rgba": "-bc2",
            "srgba": "-bc3",
            "l": "-bc3",
            "1": "-bc1",
            "graya": "-bc2"
        }[ImageMagick_Compression]
    
    def resolveCompression(ImageMagick_Compression):
        return {
            "rgb": "DXT1",
            "srgb": "DXT1",
            "rgba": "DXT3",
            "srgba": "DXT3",
            "l": "DXT5",
            "1": "DXT1",
            "graya": "DXT3"
        }[ImageMagick_Compression]

    def __cookDDS(image_path,
                  output_texture):
        
        channel = resolveChannel(image_path=image_path)
        compression = TextureCooker.resolveCompressionNvidia(channel)
        convert_to(image_path=image_path, output_texture=r"C:\Temp\temp.png")
        TextureCooker.cookDDS(input_texture=r"C:\Temp\temp.png", output_texture=output_texture, compression=compression)

    def cookDDS(input_texture, output_texture, compression, mips=None, binaryPath="bin"):
        COOKER = r"{}\nvcompress.exe".format(binaryPath)
        mipsArg = "" if mips else "-nomips"

        os.system("{} {} -nocuda {} {} {}".format(COOKER, compression, mipsArg, input_texture, output_texture))
    
    def cookPC(input_texture, output_texture):
        _Texture = Texture(input_texture, output_texture, "PC")
        _Texture.getTextureData()
        _Texture.cookDDS()
        _Texture.serializeHeader()
        _Texture.writeCookedTexture()
        del _Texture

    def cookNX(input_texture, output_texture):
        _Texture = Texture(input_texture, output_texture, "NX")
        _Texture.getTextureData()
        _Texture.cookXtx()
        _Texture.serializeHeader()
        _Texture.writeCookedTexture()
        del _Texture

    def cookWiiu(input_texture, output_texture):
        _Texture = Texture(input_texture, output_texture, "WIIU")
        _Texture.getTextureData()
        _Texture.cookGtx()
        _Texture.serializeHeader()
        _Texture.writeCookedTexture()
        del _Texture

    # def cookWii(): "stil needs to do"

    def Cook(input_texture, output_texture, platformType, IMAGETODDS=False):
        makeTemp()        
        if IMAGETODDS:
            TextureCooker.__cookDDS(image_path=input_texture, output_texture=r"C:\Temp\temp.dds")
            input_texture = r"C:\Temp\temp.dds"

        with open(input_texture, "rb") as ddsFile:
            if ddsFile.read(4) != b"DDS ":
                raise Exception("{} is not a DDS file!".format(input_texture))
            else:
                ddsFile.seek(0x54, os.SEEK_SET)
                compression = ddsFile.read(4)
                if compression == b'\0\0\0\0': compression = "RGBA32"

        if platformType == "PC":
            TextureCooker.cookPC(input_texture, output_texture)
        
        if platformType == "NX":
            TextureCooker.cookNX(input_texture, output_texture)

        if platformType == "WIIU":
            TextureCooker.cookWiiu(input_texture, output_texture)

        


