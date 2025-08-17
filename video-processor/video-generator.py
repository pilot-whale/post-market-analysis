from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import os
import time
import glob

def create_video_with_audio(image_path, audio_path, output_path, fps=24):
    # 加载背景图片和音频文件
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    
    # 设置视频时长与音频相同
    video_clip = image_clip.with_duration(audio_clip.duration)
    
    # 设置视频帧率
    video_clip = video_clip.with_fps(fps)
    
    # 添加音频到视频
    video_clip = video_clip.with_audio(audio_clip)
    
    # 输出视频文件，使用H.264编码确保兼容性
    video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

def process_all_media():
    # 定义目录路径
    image_dir = os.path.join(os.path.dirname(__file__), '..', 'picture', 'textAdded')
    audio_dir = os.path.join(os.path.dirname(__file__), '..', 'audio')
    video_dir = os.path.join(os.path.dirname(__file__), '..', 'video')
    
    # 确保输出目录存在
    os.makedirs(video_dir, exist_ok=True)
    
    # 获取所有图片和音频文件
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(image_dir, ext)))
    
    audio_extensions = ['*.mp3', '*.wav', '*.ogg', '*.m4a']
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(audio_dir, ext)))
    
    # 创建文件名到文件路径的映射
    image_map = {os.path.splitext(os.path.basename(f))[0]: f for f in image_files}
    audio_map = {os.path.splitext(os.path.basename(f))[0]: f for f in audio_files}
    
    # 找到匹配的文件对
    common_filenames = set(image_map.keys()) & set(audio_map.keys())
    
    if not common_filenames:
        print("没有找到匹配的图片和音频文件")
        return
    
    # 处理每对匹配的文件
    for filename in common_filenames:
        image_path = image_map[filename]
        audio_path = audio_map[filename]
        output_path = os.path.join(video_dir, f'{filename}.mp4')
        
        try:
            create_video_with_audio(image_path, audio_path, output_path)
            print(f"视频已成功生成：{output_path}")
        except Exception as e:
            print(f"处理文件 {filename} 时出错：{e}")

if __name__ == "__main__":
    process_all_media()