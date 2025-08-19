from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import time
import os
import random
import concurrent.futures
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class TextImageTask:
    image_path: str
    txt_path: str
    output_path: str
    font_path: str
    font_size: int = 87
    text_color: Tuple[int, int, int] = (255, 215, 0)
    bg_color: Tuple[int, int, int, int] = (100, 149, 237, 180)
    line_spacing: int = 29
    start_x: int = 50
    start_y: int = 150
    max_width: int = None

def add_text_to_image(task: TextImageTask) -> None:
    """
    优化版：将文字添加到图片上（单任务处理函数）
    """
    try:
        # 读取图片并直接转换为RGBA模式
        image = cv2.imread(task.image_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            print(f"无法加载图片: {task.image_path}")
            return
        
        if len(image.shape) == 2:  # 灰度图
            image_pil = Image.fromarray(image).convert('RGBA')
        elif image.shape[2] == 3:  # RGB
            image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).convert('RGBA')
        else:  # RGBA或其他
            image_pil = Image.fromarray(image)

        draw = ImageDraw.Draw(image_pil)
        
        # 预加载字体
        try:
            date_font = ImageFont.truetype(task.font_path, 60)
            main_font = ImageFont.truetype(task.font_path, task.font_size)
        except IOError:
            print(f"警告: 字体加载失败，使用默认字体: {task.font_path}")
            date_font = ImageFont.load_default()
            main_font = ImageFont.load_default()
        
        # 添加当前日期
        current_date = time.strftime('%Y-%m-%d')
        date_bbox = draw.textbbox((0, 0), current_date, font=date_font)
        date_width = date_bbox[2] - date_bbox[0] + 30
        date_height = date_bbox[3] - date_bbox[1] + 30
        
        # 绘制日期背景和文字
        draw.rounded_rectangle([(10, 10), (10 + date_width, 10 + date_height)], 
                             radius=15, fill=(255, 215, 0, 255))
        draw.text((20, 15), current_date, font=date_font, fill=(0, 0, 0))
        
        # 读取并处理文本
        try:
            with open(task.txt_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"无法读取文本文件 {task.txt_path}: {str(e)}")
            return

        if not lines:
            print(f"警告: TXT文件为空: {task.txt_path}")
            return
        
        # 设置最大宽度
        max_width = task.max_width if task.max_width is not None else image_pil.width - task.start_x * 2
        
        x, y = task.start_x, task.start_y
        char_width_cache: Dict[str, float] = {}  # 字符宽度缓存
        
        for line in lines:
            if not line:
                continue
                
            current_line = []
            current_line_width = 0
            
            for char in line:
                # 使用缓存获取字符宽度
                if char not in char_width_cache:
                    char_width = draw.textlength(char, font=main_font)
                    char_width_cache[char] = char_width
                
                char_width = char_width_cache[char]
                
                if current_line_width + char_width <= max_width:
                    current_line.append(char)
                    current_line_width += char_width
                else:
                    # 绘制当前行
                    if current_line:
                        _draw_text_line(draw, ''.join(current_line), x, y, main_font, task.text_color, task.bg_color)
                        y += _get_text_height(''.join(current_line), main_font) + task.line_spacing
                    
                    # 开始新行
                    current_line = [char]
                    current_line_width = char_width
            
            # 绘制剩余文字
            if current_line:
                _draw_text_line(draw, ''.join(current_line), x, y, main_font, task.text_color, task.bg_color)
                y += _get_text_height(''.join(current_line), main_font) + task.line_spacing
        
        # 保存结果
        try:
            if task.output_path.lower().endswith('.png'):
                image_pil.save(task.output_path, optimize=True, compress_level=6)
            else:
                image_pil.convert('RGB').save(task.output_path, quality=85)
            print(f"处理完成: {task.output_path}")
        except Exception as e:
            print(f"保存图片失败 {task.output_path}: {str(e)}")

    except Exception as e:
        print(f"处理图片 {task.image_path} 和文本 {task.txt_path} 时发生错误: {str(e)}")

def _draw_text_line(
    draw: ImageDraw.Draw,
    text: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    text_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int, int]
) -> None:
    """绘制单行文本及其背景"""
    bbox = draw.textbbox((x, y), text, font=font)
    padding = 15
    bg_box = (
        bbox[0] - padding,
        bbox[1] - padding,
        bbox[2] + padding,
        bbox[3] + padding
    )
    
    # 创建背景层
    bg_layer = Image.new('RGBA', (bg_box[2] - bg_box[0], bg_box[3] - bg_box[1]), bg_color)
    mask = Image.new('L', bg_layer.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), bg_layer.size], radius=10, fill=255)
    
    # 合成背景
    draw.bitmap((bg_box[0], bg_box[1]), bg_layer, mask=mask)
    
    # 绘制文字
    draw.text((x, y), text, font=font, fill=text_color)

def _get_text_height(text: str, font: ImageFont.FreeTypeFont) -> int:
    """获取文本高度"""
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]

def generate_text_images_multithread(max_workers: int = None) -> None:
    """
    多线程版：从subtitle中读取所有txt内容，从picture/resized中为每个txt文件随机选择背景图片，
    添加文字和日期后保存到picture/textAdded
    
    参数:
        max_workers: 线程池最大工作线程数，None则自动根据CPU核心数决定
    """
    # 设置路径
    subtitle_dir = "./text/subtitle"
    resized_dir = "./picture/resized"
    output_dir = "./picture/textAdded"
    font_path = "simhei.ttf"
    
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 获取文件列表
        txt_files = [f for f in os.listdir(subtitle_dir) if f.lower().endswith('.txt')]
        if not txt_files:
            print("错误: subtitle目录中没有找到txt文件")
            return
        
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        image_files = [f for f in os.listdir(resized_dir) 
                      if f.lower().endswith(image_extensions)]
        if not image_files:
            print("错误: resized目录中没有找到图片文件")
            return
        
        # 准备任务列表
        tasks = []
        for txt_file in txt_files:
            txt_path = os.path.join(subtitle_dir, txt_file)
            image_path = os.path.join(resized_dir, random.choice(image_files))
            output_name = os.path.splitext(txt_file)[0] + '.png'
            output_path = os.path.join(output_dir, output_name)
            
            tasks.append(TextImageTask(
                image_path=image_path,
                txt_path=txt_path,
                output_path=output_path,
                font_path=font_path
            ))
        
        # 使用线程池处理任务
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = [executor.submit(add_text_to_image, task) for task in tasks]
            
            # 等待所有任务完成并处理异常
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()  # 获取结果（如果有异常会在这里抛出）
                except Exception as e:
                    print(f"任务执行出错: {str(e)}")
        
        print("所有任务处理完成")
        
    except Exception as e:
        print(f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    # 检查目录
    subtitle_dir = "./text/subtitle"
    resized_dir = "./picture/resized"
    
    if not os.path.exists(subtitle_dir):
        os.makedirs(subtitle_dir, exist_ok=True)
        print(f"警告: 创建了subtitle目录: {subtitle_dir}")
    elif not os.path.exists(resized_dir):
        os.makedirs(resized_dir, exist_ok=True)
        print(f"警告: 创建了resized目录: {resized_dir}")
    else:
        # 获取CPU核心数作为默认线程数
        cpu_count = os.cpu_count() or 4
        # 使用CPU核心数的2倍作为线程数（I/O密集型任务）
        max_workers = min(cpu_count * 2, 32)  # 不超过32个线程
        
        print(f"使用 {max_workers} 个线程处理任务...")
        generate_text_images_multithread(max_workers=max_workers)