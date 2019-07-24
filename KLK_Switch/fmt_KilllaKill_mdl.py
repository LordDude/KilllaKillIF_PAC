from inc_noesis import *


def registerNoesisTypes():
	handle = noesis.register("Kill la Kill IF", ".mdl")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	return 1

def noepyCheckType(data):
	if len(data) < 8:
		return 0
	bs = NoeBitStream(data)

	if bs.readInt() != int(1179468876):
		return 0

	return 1

class Material():
    def __init__(self, *args, **kwargs):
        self.Name = str()
        self.FaceStart = int()
        self.FaceSize = int()
        self.FaceCount = int()
        self.FaceType = int()
        return super().__init__(*args, **kwargs)


def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    Skin = 1
    
    ID = bs.readUInt()
    ModelNameLOC = bs.readUInt()
    MATNameLOC = bs.readUInt()
    MATCount = bs.readUInt()
    BoneLOC = bs.readUInt()
    BoneCount = bs.readUInt()
    VertBuffLOC = bs.readUInt()
    VertBuffSize = bs.readUInt()
    VertexCount = bs.readUInt()
    TotalFaceCount = bs.readUInt()
    ModelName = bs.readBytes(160).decode("ASCII").rstrip("\0")
    BoneList = []

    MatList = []
    FaceBuffers = []
    bs.seek(MATNameLOC)
    for X in range(0, MATCount):
        M = Material()
        M.Name = bs.readBytes(64).decode("ASCII").rstrip("\0")
        M.FaceStart = bs.readUInt()
        M.FaceSize = bs.readUInt()
        M.FaceCount = bs.readUInt()
        M.FaceType = bs.readUInt()
        bs.seek(96, NOESEEK_REL)
        MatList.append(M)
    for X in range(0, MATCount):
        U = MatList[X]
        bs.seek(U.FaceStart)
        FaceBuffers.append(bs.readBytes(U.FaceSize))

    if BoneLOC:
        bs.seek(BoneLOC)
        for B in range(0, BoneCount):
            BoneName = bs.readBytes(32).decode("ASCII").rstrip("\0")
            BoneROT = NoeQuat.fromBytes(bs.readBytes(16))
            BonePOS = NoeVec3.fromBytes(bs.readBytes(12))
            BoneSCA = NoeVec3.fromBytes(bs.readBytes(12))
            BoneParent = bs.readInt()
            BoneROT = BoneROT.toMat43()
            BoneROT[3] = [BonePOS[0], BonePOS[1], BonePOS[2]]
            BoneROT.__mul__(BoneSCA)
            BoneList.append(NoeBone(B, BoneName, BoneROT, None, BoneParent))

    bs.seek(VertBuffLOC)
    VertexBuff = bs.readBytes(VertBuffSize)
    rapi.rpgBindPositionBufferOfs(VertexBuff, noesis.RPGEODATA_FLOAT, 48, 0)
    rapi.rpgBindNormalBufferOfs(VertexBuff, noesis.RPGEODATA_HALFFLOAT, 48, 16)
    rapi.rpgBindUV1BufferOfs(VertexBuff, noesis.RPGEODATA_HALFFLOAT, 48, 24)
    rapi.rpgBindColorBufferOfs(VertexBuff, noesis.RPGEODATA_UBYTE, 48, 12, 4)
    if len(BoneList) >= 1:
        if Skin:
            rapi.rpgBindBoneIndexBufferOfs(VertexBuff, noesis.RPGEODATA_USHORT, 48, 36, 4)
            rapi.rpgBindBoneWeightBufferOfs(VertexBuff, noesis.RPGEODATA_UBYTE, 48, 44, 4)
    for t in range(0, len(MatList)):
        q = MatList[t]
        rapi.rpgSetMaterial(q.Name)
        rapi.rpgSetName(q.Name)
        rapi.rpgCommitTriangles(FaceBuffers[t], noesis.RPGEODATA_UINT, q.FaceCount, noesis.RPGEO_TRIANGLE, 1)

    mdl = rapi.rpgConstructModel()
    if len(BoneList) >= 1:
        mdl.setBones(BoneList)
    mdlList.append(mdl)


    return 1
