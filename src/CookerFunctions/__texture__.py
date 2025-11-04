import os
from .__utils__ import *
from .__types__ import *
from PIL import Image
import numpy, time
import shutil

# This is a revival of planedec50's code, kind of like my version

class Texture:
    def __init__(self, ddsImage, cookedOut, platform="nx", binPath="bin"):
        self.version = 9
        self.signature = 1413830656
        self.rawDataOffset = 0x2C
        self.rawDataSize = 0
        self.width = 0
        self.height = 0
        self.depth = 1
        self.bpp = 32
        self.type = 0
        self.memorySize = 0
        self.uncompressedSize = 0
        self.nbOpaquePixels = 0
        self.nbHolePixels = 0
        self.wrapModeX = 2
        self.wrapModeY = 2
        self.dummybyte = 0
        self.dummybyte2 = 0
        self.rawdata = None
        self.ddsPath = ddsImage
        self.bIO_header = b''
        self.cookedTexture = open(cookedOut, "wb")
        self.platformType = platform
        self.tmpCook = None
        self.binaryPath = binPath

    def getTextureData(self):
        ENUM_bpp_mode = {
            "1": 1,
            "L": 8,
            "P": 8,
            "RGB": 24,
            "RGBA": 32,
            "CMYK": 32,
            "YCbCr": 24,
            "I": 32,
            "F": 32
        }
        PILLOW_DDS = Image.open(self.ddsPath)
        
        self.width = PILLOW_DDS.width
        self.height = PILLOW_DDS.height
        self.PILLOW_MODE = PILLOW_DDS.mode
        self.bpp = ENUM_bpp_mode[self.PILLOW_MODE]

        NUMPY_DDS = numpy.array(PILLOW_DDS)
        for x in range(len(NUMPY_DDS)):
            # X Axis position of current pixel
            for y in range(len(NUMPY_DDS[x])):
                # Y Axis of the current X Axis row
                if NUMPY_DDS[x][y][3] == 0:
                    self.nbHolePixels += 1
                elif NUMPY_DDS[x][y][3] == 255:
                    self.nbOpaquePixels += 1

    # Platform Texture Cookers
    def r_getTextureData(self, texturepath=None, sizeModifier=0):
        with open(texturepath, "rb") as byteStream:
            self.rawdata = byteStream.read()
            self.rawDataSize = byteStream.tell() + sizeModifier
            self.memorySize = byteStream.tell() + sizeModifier

    def r_xpr_getTextureData(self, texturepath=None):
        with open(texturepath, "rb") as byteStream:
            byteStream.seek(0x2C)
            self.d_xpr_header= byteStream.read(0x34)
            byteStream.seek(2060)
            self.rawdata = byteStream.read()
            self.rawDataSize = len(self.rawdata) + 0x23
            self.memorySize = len(self.rawdata) + 0x23

    def cookDDS(self):
        # Creating the temp folder
        makeTemp()
        self.tmpCook = os.path.join("temp", "tmpCook.dds")
        shutil.copy2(self.ddsPath, self.tmpCook)
        self.r_getTextureData(texturepath=self.tmpCook)

    def cookGtx(self):
        COOKER = r"python " + os.path.join(self.binaryPath, "gtx_extract.py")
        
        # Creating the temp folder
        makeTemp()
        self.tmpCook = os.path.join("temp", "tmpCook.gtx")
        os.system("{} -o {} -swizzle 0 {}".format(COOKER, self.tmpCook, self.ddsPath))
        self.r_getTextureData(texturepath=self.tmpCook)

    def cookXtx(self):
        # Checking if theres, Executable version or Python version of XTX-Extract
        xtxPyPresence = os.path.isfile(os.path.join(self.binaryPath, "xtx_extract.py"))
        if xtxPyPresence: COOKER = r"python " + os.path.join(self.binaryPath, "xtx_extract.py")
        if not xtxPyPresence: COOKER = os.path.join(self.binaryPath, "xtx_extract.exe")

        # Creating the temp folder
        makeTemp()
        self.tmpCook = os.path.join("temp", "tmpCook.xtx")
        os.system("{} -o {} {}".format(COOKER, self.tmpCook, self.ddsPath))
        self.r_getTextureData(texturepath=self.tmpCook)

    def cookGtf(self):
        COOKER = os.path.join(self.binaryPath, "dds2gtf.exe")
        
        # Creating the temp folder
        makeTemp()
        self.tmpCook = os.path.join("temp", "tmpCook.gtf")
        os.system("{} -o {} {}".format(COOKER, self.tmpCook, self.ddsPath))
        self.r_getTextureData(texturepath=self.tmpCook)

    def cookTex(self):
        def make_wii_textures(img, outputImg, outputImgMask=None, alpha=True):
            _img = Image.open(img)
            # Creating the alpha & mask source textures
            alpha_texture = _img.convert("RGB").convert("RGBA")

            if alpha: 
                mask_texture = _img.tobytes("raw", "A")
                mask_texture = Image.frombytes("L", _img.size, mask_texture)
                mask_texture = mask_texture.convert("RGBA")

            alpha_texture.save(outputImg)
            if alpha:
                mask_texture.save(outputImgMask)

        COOKER = os.path.join(self.binaryPath, "wimgt.exe")

        # Creating the temp folder
        makeTemp()

        if has_transparency(image_path=self.ddsPath): _alpha = True
        else: _alpha = False

        self.tmpCook = os.path.join("temp", "tmpCook.png")
        if _alpha: self.tmpCookMask = os.path.join("temp", "tmpCookMask.png")
        
        if _alpha: make_wii_textures(img=self.ddsPath, outputImg=self.tmpCook, outputImgMask=self.tmpCookMask, alpha=_alpha)

        self.newTmpCook = os.path.join("temp", "tmpCook.tpl")
        if _alpha: self.newTmpCookMask = os.path.join("temp", "tmpCookMask.tpl")

        os.system(f"{COOKER} COPY {self.tmpCook} --transform tpl.cmpr --overwrite --dest {self.newTmpCook}")
        if _alpha: os.system(f"{COOKER} COPY {self.tmpCookMask} --transform tpl.cmpr --overwrite --dest {self.newTmpCookMask}")

        if _alpha:
            with open(os.path.join("temp", "tmpCook_new.tex"), "wb") as combined:
                img_a = open(os.path.join("temp", "tmpCook.tpl"), "rb")
                img_m = open(os.path.join("temp", "tmpCookMask.tpl"), "rb")
                img_a.seek(0x40)
                img_m.seek(0x40)
                combined.write(img_a.read() + img_m.read())
                img_a.close()
                img_m.close()

        else:
            with open(os.path.join("temp", "tmpCook_new.tex"), "wb") as newTex:
                img_a = open(os.path.join("temp", "tmpCook.tpl"), "rb")
                img_a.seek(0x40)
                newTex.write(img_a.read())
                img_a.close()

        self.tmpCook = os.path.join("temp", "tmpCook_new.tex")

        self.r_getTextureData(texturepath=self.tmpCook, sizeModifier=+0x80)

        if _alpha: self.d_ssd_header = b" SSD\x00\x00\x00\x7C\x00\x00\x10\x0F" + uint32(self.height) + uint32(self.width) + b"\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00TTVN\x00\x02\x00\x07\x00\x00\x00\x20\x00\x00\x00\x41APMC\x00\x00\x00\x20\x00\xFF\x00\x00\x00\x00\xFF\x00\x00\x00\x00\xFF\xFF\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        else: self.d_ssd_header = b" SSD\x00\x00\x00\x7C\x00\x00\x10\x0F" + uint32(self.height) + uint32(self.width) + b"\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00TTVN\x00\x02\x00\x07\x00\x00\x00\x20\x00\x00\x00\x411TXD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

        if _alpha: 
            del self.tmpCookMask
            del self.newTmpCookMask

        del self.newTmpCook

    def cookXpr(self):
        @staticmethod
        def r_rdfFormat(mode="RGBA"):
            return {
                "1": "D3DFMT_DXT3",
                "L": "D3DFMT_DXT3",
                "P": "D3DFMT_DXT3",
                "RGB": "D3DFMT_DXT1",
                "RGBA": "D3DFMT_DXT3",
                "CMYK": "D3DFMT_DXT1",
                "YCbCr": "D3DFMT_DXT1",
                "I": "D3DFMT_DXT5",
                "F": "D3DFMT_DXT5",
                "GRAYA": "D3DFMT_DXT3"
            }[mode]
        
        COOKER = os.path.join(self.binaryPath, "Bundler.exe")

        # Creating the temp folder
        makeTemp()
        self.tmpCook = os.path.join("temp", "tmpCook.png")

        # Converting image to png cause dds is not supported
        convert_to(image_path=self.ddsPath, output_texture=self.tmpCook)

        # Creating the RDF file
        rdf = '''<RDF Version="XPR2">
        <Texture
        Name = "StrName"
        Source="{Source}"
        Format = "{Format}"
        Width = "{Width}"
        Height = "{Height}"
        Levels = "1"
        />
        </RDF>'''.format(Source=self.tmpCook,
                        Format=r_rdfFormat(mode=self.PILLOW_MODE),
                        Width=self.width,
                        Height=self.height)
        
        self.tmpCook = os.path.join("temp", "tmpCook.rdf")
        self.newTmpCook = os.path.join("temp", "tmpCook.xpr")

        with open(self.tmpCook, "w") as temprdf:
            temprdf.write(rdf)

        os.system("{} {}  ".format(COOKER, self.tmpCook))

        self.tmpCook = self.newTmpCook
        del self.newTmpCook

        self.r_xpr_getTextureData(texturepath=self.tmpCook)

    def serializeHeader(self):
        self.bIO_header += uint32(self.version)
        self.bIO_header += uint32(self.signature)
        self.bIO_header += uint32(self.rawDataOffset)
        self.bIO_header += uint32(self.rawDataSize)
        self.bIO_header += ushort(self.width)
        self.bIO_header += ushort(self.height)
        self.bIO_header += ushort(self.depth)
        self.bIO_header += ubyte(self.bpp)
        self.bIO_header += ubyte(self.type)
        self.bIO_header += uint32(self.memorySize)        
        self.bIO_header += uint32(self.uncompressedSize)
        self.bIO_header += uint32(self.nbOpaquePixels)
        self.bIO_header += uint32(self.nbHolePixels)
        self.bIO_header += ubyte(self.wrapModeX)
        self.bIO_header += ubyte(self.wrapModeY)  
        self.bIO_header += ubyte(self.dummybyte)
        self.bIO_header += ubyte(self.dummybyte2)

        if self.platformType == "X360":
            self.bIO_header += self.d_xpr_header

        if self.platformType == "WII":
            self.bIO_header += self.d_ssd_header

    def writeCookedTexture(self):
        self.cookedTexture.write(self.bIO_header)
        self.cookedTexture.write(self.rawdata)


