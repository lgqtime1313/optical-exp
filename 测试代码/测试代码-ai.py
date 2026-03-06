"""
对于任意波形生成器 卡片类型是SPCM_TYPE_AO
"""
from spcm_dir import pyspcm as spcm

# 1. 打开设备句柄 (例如第一张 PCIe 卡)
hCard = spcm.spcm_hOpen(spcm.create_string_buffer(b'/dev/spcm0'))   # Windows

if hCard is None:
    print("无法打开设备")
    exit()

# 2. 定义用于接收返回值的变量
lDrvType = spcm.int64(0)

# 3. 读取驱动类型寄存器 (SPC_GETDRVTYPE = 1220)
spcm.spcm_dwGetParam_i64(hCard, spcm.SPC_GETDRVTYPE, spcm.byref(lDrvType))

print(f"当前设备驱动类型值为: {lDrvType.value}")

# 4. 关闭设备
spcm.spcm_vClose(hCard)
