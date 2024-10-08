import os
from .__utils__ import *
from .__types__ import *
from PIL import Image
import numpy, time

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
    def r_getTextureData(self, texturepath=None):
        with open(texturepath, "rb") as byteStream:
            self.rawdata = byteStream.read()
            self.rawDataSize = byteStream.tell()
            self.memorySize = byteStream.tell()

    def cookGtx(self):
        COOKER = r"{}\TexConv2.exe".format(self.binaryPath)
        
        # Creating the temp folder
        makeTemp()
        self.tmpCook = r"C:\Temp\tmpCook.gtx"
        os.system("{} -i {} -o {}".format(COOKER, self.ddsPath, self.tmpCook))
        self.r_getTextureData(texturepath=self.tmpCook)

    def cookXtx(self):
        # Checking if theres, Executable version or Python version of XTX-Extract
        xtxPyPresence = os.path.isfile(r"{}\xtx_extract.py".format(self.binaryPath))
        if xtxPyPresence: COOKER = r"python {}\xtx_extract.py".format(self.binaryPath)
        if not xtxPyPresence: COOKER = r"{}\xtx_extract.exe".format(self.binaryPath)

        # Creating the temp folder
        makeTemp()
        self.tmpCook = r"C:\Temp\tmpCook.xtx"
        os.system("{} -o {} {}".format(COOKER, self.tmpCook, self.ddsPath))
        self.r_getTextureData(texturepath=self.tmpcook)

    def cookGtf(self):
        print(self.binaryPath)
        COOKER = r"{}\dds2gtf.exe".format(self.binaryPath)
        
        # Creating the temp folder
        makeTemp()
        self.tmpCook = r"C:\Temp\tmpCook.gtf"
        os.system("{} -o {} {}".format(COOKER, self.tmpCook, self.ddsPath))
        self.r_getTextureData(texturepath=self.tmpCook)

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
        
        COOKER = r"{}\Bundler.exe".format(self.binaryPath)

        # Creating the temp folder
        makeTemp()
        self.tmpCook = r"C:\Temp\tmpCook.png"

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
        
        self.tmpCook = r"C:\Temp\tmpCook.rdf"
        self.newTmpCook = r"C:\Temp\tmpCook.xpr"

        with open(self.tmpCook, "w") as temprdf:
            temprdf.write(rdf)

        os.system("{} {}  ".format(COOKER, self.tmpCook))

        self.tmpCook = self.newTmpCook
        del self.newTmpCook

        with open(self.tmpCook, "rb") as byteStream:
            byteStream.seek(0x2C)
            self.d_xpr_header= byteStream.read(0x34)
            byteStream.seek(2060)
            self.rawdata = byteStream.read()
            self.rawDataSize = len(self.rawdata) + 0x23
            self.memorySize = len(self.rawdata) + 0x23

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

    def writeCookedTexture(self):
        self.cookedTexture.write(self.bIO_header)
        self.cookedTexture.write(self.rawdata)


