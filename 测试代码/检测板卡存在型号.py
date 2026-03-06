import spcm
from spcm_core import int32
from spcm_dir.spcm_tools import *

# 1. 打开设备句柄
# 在模拟模式下，'/dev/spcm0' 指向您在 Control Center 中创建的虚拟卡
hCard = spcm.spcm_hOpen(create_string_buffer(b'/dev/spcm0'))

if not hCard:
    print("无法打开板卡，请检查 Control Center 中是否已添加 Demo Card")
    exit()

try:
    # 2. 获取板卡信息 (即便是虚拟卡，也会返回模拟的型号信息)
    lCardType = int32(0)
    spcm.spcm_dwGetParam_i32(hCard, spcm.SPC_PCITYP, byref(lCardType))
    print(f"成功连接到板卡，型号代码: {hex(lCardType.value)}")

    # 3. 设置参数 (例如：设置采样率为 10 MHz)
    # 这里的寄存器写入操作在虚拟模式下是有效的，驱动会检查参数合法性
    spcm.spcm_dwSetParam_i64(hCard, spcm.SPC_SAMPLERATE, 10000000)

    print("参数设置完成，无硬件报错。")

finally:
    # 4. 关闭句柄
    spcm.spcm_vClose(hCard)