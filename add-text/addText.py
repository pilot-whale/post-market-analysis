from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import time

def add_text_from_txt_to_image(image_path, txt_path, output_path, 
                              font_path="simhei.ttf",
                              font_size=24,
                              color=(255, 255, 255),
                              line_spacing=30,
                              start_x=50,
                              start_y=50,
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

# 使用示例
if __name__ == "__main__":
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
    image_path = "./picture/background.png"
    txt_path = "./text/latest.txt"
    output_path1 = "./picture/latest.png"
    output_path2 = f'./picture/picture_{timestamp}.png'
    output_path3 = "./social-auto-upload/videos/latest.png"
    
    add_text_from_txt_to_image(
        image_path=image_path,
        txt_path=txt_path,
        output_path=output_path1,
        font_path="simhei.ttf",
        font_size=30,
        color=(255, 255, 255),
        line_spacing=40,
        start_x=50,
        start_y=50,
        max_width=1700  # 设置最大宽度为600像素
    )
    
    add_text_from_txt_to_image(
        image_path=image_path,
        txt_path=txt_path,
        output_path=output_path2,
        font_path="simhei.ttf",
        font_size=30,
        color=(255, 255, 255),
        line_spacing=40,
        start_x=50,
        start_y=50,
        max_width=1700  # 设置最大宽度为600像素
    )
    
    add_text_from_txt_to_image(
        image_path=image_path,
        txt_path=txt_path,
        output_path=output_path3,
        font_path="simhei.ttf",
        font_size=30,
        color=(255, 255, 255),
        line_spacing=40,
        start_x=50,
        start_y=50,
        max_width=1700  # 设置最大宽度为600像素
    )