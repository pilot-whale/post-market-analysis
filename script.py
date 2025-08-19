import subprocess
from pathlib import Path

# 调用清理脚本 - 运行前
print("运行前清理文件...")
subprocess.run(["python", str(Path(__file__).parent / "cleanup.py")], check=True)

# 激活 Conda 环境 chattts
print("正在激活 Conda 环境 chattts...")
conda_activate_cmd = ["conda", "run", "-n", "chattts", "python", "--version"] 
try:
    subprocess.run(conda_activate_cmd, check=True, shell=True)
    print("Conda 环境 chattts 激活成功")
except subprocess.CalledProcessError as e:
    print(f"激活 Conda 环境失败: {e}")
    exit(1)

# 获取当前脚本所在目录
script_dir = Path(__file__).parent

# 定义相对路径
email_path = script_dir / "read_email" / "read_email.py"
tts_path = script_dir / "ChatTTS-asker" / "localtts.py"
addText_path = script_dir / "add-text" / "addText.py"
video_generate_connect_path = script_dir / "video-processor" / "video-generator-connector.py"
upload_path = script_dir / "social-auto-upload" / "upload_video_to_douyin.py"

try:
    # 运行Python脚本 - 确保在 Conda 环境 chatTTS 中运行
    print(f"正在运行: {email_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(email_path)], check=True)
    print(f"正在运行: {tts_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(tts_path)], check=True)
    print(f"正在运行: {addText_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(addText_path)], check=True)
    print(f"正在运行: {video_generate_connect_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(video_generate_connect_path)], check=True)
    print(f"正在运行: {upload_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(upload_path)], check=True)
    
    print("Python脚本执行完毕，准备关闭app.exe...")
    
finally:
    # 调用清理脚本 - 运行后
    print("运行后清理文件...")
    subprocess.run(["python", str(Path(__file__).parent / "cleanup.py")], check=True)