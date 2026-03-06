"""
64位DDS生成代码

基于Spectrum板卡的DDS功能，生成64个独立的DDS载波信号

使用方法：
1. 确保Spectrum板卡已正确安装并连接
2. 运行此脚本，将生成64个不同频率的DDS信号
3. 按Enter键退出
"""

import spcm
from spcm import units

# 打开板卡
with spcm.Card(card_type=spcm.SPCM_TYPE_AO) as card:
    # 设置卡模式为DDS模式
    card.card_mode(spcm.SPC_REP_STD_DDS)
    
    # 查看卡信息
    card_family = card.family()
    print(f"Card family: 0x{card_family:02x}xx")
    
    # 配置通道
    channels = spcm.Channels(card)
    channels.enable(True)  # 启用所有通道
    channels.output_load(50 * units.ohm)  # 设置输出负载
    channels.amp(500 * units.mV)  # 设置输出幅度
    
    # 重要：写入设置，启动卡的系统时钟信号，这是DDS工作所必需的
    card.write_setup()
    
    # 创建DDS对象
    dds = spcm.DDS(card, channels=channels)
    dds.reset()  # 重置DDS
    
    # 检查DDS核心数量
    num_cores = len(dds)
    print(f"Found {num_cores} DDS cores")
    
    # 为64个DDS核心设置参数
    start_freq = 1 * units.MHz  # 起始频率
    freq_step = 0.5 * units.MHz  # 频率步进
    
    for i, core in enumerate(dds):
        if i >= 64:  # 只设置前64个核心
            break
        
        # 设置频率：从1MHz开始，每个核心增加0.5MHz
        frequency = start_freq + i * freq_step
        core.freq(frequency)
        
        # 设置幅度：平均分配总功率
        amplitude = 100 * units.percent / min(num_cores, 64)
        core.amp(amplitude)
        
        # 设置相位：每个核心相位递增15度
        phase = (i * 15) % 360 * units.degrees
        core.phase(phase)
        
        # 读取并打印设置
        actual_freq = core.get_freq(return_unit=units.MHz)
        actual_amp = core.get_amp(return_unit=units.dBm)
        actual_phase = core.get_phase(return_unit=units.degrees)
        
        print(f"Core {i}: Frequency={actual_freq:.2f}, Amplitude={actual_amp:.2f}, Phase={actual_phase:.2f}")
    
    # 执行DDS设置
    dds.exec_at_trg()
    dds.write_to_card()
    
    # 启动卡，包括启用触发引擎
    print("\nStarting DDS...")
    card.start(spcm.M2CMD_CARD_ENABLETRIGGER, spcm.M2CMD_CARD_FORCETRIGGER)
    
    print("\n64-bit DDS started successfully!")
    print("Press Enter to stop and exit...")
    input()
    
    print("Exiting...")
