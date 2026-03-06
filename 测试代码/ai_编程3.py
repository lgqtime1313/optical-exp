"""
64位DDS与SLM结合控制代码

该代码实现了使用64位DDS生成的信号来控制SLM（空间光调制器）的功能。
DDS生成的64个不同频率的信号将被转换为SLM的相位调制，
从而实现动态的光学调制效果。

使用方法：
1. 确保Spectrum板卡和SLM都已正确安装并连接
2. 运行此脚本
3. 按Enter键退出
"""

import spcm
from spcm import units
import numpy as np
import time
import sys

# 导入SLM控制模块
sys.path.append('d:\\LvgqExperiment\\slm')
from slm.slm_class import SLM

class DDS_SLM_Controller:
    def __init__(self):
        # 初始化SLM - 使用显示器0
        self.slm = SLM(monitor=0, lut=r"d:\\LvgqExperiment\\slm\\ScaledLutModel.txt")
        # getSize()返回(x_size, y_size)，即(宽度, 高度)
        self.slm_width, self.slm_height = self.slm.slm.getSize()
        print(f"SLM尺寸: {self.slm_width} x {self.slm_height}")
        
        # 初始化全息图 - 形状为(高度, 宽度)
        self.hologram = np.zeros((self.slm_height, self.slm_width))
    
    def run(self, duration=60):
        """运行控制程序
        
        参数:
            duration: 运行时间（秒）
        """
        print("启动DDS-SLM控制系统...")
        
        # 使用with语句管理DDS卡连接
        with spcm.Card(card_type=spcm.SPCM_TYPE_AO) as card:
            # 设置卡模式
            card.card_mode(spcm.SPC_REP_STD_DDS)
            
            # 配置通道
            channels = spcm.Channels(card)
            channels.enable(True)
            channels.output_load(50 * units.ohm)
            channels.amp(500 * units.mV)
            card.write_setup()  # 启动系统时钟
            
            # 初始化DDS
            dds = spcm.DDS(card, channels=channels)
            dds.reset()
            
            # 检查DDS核心数量
            num_cores = len(dds)
            print(f"DDS核心数量: {num_cores}")
            
            # 设置64位DDS的参数
            start_freq = 1 * units.MHz  # 起始频率
            freq_step = 0.5 * units.MHz  # 频率步进
            
            for i, core in enumerate(dds):
                if i >= 64:  # 只设置前64个核心
                    break
                
                # 设置频率
                frequency = start_freq + i * freq_step
                core.freq(frequency)
                
                # 设置幅度
                amplitude = 100 * units.percent / min(num_cores, 64)
                core.amp(amplitude)
                
                # 设置相位
                phase = (i * 15) % 360 * units.degrees
                core.phase(phase)
                
                print(f"DDS核心 {i}: 频率={frequency}, 幅度={amplitude}, 相位={phase}")
            
            # 执行DDS设置
            dds.exec_at_trg()
            dds.write_to_card()
            
            # 启动DDS
            card.start(spcm.M2CMD_CARD_ENABLETRIGGER, spcm.M2CMD_CARD_FORCETRIGGER)
            print("DDS启动成功!")
            
            start_time = time.time()
            try:
                while time.time() - start_time < duration:
                    # 从DDS生成全息图
                    # 注意：SLM的pad_image方法期望图像形状为(宽度, 高度, 3)
                    # 但numpy的mgrid是(y, x)顺序，所以我们需要调整
                    hologram = np.zeros((self.slm_height, self.slm_width))
                    
                    # 计算64个频率对应的空间模式
                    for i in range(min(64, num_cores)):
                        # 获取DDS核心的频率
                        core = dds[i]
                        freq = core.get_freq()
                        
                        # 计算空间频率（简化模型）
                        # 检查freq是否为浮点数
                        if isinstance(freq, float):
                            spatial_freq = freq / 1e6  # 归一化到MHz
                        else:
                            # 如果是带单位的对象
                            spatial_freq = freq.to_base_units().magnitude / 1e6  # 归一化到MHz
                        
                        # 在全息图上生成对应的空间模式
                        # mgrid返回(y, x)，对应(高度, 宽度)
                        y, x = np.mgrid[0:self.slm_height, 0:self.slm_width]
                        
                        # 创建正弦/余弦模式
                        pattern = np.sin(2 * np.pi * spatial_freq * (x / self.slm_width + y / self.slm_height))
                        
                        # 归一化到0-1范围
                        pattern = (pattern + 1) / 2
                        
                        # 叠加到全息图上
                        hologram += pattern / min(64, num_cores)
                    
                    # 确保全息图在0-1范围内
                    hologram = np.clip(hologram, 0, 1)
                    
                    # 应用全息图到SLM
                    try:
                        self.slm.apply_hologram(hologram)
                    except Exception as e:
                        print(f"应用全息图时出错: {e}")
                        # 打印相关尺寸信息
                        print(f"全息图形状: {hologram.shape}")
                        print(f"SLM宽度: {self.slm_width}, 高度: {self.slm_height}")
                        # 尝试调整全息图尺寸
                        if hologram.shape[0] != self.slm_height or hologram.shape[1] != self.slm_width:
                            print("调整全息图尺寸...")
                            # 调整到正确的尺寸
                            from skimage.transform import resize
                            hologram_resized = resize(hologram, (self.slm_height, self.slm_width))
                            self.slm.apply_hologram(hologram_resized)
                    
                    # 短暂延迟
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("用户中断程序")
            finally:
                # 清理SLM
                if hasattr(self, 'slm') and self.slm is not None:
                    self.slm.close()
                    self.slm = None  # 标记为已关闭
                print("资源清理完成")

if __name__ == "__main__":
    print("64位DDS与SLM结合控制程序")
    print("=" * 50)
    
    controller = DDS_SLM_Controller()
    
    try:
        # 运行60秒
        controller.run(duration=10)
    except Exception as e:
        print(f"发生错误: {e}")
        # 只有当SLM存在且未关闭时才关闭
        if hasattr(controller, 'slm') and controller.slm is not None:
            controller.slm.close()
            controller.slm = None
    
    print("程序结束")
