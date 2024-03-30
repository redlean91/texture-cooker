import struct

def uint32(value):
    return struct.pack(">I", value)

def int32(value):
    return struct.pack(">i", value)

def ushort(value):
    return struct.pack(">H", value)

def short(value):
    return struct.pack(">h", value)

def ubyte(value):
    return struct.pack(">B", value)

def byte(value):
    return struct.pack(">b", value)

def String8(value: str, _len = True):
    if _len: return uint32(len(value)) + value.encode("utf-8")
    else: return value.encode("utf-8")