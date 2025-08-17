import os
import sys
from PIL import Image

# 设置图片目录和输出目录
input_dir = os.path.join(os.getcwd(), 'picture')
output_dir = os.path.join(os.getcwd(), 'picture', 'resized')


def ensure_dir_exists(dir_path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f'创建目录: {dir_path}')


def resize_and_crop_image(input_path, output_path, target_size=(1920, 1080)):
    """
    调整图片大小并裁剪为指定尺寸，保持原始比例
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        target_size: 目标尺寸，默认为(1920, 1080)
    """
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 获取原始尺寸
            orig_width, orig_height = img.size
            target_width, target_height = target_size
            
            # 计算原始比例和目标比例
            orig_ratio = orig_width / orig_height
            target_ratio = target_width / target_height
            
            # 根据比例确定缩放方式
            if orig_ratio > target_ratio:
                # 原始图片更宽，按高度缩放，然后裁剪宽度
                new_height = target_height
                new_width = int(orig_width * (new_height / orig_height))
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # 计算裁剪区域
                left = (new_width - target_width) // 2
                top = 0
                right = left + target_width
                bottom = target_height
            else:
                # 原始图片更高，按宽度缩放，然后裁剪高度
                new_width = target_width
                new_height = int(orig_height * (new_width / orig_width))
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # 计算裁剪区域
                left = 0
                top = (new_height - target_height) // 2
                right = target_width
                bottom = top + target_height
            
            # 裁剪图片
            cropped_img = resized_img.crop((left, top, right, bottom))
            
            # 转换为 RGB 模式（如果不是的话）
            if cropped_img.mode != 'RGB':
                cropped_img = cropped_img.convert('RGB')
                
            # 保存为 PNG 格式
            cropped_img.save(output_path, 'PNG')
            print(f'已处理: {input_path} -> {output_path}')
            return True
    except Exception as e:
        print(f'处理失败 {input_path}: {str(e)}')
        return False


def process_all_images():
    """处理目录中的所有图片"""
    # 确保输入和输出目录存在
    ensure_dir_exists(input_dir)
    ensure_dir_exists(output_dir)
    
    # 获取输入目录中的所有文件
    files = os.listdir(input_dir)
    
    # 筛选出图片文件（根据扩展名）
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    image_files = [f for f in files if os.path.splitext(f)[1].lower() in image_extensions]
    
    if not image_files:
        print(f'在 {input_dir} 中未找到图片文件。')
        return
    
    print(f'找到 {len(image_files)} 个图片文件，开始处理...')
    
    # 处理每个图片文件
    success_count = 0
    for image_file in image_files:
        # 构建完整路径
        input_path = os.path.join(input_dir, image_file)
        
        # 获取文件名（不含扩展名）
        file_name = os.path.splitext(image_file)[0]
        
        # 构建输出路径（PNG格式）
        output_path = os.path.join(output_dir, f'{file_name}.png')
        
        # 处理图片
        if resize_and_crop_image(input_path, output_path):
            success_count += 1
    
    print(f'处理完成: 成功 {success_count}/{len(image_files)} 个图片')


if __name__ == '__main__':
    # 检查是否安装了 PIL
    try:
        import PIL
    except ImportError:
        print('错误: 未找到 PIL (Pillow) 库。请使用 pip install pillow 安装。')
        sys.exit(1)
    
    process_all_images()