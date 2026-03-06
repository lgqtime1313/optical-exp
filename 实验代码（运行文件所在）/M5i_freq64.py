import spcm
import numpy as np
from spcm import *

# 1. 定义你的频率参数
NUM_FREQS = 64  # 目标频率数量
FREQ_STEP = 0.49 * units.MHz  # 频率间隔
START_FREQ = 80 * units.MHz  # 起始频率 (你可以根据需要修改，例如 80MHz)

try:
    # 连接板卡 (模拟模式)
    with spcm.Card('/dev/spcm0') as card:
        print(f"已连接板卡: {card}")

        # Setup card for DDS
        card.card_mode(spcm.SPC_REP_STD_DDS)

        # Setup Channels
        channels = spcm.Channels(card)
        channels.enable(True)
        channels.output_load(50 * units.ohm)
        channels.amp(500 * units.mV)  # 此时输出的总最大电压
        card.write_setup()

        dds = spcm.DDS(card, channels=channels)
        dds.reset()

        # -----------------------------------------------------------
        # 2. 自动生成 64 个频率的数组
        # 公式: [start, start+step, start+2*step, ...]
        # -----------------------------------------------------------
        # np.arange(数量) 会生成 0 到 63
        init_freq = START_FREQ + (np.arange(NUM_FREQS) * FREQ_STEP)

        print("=" * 50)
        print(f"计划生成频率数量: {len(init_freq)}")
        print(f"频率范围: {init_freq[0]} 到 {init_freq[-1]}")
        print(f"频率间隔: {FREQ_STEP}")
        print(f"板卡可用 DDS 核心数: {len(dds)}")
        print("=" * 50)

        # 3. 遍历并配置
        # 计算每个频率的幅度 (总幅度分散到64个点，避免过载)
        # 注意：点数越多，单点功率越小
        amp_per_tone = 45 * units.percent / len(init_freq)

        active_cores = 0

        for i, core in enumerate(dds):
            # 如果核心索引 i 超过了我们准备的频率数量 (虽然这里不太可能，因为准备了64个)
            if i >= len(init_freq):
                break

            # 设置该核心的参数
            current_freq = init_freq[i]
            core.amp(amp_per_tone)
            core.freq(current_freq)
            core.phase(0 * units.deg)  # 可选：设置相位

        #     # 打印前3个和最后3个，避免刷屏，确认数值正确
        #     if i < 3 or i >= (min(len(dds), len(init_freq)) - 3):
        #         print(f"[Core {i:02d}] 设定频率: {current_freq} | 幅度: {amp_per_tone:.4f}")
        #     elif i == 3:
        #         print("... (中间省略) ...")
        #
        #     active_cores += 1
        #
        # # 4. 检查是否所有 64 个频率都配置成功
        # if active_cores < len(init_freq):
        #     print("!" * 50)
        #     print(f"【警告】你想要输出 {len(init_freq)} 个频率，但板卡只有 {active_cores} 个 DDS 核心。")
        #     print(f"因此，只有前 {active_cores} 个频率 (从 {init_freq[0]} 到 {init_freq[active_cores - 1]}) 被激活。")
        #     print("如果必须输出 64 个频率，请检查板卡型号是否支持，或改用 AWG 波形生成模式。")
        #     print("!" * 50)
        # else:
        #     print(f"成功配置所有 {active_cores} 个频率！")

        # 写入并触发
        dds.exec_at_trg()
        dds.write_to_card()

        print("\n正在启动触发...")
        card.start(spcm.M2CMD_CARD_ENABLETRIGGER, spcm.M2CMD_CARD_FORCETRIGGER)

        input("按 Enter 键退出模拟")

except spcm.SpcmError as e:
    print(f"Spectrum 驱动错误: {e}")
except Exception as e:
    print(f"代码运行错误: {e}")