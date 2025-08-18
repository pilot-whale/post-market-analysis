import os
import sys
import re  # 添加正则表达式模块导入
from moviepy import VideoFileClip, concatenate_videoclips
from tqdm import tqdm

# 设置视频目录路径
video_local_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'video')
video_remote_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'social-auto-upload/videos')
output_file_local = os.path.join(video_local_dir, 'latest.mp4')
output_file_remote = os.path.join(video_remote_dir, 'latest.mp4')

# 获取视频目录中的所有mp4文件
video_files = [f for f in os.listdir(video_local_dir) if f.endswith('.mp4')]

# 定义自然排序函数
def natural_sort_key(s):
    # 提取字符串中的数字部分，并转换为整数进行排序
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# 使用自然排序而不是默认字符串排序
video_files.sort(key=natural_sort_key)

# 检查是否有视频文件
if not video_files:
    print("错误: 未在视频目录中找到MP4文件")
    sys.exit(1)

# 加载所有视频剪辑
clips = []
for video_file in video_files:
    video_path = os.path.join(video_local_dir, video_file)
    try:
        clip = VideoFileClip(video_path)
        clips.append(clip)
        print(f"已加载: {video_file}")
    except Exception as e:
        print(f"加载视频失败 {video_file}: {e}")

# 检查是否成功加载了视频
if not clips:
    print("错误: 没有成功加载任何视频文件")
    exit(1)

# 拼接视频
final_clip = concatenate_videoclips(clips)

# 保存拼接后的视频
try:
    final_clip.write_videofile(output_file_local, codec='libx264', audio_codec='aac')
    print(f"视频已成功拼接并保存为: {output_file_local}")
    # 复制到远程目录
    final_clip.write_videofile(output_file_remote, codec='libx264', audio_codec='aac')
    print(f"视频已成功拼接并保存为: {output_file_remote}")
finally:
    # 关闭所有视频剪辑
    for clip in clips:
        clip.close()
    final_clip.close()