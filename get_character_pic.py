# %% 导入必要的包 
import shutil
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

# %% 要生成的文本
label_dict = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '=', 11: '+', 12: '-',
              13: '×', 14: '÷'}

# 文本对应的文件夹，给每一个分类建一个文件
for value, char in label_dict.items():
    # train_images_dir = "dataset"+"/"+str(value)
    train_images_dir = Path(".") / f"dataset/{value}"
    if train_images_dir.is_dir():
        shutil.rmtree(train_images_dir)
    Path.mkdir(train_images_dir, parents=True)


#
def get_square_img(image):
    x, y, w, h = cv2.boundingRect(image)
    image = image[y:y + h, x:x + w]

    max_size = 18
    max_size_and_border = 24

    if w > max_size or h > max_size:  # 有超过宽高的情况
        if w >= h:  # 宽比高长，压缩宽
            times = max_size / w
            w = max_size
            h = int(h * times)
        else:  # 高比宽长，压缩高
            times = max_size / h
            h = max_size
            w = int(w * times)
        # 保存图片大小
        image = cv2.resize(image, (w, h))

    xw = image.shape[0]
    xh = image.shape[1]

    xwLeftNum = int((max_size_and_border - xw) / 2)
    xwRightNum = (max_size_and_border - xw) - xwLeftNum

    xhLeftNum = int((max_size_and_border - xh) / 2)
    xhRightNum = (max_size_and_border - xh) - xhLeftNum

    img_large = np.pad(image, ((xwLeftNum, xwRightNum), (xhLeftNum, xhRightNum)), 'constant', constant_values=(0, 0))

    return img_large


# %% 生成图片
def makeImage(label_dict, font_path, width=24, height=24, rotate=0):
    # 从字典中取出键值对
    for value, char in label_dict.items():
        # 创建一个黑色背景的图片，大小是24*24
        img = Image.new("RGB", (width, height), "black")
        # 创建一个画笔
        draw = ImageDraw.Draw(img)
        scale = 1.0
        # 字符扩大字号倍数
        if value in [12]:  # '-'
            scale = 1.3
        if value in [12, 14]:  # '-' '÷'
            scale = 1.2
        if value in [10, 11, 13]:  # '=' '+' '×'
            scale = 1.1
        # 加载一种字体
        font = ImageFont.truetype(font_path, int(width * scale))
        # 获取字体的宽高
        left, top, right, bottom = draw.textbbox((0, 0), char, font=font)
        font_width, font_height = right - left, bottom - top

        fleft, ftop, fright, fbottom = font.getbbox(char)
        woffset, hoffset = fright - fleft, fbottom - ftop

        # 计算字体绘制的x,y坐标，主要是让文字画在图标中心
        x = int((width - font_width) / 2)
        y = int((height - font_height - hoffset) / 2)

        # 绘制文本
        draw.text((x, y), char, fill=(255, 255, 255), font=font)
        # 设置图片倾斜角度
        if rotate != 0:
            img = img.rotate(rotate)
        img_arr = np.array(img)
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY)
        img_arr = get_square_img(img_arr)

        img = Image.fromarray(img_arr)
        # 命名文件保存，命名规则：dataset/编号/img-编号_r-选择角度_时间戳.png
        time_value = int(round(time.time() * 1000))

        # 保存图片
        img_path = Path("dataset") / f"{value}" / f"img-{value}_r-{rotate}_{time_value}.png"
        img.save(img_path)
        # time.sleep(1)


# %% 存放字体的路径
font_dir = Path(".") / "fonts"
for font_name in tqdm(font_dir.iterdir()):
    font_file = font_name.resolve()
    # 倾斜角度从-10到10度，每个角度都生成一批图片
    for k in range(-10, 10, 1):
        # 每个字符都生成图片
        makeImage(label_dict, str(font_file), rotate=k)
print("done ==================")
