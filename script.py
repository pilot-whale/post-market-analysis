import subprocess
import time  # 导入time模块
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
app_path = script_dir / "ChatTTS-UI-0.84" / "app.exe"
email_path = script_dir / "read_email" / "read_email.py"
tts_path = script_dir / "ChatTTS-asker" / "localtts.py"
addText_path = script_dir / "add-text" / "addText.py"
# videoGenerate_path = script_dir / "video-processor" / "video-generator.py"
# videoConnect_path = script_dir / "video-processor" / "video-connecter.py"
video_generate_connect_path = script_dir / "video-processor" / "video-generator-connector.py"
upload_path = script_dir / "social-auto-upload" / "upload_video_to_douyin.py"

try:
    # 启动app.exe
    # app_process = subprocess.Popen(str(app_path))
    # print(f"已启动: {app_path}")

    # # 添加等待时间，确保app完全启动
    # print("等待app完全启动...")
    # time.sleep(60)  # 等待10秒，可以根据实际情况调整

    # 运行Python脚本 - 确保在 Conda 环境 chatTTS 中运行
    print(f"正在运行: {email_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(email_path)], check=True)
    print(f"正在运行: {tts_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(tts_path)], check=True)
    print(f"正在运行: {addText_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(addText_path)], check=True)
    # print(f"正在运行: {videoGenerate_path}")
    # subprocess.run(["conda", "run", "-n", "chattts", "python", str(videoGenerate_path)], check=True)    
    # print(f"正在运行: {videoConnect_path}")
    # subprocess.run(["conda", "run", "-n", "chattts", "python", str(videoConnect_path)], check=True)
    print(f"正在运行: {video_generate_connect_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(video_generate_connect_path)], check=True)
    print(f"正在运行: {upload_path}")
    subprocess.run(["conda", "run", "-n", "chattts", "python", str(upload_path)], check=True)
    
    print("Python脚本执行完毕，准备关闭app.exe...")
    
finally:
    # # 确保app.exe被关闭
    # if app_process.poll() is None:  # 检查进程是否仍在运行
    #     app_process.terminate()
    #     app_process.wait()
    #     print("app.exe已关闭")
    # else:
    #     print("app.exe已自行退出")
    
    # 关闭所有浏览器窗口
    # try:
    #     print("正在关闭所有浏览器窗口...")
    #     # 列出常见浏览器进程名
    #     browsers = ['chrome.exe', 'msedge.exe', 'firefox.exe', 'opera.exe', 'brave.exe', 'vivaldi.exe']
        
    #     for browser in browsers:
    #         # 使用taskkill命令强制关闭进程
    #         subprocess.run(["taskkill", "/F", "/IM", browser], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #         print(f"已尝试关闭: {browser}")
        
    #     print("所有浏览器窗口关闭操作已完成")
    # except Exception as e:
    #     print(f"关闭浏览器时出错: {e}")

    print("所有操作完成")

# 调用清理脚本 - 运行后
print("运行后清理文件...")
subprocess.run(["python", str(Path(__file__).parent / "cleanup.py")], check=True)