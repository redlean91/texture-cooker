import os
import shutil
from .__utils__ import *
from .__texture__ import Texture

class TextureCooker:
    def cookDDS(input_texture, output_texture, compression, mips=None, binaryPath="bin"):
        COOKER = r"{}\nvcompress.exe".format(binaryPath)
        if compression == "DXT1": _type = "-bc1"
        if compression == "DXT3": _type = "-bc2"
        if compression == "DXT5": _type = "-bc3"
        if compression == "RGBA32": _type = "-rgb"
        mipsArg = "" if mips else "-nomips"

        os.system("{} -silent {} -nocuda {} {} {}".format(COOKER, _type, input_texture, output_texture))
    
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

    def cook(input_texture, output_texture, platformType):
        makeTemp()

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

        


