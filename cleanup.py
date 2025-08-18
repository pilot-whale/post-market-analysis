import os
import shutil
import sys
from pathlib import Path

def clean_directory(path):
    """删除指定目录中的所有文件和子目录，但保留目录本身"""
    if not os.path.exists(path):
        print(f"目录 {path} 不存在")
        return
    
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f"已删除文件: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"已删除目录: {file_path}")
        except Exception as e:
            print(f"删除 {file_path} 时出错: {e}")

def main():
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent
    
    # 定义要清理的目录
    directories = [
        script_dir / "audio",
        script_dir / "text" / "subtitle",
        script_dir / "text" / "target",
        script_dir / "video",
        script_dir / "picture" / "textAdded"
    ]
    
    # 清理每个目录
    for directory in directories:
        clean_directory(str(directory))

if __name__ == "__main__":
    main()