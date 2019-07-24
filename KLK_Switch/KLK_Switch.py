import struct
import io
import sys
import os
import gzip

def readUInt(f):
    return struct.unpack("I", f.read(4))[0]

def readInt(f):
    return struct.unpack("i", f.read(4))[0]

def readUQInt(f):
    return struct.unpack("Q", f.read(8))[0]

def readQInt(f):
    return struct.unpack("q", f.read(8))[0]

class PKGDTableEnt():
    def __init__(self, *args, **kwargs):
        self.Type = str()
        self.UNK = int()
        self.Size = int()
        self.Offset = int()
        self.Name = str()
        return super().__init__(*args, **kwargs)

def PKGD(f):
    Blank = readInt(f)
    FileCount = readInt(f)
    TableStart = readInt(f)
    f.seek(TableStart)
    Table = []
    for X in range(0, FileCount):
        D = PKGDTableEnt()
        D.Type = f.read(4).decode()
        D.UNK = readInt(f)
        D.Size = readUInt(f)
        D.Offset = readUInt(f)
        D.Name = f.read(128).decode().rstrip("\00")
        Table.append(D)
        print(D.Offset, D.Name, D.Size)
    return Table



def ExportPKGD(T, f, out):
    print("writing")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    F = len(T)
    for M in range(0, F):
        O = T[M]
        f.seek(O.Offset)
        U = f.read(O.Size)
        w = open(out+O.Name, 'wb')
        w.write(U)
        w.close()

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    out = dir_path+"//EXT//"
    fileName = sys.argv[1]
    fileNameNoPath = fileName.split("\\")
    fileNameNoPath = fileNameNoPath[len(fileNameNoPath) - 1]
    logOnly = 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    f = open(fileName, 'rb')
    Test = readUQInt(f)
    Check = int(562951300532036)
    Comp = int(559903)
    if Test == int(562951300532036):
        T = PKGD(f)
        if not logOnly:
            ExportPKGD(T, f, out)
    elif Test == Comp:
        f.seek(0)
        Decomp = gzip.decompress(f.read())
        w = open(out+fileNameNoPath, 'wb')
        w.write(Decomp)
        w.close()
        f.close()
        f = open(out+fileNameNoPath, 'rb')
        f.seek(8)
        T = PKGD(f)
        if not logOnly:
            ExportPKGD(T, f, out)


                









main()
