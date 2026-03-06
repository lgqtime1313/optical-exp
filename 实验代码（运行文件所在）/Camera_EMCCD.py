import cv2
import numpy as np
import matplotlib.pyplot as plt


def count_green_atoms(image_path):
    # 1. 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print("错误：无法找到或读取图片")
        return

    print(f"图片读取成功！图片尺寸: {img.shape}")
    
    # 复制一份用于画图展示
    output_img = img.copy()

    # 2. 转换为 HSV 颜色空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 3. 定义绿色的 HSV 范围 (根据图片色调微调)
    # 图片中的绿色比较深且模糊，我们需要一个较宽的范围
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    # 4. 创建掩膜 (Mask)：绿色区域为白，其余为黑
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # # 5. 降噪处理 (关键步骤)
    # 1. 高斯平滑，让像素点稍微融合
    blurred = cv2.GaussianBlur(mask, (3, 3), 0)
    # 2. 重新进行二值化，过滤掉变淡的噪点
    _, mask_clean = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

    # 6. 查找轮廓
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    atom_count = 0
    min_area = 20  # 最小面积阈值，过滤掉极小的噪点， 最好是6.2
    max_area = 180 # 最大面积阈值，防止识别整个区域

    # print(f"检测到的轮廓总数 (过滤前): {len(contours)}")

    for cnt in contours:
        area = cv2.contourArea(cnt)

        # 只有面积在合理范围内的才被认为是原子
        if min_area < area < max_area:
            atom_count += 1

            # 在原图上画圈标记识别到的原子
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            radius = int(radius)
            # 画红色圆圈，线宽1
            cv2.circle(output_img, center, radius + 2, (0, 0, 255), 1)

    # 7. 显示结果
    print(f"---------------------------")
    print(f"最终识别到的原子数量: {atom_count}")
    print(f"---------------------------")

    # 使用 Matplotlib 显示对比图
    plt.figure(figsize=(12, 6))

    # # 显示原图
    # plt.subplot(1, 3, 1)
    # plt.title("Original Image")
    # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # plt.axis('off')
    #
    # 显示掩膜 (黑白图)
    # plt.subplot(1, 2, 1)
    # plt.title("Green Mask (Processed)")
    # plt.imshow(mask_clean, cmap='gray')
    # plt.axis('off')

    # 显示结果图
    # plt.subplot(1, 2, 2)
    plt.title(f"Detected: {atom_count}")
    plt.imshow(cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    plt.tight_layout()
    plt.show()

'''
使用示例 需要修改的参数HSV返回 像素阈值
'''
count_green_atoms('D:\\LvgqExperiment\\1.png')