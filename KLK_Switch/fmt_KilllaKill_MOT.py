from inc_noesis import *


def registerNoesisTypes():
	handle = noesis.register("Kill la Kill IF Animation", ".mot")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	return 1

def noepyCheckType(data):
	if len(data) < 8:
		return 0
	bs = NoeBitStream(data)

	if bs.readInt() != int(1179471700):
		return 0

	return 1


def GetBones():
    rigFile = rapi.loadPairedFile("Kill la Kill IF", ".mdl")
    rig = NoeBitStream(rigFile)
    ID = rig.readUInt()
    ModelNameLOC = rig.readUInt()
    MATNameLOC = rig.readUInt()
    MATCount = rig.readUInt()
    BoneLOC = rig.readUInt()
    BoneCount = rig.readUInt()
    BoneList = []
    if BoneLOC:
        rig.seek(BoneLOC)
        for B in range(0, BoneCount):
            BoneName = rig.readBytes(32).decode("ASCII").rstrip("\0")
            BoneROT = NoeQuat.fromBytes(rig.readBytes(16))
            BonePOS = NoeVec3.fromBytes(rig.readBytes(12))
            BoneSCA = NoeVec3.fromBytes(rig.readBytes(12))
            BoneParent = rig.readInt()
            BoneROT = BoneROT.toMat43()
            BoneROT[3] = [BonePOS[0], BonePOS[1], BonePOS[2]]
            BoneROT.__mul__(BoneSCA)
            BoneList.append(NoeBone(B, BoneName, BoneROT, None, BoneParent))
    return BoneList

class TrackEntry():
    def __init__(self, *args, **kwargs):
        self.ROTAt = int()
        self.ROTCount = int()
        self.POSAt = int()
        self.POSCount = int()
        self.SCAAt = int()
        self.SCACount = int()
        return super().__init__(*args, **kwargs)
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    
    ctx = rapi.rpgCreateContext()
    
    BoneList = GetBones()
    bs.seek(8)
    AnimName = bs.readBytes(36).decode("ASCII").rstrip("\0")
    FrameCount = bs.readUInt()
    FrameRate = float(bs.readUInt() + 3)
    TrackCount = bs.readUInt()
    UNK = bs.readUInt()
    TrackEntList = []
    for X in range(0, TrackCount):
        T = TrackEntry()
        T.ROTAt = bs.readUInt()
        T.ROTCount = bs.readUInt()
        T.POSAt = bs.readUInt()
        T.POSCount = bs.readUInt()
        T.SCAAt = bs.readUInt()
        T.SCACount = bs.readUInt()
        TrackEntList.append(T)
    print(bs.tell())
    KFBones = []
    Anim = []
    for x in range(0, TrackCount):
        b = TrackEntList[x]
        AnimBone = NoeKeyFramedBone(x)
        ROTL = []
        ROTF = []
        POSL = []
        POSF = []
        SCAL = []
        SCAF = []
        if b.ROTCount >= int(1):
            bs.seek(b.ROTAt)
            for r in range(0, b.ROTCount):
                CurFrameIndex = bs.readUInt()
                RH = NoeQuat.fromBytes(bs.readBytes(16)).transpose()
                ROTL.append(NoeKeyFramedValue(CurFrameIndex / FrameRate, RH))
            AnimBone.setRotation(ROTL, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_NEAREST)
        if b.POSCount >= int(1):
            bs.seek(b.POSAt)
            for r in range(0, b.POSCount):
                CurFrameIndex = bs.readUInt()
                PH = NoeVec3.fromBytes(bs.readBytes(12))
                POSL.append(NoeKeyFramedValue(CurFrameIndex / FrameRate, PH))
            AnimBone.setTranslation(POSL, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_NEAREST)
        if b.SCACount >= int(1):
            bs.seek(b.SCAAt)
            for r in range(0, b.SCACount):
                CurFrameIndex = bs.readUInt()
                SH = NoeVec3.fromBytes(bs.readBytes(12))
                SCAL.append(NoeKeyFramedValue(CurFrameIndex / FrameRate, SH))
            AnimBone.setScale(SCAL, noesis.NOEKF_SCALE_VECTOR_3, noesis.NOEKF_INTERPOLATE_NEAREST)
        KFBones.append(AnimBone)
    Anim.append(NoeKeyFramedAnim(AnimName, BoneList, KFBones, FrameRate))

    mdl = NoeModel()
    mdl.setBones(BoneList)
    mdl.setAnims(Anim)
    mdlList.append(mdl)


    return 1

