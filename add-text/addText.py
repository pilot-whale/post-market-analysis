from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import time
import os
import random

def add_text_from_txt_to_image(image_path, txt_path, output_path, 
                              font_path="simhei.ttf",
                              font_size=37,  # 放大到原来的3倍 (24*3)
                              color=(0, 0, 0),  # 改为黑色
                              line_spacing=30,  # 行间距也相应放大3倍 (30*3)
                              start_x=50,
                              start_y=150,  # 增加上边距给更大的日期
                              max_width=None):
    """
    改进版：从TXT文件读取多行文字并添加到图片上，支持自动换行
    
    参数:
        image_path: 原始图片路径
        txt_path: 包含文字的TXT文件路径
        output_path: 输出图片路径
        font_path: 中文字体路径
        font_size: 字体大小
        color: 文字颜色
        line_spacing: 行间距
        start_x: 起始x坐标
        start_y: 起始y坐标
        max_width: 文本最大宽度(像素)，None则自动使用图片宽度减去start_x
    """
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("无法加载图片，请检查路径是否正确")
    
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    
    # 添加当前年月日（黄底黑字）
    current_date = time.strftime('%Y-%m-%d')
    try:
        date_font = ImageFont.truetype(font_path, 60)  # 放大到原来的3倍 (20*3)
    except IOError:
        date_font = ImageFont.load_default()
    
    # 计算日期文本的边界框
    date_bbox = draw.textbbox((0, 0), current_date, font=date_font)
    date_width = date_bbox[2] - date_bbox[0] + 30  # 增加30像素的边距
    date_height = date_bbox[3] - date_bbox[1] + 30  # 增加30像素的边距
    
    # 绘制黄色背景
    draw.rounded_rectangle([(10, 10), (10 + date_width, 10 + date_height)], radius=15, fill=(255, 215, 0))
    
    # 绘制黑色日期文字
    draw.text((20, 15), current_date, font=date_font, fill=(0, 0, 0))
    
    # 读取TXT文件内容
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    if not lines:
        print("警告: TXT文件为空或没有有效内容")
        return
    
    # 加载字体
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"警告: 找不到字体文件 {font_path}，尝试使用默认字体")
        font = ImageFont.load_default()
    
    # 设置最大宽度
    if max_width is None:
        max_width = image_pil.width - start_x * 2  # 默认左右各留start_x的边距
    
    x, y = start_x, start_y
    
    for line in lines:
        # 如果行内容为空则跳过
        if not line:
            continue
            
        # 自动换行处理
        words = list(line)
        current_line = []
        
        for word in words:
            # 测试添加当前字后的宽度
            test_line = ''.join(current_line + [word])
            bbox = draw.textbbox((x, y), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                # 绘制当前行
                if current_line:
                    draw.text((x, y), ''.join(current_line), font=font, fill=color)
                    bbox = draw.textbbox((x, y), ''.join(current_line), font=font)
                    y += (bbox[3] - bbox[1]) + line_spacing
                
                # 开始新行
                current_line = [word]
        
        # 绘制剩余的文字
        if current_line:
            draw.text((x, y), ''.join(current_line), font=font, fill=color)
            bbox = draw.textbbox((x, y), ''.join(current_line), font=font)
            y += (bbox[3] - bbox[1]) + line_spacing
    
    # 保存结果
    result_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, result_image)
    print(f"处理完成，结果已保存到: {output_path}")

def generate_text_image():
    """
    从subtitle中读取所有txt内容，从picture/resized中为每个txt文件随机选择背景图片，
    添加文字和日期后保存到picture/textAdded
    """
    # 设置路径
    subtitle_dir = "./text/subtitle"
    resized_dir = "./picture/resized"
    output_dir = "./picture/textAdded"
    font_path = "simhei.ttf"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取subtitle目录中的所有txt文件
    txt_files = [f for f in os.listdir(subtitle_dir) if f.lower().endswith('.txt')]
    if not txt_files:
        print("错误: subtitle目录中没有找到txt文件")
        return
    
    # 获取resized目录中的所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    image_files = [f for f in os.listdir(resized_dir) if any(f.lower().endswith(ext) for ext in image_extensions)]
    if not image_files:
        print("错误: resized目录中没有找到图片文件")
        return
    
    # 遍历所有txt文件
    for txt_file in txt_files:
        # 为当前txt文件随机选择一张图片
        image_file = random.choice(image_files)
        
        # 构建完整路径
        txt_path = os.path.join(subtitle_dir, txt_file)
        image_path = os.path.join(resized_dir, image_file)
        
        # 生成输出文件名（与txt文件名一致）
        txt_name = os.path.splitext(txt_file)[0]
        output_filename = f"{txt_name}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        # 调用函数添加文字到图片
        add_text_from_txt_to_image(
            image_path=image_path,
            txt_path=txt_path,
            output_path=output_path,
            font_path=font_path
        )

# 使用示例
if __name__ == "__main__":
    # 检查subtitle和resized目录是否存在
    subtitle_dir = "./text/subtitle"
    resized_dir = "./picture/resized"
    
    if not os.path.exists(subtitle_dir):
        os.makedirs(subtitle_dir, exist_ok=True)
        print(f"警告: subtitle目录不存在，已自动创建: {subtitle_dir}")
        print("请在该目录下添加txt文件后再运行程序")
    elif not os.path.exists(resized_dir):
        os.makedirs(resized_dir, exist_ok=True)
        print(f"警告: resized目录不存在，已自动创建: {resized_dir}")
        print("请在该目录下添加图片文件后再运行程序")
    else:
        # 运行生成函数
        generate_text_image()