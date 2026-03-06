"""
一维阵列重排技术实现代码

基于SLM和DDS的一维光镊阵列重排系统
参考文献：演示一维阵列重排技术.pdf

功能：
1. 使用SLM生成一维光镊阵列
2. 通过DDS控制信号动态调整阵列参数
3. 实现阵列的重排、移动和变换

使用方法：
1. 确保Spectrum板卡和SLM都已正确安装并连接
2. 运行此脚本
3. 按Ctrl+C退出
"""

import spcm
from spcm import units
import numpy as np
import time
import sys

# 导入SLM控制模块
sys.path.append('d:\\LvgqExperiment\\slm')
from slm.slm_class import SLM

class ArrayRearrangementController:
    def __init__(self):
        # 初始化SLM - 使用显示器0
        self.slm = SLM(monitor=0, lut=r"d:\\LvgqExperiment\\slm\\ScaledLutModel.txt")
        # getSize()返回(x_size, y_size)，即(宽度, 高度)
        self.slm_width, self.slm_height = self.slm.slm.getSize()
        print(f"SLM尺寸: {self.slm_width} x {self.slm_height}")
        
        # 初始化全息图 - 形状为(高度, 宽度)
        self.hologram = np.zeros((self.slm_height, self.slm_width))
        
        # 阵列参数
        self.array_length = 8  # 一维阵列的长度
        self.array_spacing = 50  # 阵列元素间距（像素）
        self.array_center = (self.slm_width // 2, self.slm_height // 2)  # 阵列中心位置
        
        # DDS参数
        self.dds_frequency_base = 1.0 * units.MHz  # 基础频率
        self.dds_frequency_step = 0.5 * units.MHz  # 频率步进
    
    def setup_dds(self, card):
        """设置DDS参数"""
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
        
        # 设置DDS核心参数
        for i, core in enumerate(dds):
            if i >= self.array_length:  # 只设置与阵列长度相同数量的核心
                break
            
            # 设置频率
            frequency = self.dds_frequency_base + i * self.dds_frequency_step
            core.freq(frequency)
            
            # 设置幅度
            amplitude = 100 * units.percent / min(num_cores, self.array_length)
            core.amp(amplitude)
            
            # 设置相位
            phase = (i * 45) % 360 * units.degrees
            core.phase(phase)
            
            print(f"DDS核心 {i}: 频率={frequency}, 幅度={amplitude}, 相位={phase}")
        
        # 执行DDS设置
        dds.exec_at_trg()
        dds.write_to_card()
        
        # 启动DDS
        card.start(spcm.M2CMD_CARD_ENABLETRIGGER, spcm.M2CMD_CARD_FORCETRIGGER)
        print("DDS启动成功!")
        
        return dds, num_cores
    
    def generate_1d_array_hologram(self, positions):
        """生成一维阵列全息图
        
        参数:
            positions: 一维阵列元素的位置列表
        """
        # 创建基础全息图
        hologram = np.zeros((self.slm_height, self.slm_width))
        
        # 为每个阵列元素生成高斯光斑
        for pos in positions:
            x0, y0 = pos
            # 生成高斯光斑
            y, x = np.mgrid[0:self.slm_height, 0:self.slm_width]
            sigma = 10  # 光斑大小
            gaussian = np.exp(-((x - x0)**2 + (y - y0)**2) / (2 * sigma**2))
            hologram += gaussian
        
        # 归一化到0-1范围
        if np.max(hologram) > 0:
            hologram = hologram / np.max(hologram)
        
        return hologram
    
    def generate_linear_array(self):
        """生成线性阵列"""
        positions = []
        start_x = self.array_center[0] - (self.array_length - 1) * self.array_spacing // 2
        for i in range(self.array_length):
            x = start_x + i * self.array_spacing
            y = self.array_center[1]
            positions.append((x, y))
        return positions
    
    def generate_rearranged_array(self, pattern):
        """生成重排后的阵列
        
        参数:
            pattern: 重排模式，如 'reverse', 'shuffle', 'split'
        """
        linear_positions = self.generate_linear_array()
        
        if pattern == 'reverse':
            # 反转阵列
            return linear_positions[::-1]
        elif pattern == 'shuffle':
            # 随机打乱阵列
            np.random.shuffle(linear_positions)
            return linear_positions
        elif pattern == 'split':
            # 分成两部分
            mid = self.array_length // 2
            first_half = linear_positions[:mid]
            second_half = linear_positions[mid:]
            # 交换两部分
            return second_half + first_half
        else:
            # 默认返回线性阵列
            return linear_positions
    
    def run(self, duration=300):
        """运行控制程序
        
        参数:
            duration: 运行时间（秒）
        """
        print("启动一维阵列重排系统...")
        
        # 使用with语句管理DDS卡连接
        with spcm.Card(card_type=spcm.SPCM_TYPE_AO) as card:
            # 设置DDS
            dds, num_cores = self.setup_dds(card)
            
            start_time = time.time()
            pattern_index = 0
            patterns = ['linear', 'reverse', 'shuffle', 'split']
            
            try:
                while time.time() - start_time < duration:
                    # 每10秒切换一种重排模式
                    current_time = time.time() - start_time
                    if int(current_time) % 10 == 0:
                        pattern = patterns[pattern_index % len(patterns)]
                        print(f"\n切换到模式: {pattern}")
                        pattern_index += 1
                        
                        # 生成对应模式的阵列位置
                        if pattern == 'linear':
                            positions = self.generate_linear_array()
                        else:
                            positions = self.generate_rearranged_array(pattern)
                        
                        # 生成全息图
                        hologram = self.generate_1d_array_hologram(positions)
                        
                        # 应用全息图到SLM
                        try:
                            self.slm.apply_hologram(hologram)
                            print(f"应用{pattern}模式阵列成功")
                        except Exception as e:
                            print(f"应用全息图时出错: {e}")
                    
                    # 短暂延迟
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\n用户中断程序")
            finally:
                # 清理SLM
                if hasattr(self, 'slm') and self.slm is not None:
                    self.slm.close()
                    self.slm = None  # 标记为已关闭
                print("资源清理完成")

if __name__ == "__main__":
    print("一维阵列重排技术实现")
    print("=" * 50)
    
    controller = ArrayRearrangementController()
    
    try:
        # 运行5分钟
        controller.run(duration=300)
    except Exception as e:
        print(f"发生错误: {e}")
        # 只有当SLM存在且未关闭时才关闭
        if hasattr(controller, 'slm') and controller.slm is not None:
            controller.slm.close()
            controller.slm = None
    
    print("程序结束")
