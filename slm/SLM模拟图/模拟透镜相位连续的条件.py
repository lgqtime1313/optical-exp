# 焦距随半径单调递增
import numpy as np
import matplotlib.pyplot as plt

num_pixelss = np.linspace(1, 100, 100)
f_maxs = []
for num_pixels in num_pixelss:
    phase_states = []
    fs = np.linspace(1, 1000, 10000)
    w = 1064e-9
    pixel_size = 15e-6
    k = (2 * np.pi) / w
    r = pixel_size * num_pixels
    for f in fs:
        phase = (k * r ** 2 / 2 / f) % (2 * np.pi)
        phase /= 2 * np.pi
        phase_state = phase * 31000
        phase_states.append(phase_state / num_pixels)
    idx = (np.abs(np.asarray(phase_states) - 1)).argmin()
    f_max = fs[idx]
    f_maxs.append(f_max)

    # plt.plot(fs,phase_states)
    # plt.xlabel('SLM lens focal length (m)')
    # plt.ylabel('phase states per pixel from centre to edge')
    # plt.axhline(1,c='k',alpha=0.5,linestyle='--')
    # idx = (np.abs(np.asarray(phase_states) - 1)).argmin()
    # f_max = fs[idx]
    # plt.axvline(f_max,c='k',alpha=0.5,linestyle='--')
    # print(f_max)
    # plt.show()
    # # 很多个图

plt.plot(num_pixelss, f_maxs)
plt.xlabel('radius of circle around centre (pixels)')
plt.ylabel('max $f$ where all neighbouring pixels outside circle are unique (m)')
plt.show()