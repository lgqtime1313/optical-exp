import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib as mpl
mpl.rcParams['font.family'] = 'SimHei'        # 使用黑体显示中文
mpl.rcParams['axes.unicode_minus'] = False    # 正常显示负号

class OpticalTrap:
    def __init__(self, trap_pos=(0, 0, 0), trap_depth=10, beam_waist=1.0, wavelength=780e-9):
        """
        初始化光阱参数
        trap_pos: 光阱中心位置 (x, y, z)
        trap_depth: 光阱深度 (mK)
        beam_waist: 光束腰斑大小 (μm)
        wavelength: 激光波长 (m)
        """
        self.trap_pos = np.array(trap_pos)
        self.trap_depth = trap_depth
        self.beam_waist = beam_waist * 1e-6  # 转换为米
        self.wavelength = wavelength
        self.k = 2 * np.pi / wavelength  # 波数
        
    def potential(self, pos):
        """
        计算给定位置的光阱势场
        pos: 位置坐标 (x, y, z)，单位为微米
        返回: 势场强度 (mK)
        """
        pos_m = np.array(pos) * 1e-6  # 转换为米
        trap_pos_m = self.trap_pos * 1e-6  # 转换为米
        
        # 计算径向距离
        r = np.sqrt((pos_m[0] - trap_pos_m[0])**2 + (pos_m[1] - trap_pos_m[1])**2)
        
        # 高斯光束强度分布
        intensity = np.exp(-2 * r**2 / self.beam_waist**2)
        
        # 势场与强度成正比
        potential = -self.trap_depth * intensity
        
        return potential

class Atom:
    def __init__(self, pos=(0, 0, 0), velocity=(0, 0, 0), mass=1.44e-25):  # 87Rb原子质量
        """
        初始化原子参数
        pos: 原子位置 (x, y, z)，单位为微米
        velocity: 原子速度 (vx, vy, vz)，单位为微米/微秒
        mass: 原子质量 (kg)
        """
        self.pos = np.array(pos, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.mass = mass
        self.kB = 1.38e-23  # 玻尔兹曼常数
    
    def update(self, trap, dt):
        """
        更新原子位置和速度
        trap: 光阱对象
        dt: 时间步长 (微秒)
        """
        # 计算势场梯度（力）
        dx = 1e-3  # 数值微分的步长
        grad_x = (trap.potential([self.pos[0]+dx, self.pos[1], self.pos[2]]) - 
                  trap.potential([self.pos[0]-dx, self.pos[1], self.pos[2]])) / (2*dx)
        grad_y = (trap.potential([self.pos[0], self.pos[1]+dx, self.pos[2]]) - 
                  trap.potential([self.pos[0], self.pos[1]-dx, self.pos[2]])) / (2*dx)
        grad_z = (trap.potential([self.pos[0], self.pos[1], self.pos[2]+dx]) - 
                  trap.potential([self.pos[0], self.pos[1], self.pos[2]-dx])) / (2*dx)
        
        force = -np.array([grad_x, grad_y, grad_z]) * 1e-3 * self.kB  # 转换为牛顿
        
        # 计算加速度 (F = ma)
        acceleration = force / self.mass * 1e12  # 转换为微米/微秒²
        
        # 更新速度和位置
        self.velocity += acceleration * dt
        self.pos += self.velocity * dt
        
        # 添加随机热运动 (布朗运动)
        temperature = 0.1  # 温度 (mK)
        thermal_velocity = np.sqrt(3 * self.kB * temperature * 1e-3 / self.mass) * 1e6  # 微米/微秒
        thermal_noise = np.random.normal(0, thermal_velocity * np.sqrt(dt), 3)
        self.velocity += thermal_noise

def simulate_trapping():
    """
    模拟空间光俘获原子的过程
    """
    # 创建光阱
    trap = OpticalTrap(trap_pos=(0, 0, 0), trap_depth=10, beam_waist=1.0)
    
    # 创建原子
    atoms = []
    for i in range(10):
        # 在光阱周围随机分布原子
        pos = np.random.normal(0, 2, 3)  # 位置在±2μm范围内
        velocity = np.random.normal(0, 0.1, 3)  # 初始速度较小
        atoms.append(Atom(pos=pos, velocity=velocity))
    
    # 模拟参数
    total_time = 100  # 总模拟时间 (微秒)
    dt = 0.1  # 时间步长 (微秒)
    steps = int(total_time / dt)
    
    # 存储原子位置历史
    pos_history = [[] for _ in range(len(atoms))]
    
    # 模拟过程
    for step in range(steps):
        for i, atom in enumerate(atoms):
            atom.update(trap, dt)
            pos_history[i].append(atom.pos.copy())
    
    # 可视化结果
    fig = plt.figure(figsize=(12, 8))
    
    # 3D轨迹图
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.set_title('原子在光阱中的轨迹')
    ax1.set_xlabel('X (μm)')
    ax1.set_ylabel('Y (μm)')
    ax1.set_zlabel('Z (μm)')
    
    for i, history in enumerate(pos_history):
        history = np.array(history)
        ax1.plot(history[:, 0], history[:, 1], history[:, 2], label=f'原子 {i+1}')
    
    # 绘制光阱位置
    ax1.scatter(0, 0, 0, color='red', s=100, label='光阱中心')
    ax1.legend()
    
    # 2D密度图 (XY平面)
    ax2 = fig.add_subplot(122)
    ax2.set_title('原子在XY平面的密度分布')
    ax2.set_xlabel('X (μm)')
    ax2.set_ylabel('Y (μm)')
    
    # 收集所有原子的XY坐标
    xy_coords = []
    for history in pos_history:
        history = np.array(history)
        xy_coords.extend(history[:, :2])
    xy_coords = np.array(xy_coords)
    
    # 绘制密度热图
    ax2.hist2d(xy_coords[:, 0], xy_coords[:, 1], bins=50, cmap='viridis')
    
    plt.tight_layout()
    plt.show()
    
    # 计算捕获效率
    trapped_atoms = 0
    for atom in atoms:
        distance = np.sqrt(np.sum(atom.pos**2))
        if distance < 3:  # 3μm范围内视为被捕获
            trapped_atoms += 1
    
    print(f"捕获效率: {trapped_atoms}/{len(atoms)} = {trapped_atoms/len(atoms)*100:.2f}%")
    print(f"光阱参数: 深度={trap.trap_depth}mK, 腰斑={trap.beam_waist*1e6}μm")

if __name__ == "__main__":
    print("空间光俘获原子模拟")
    print("=" * 50)
    simulate_trapping()
