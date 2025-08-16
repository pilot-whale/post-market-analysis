from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip  # 修正音频文件导入路径
import os
import time

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

if __name__ == "__main__":
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')  # 新格式：年-月-日_时-分-秒
    # 使用指定的背景图片和音频文件
    BACKGROUND_IMAGE = "latest.png"
    AUDIO_FILE = "latest.wav"
    OUTPUT_VIDEO1 = "latest.mp4"
    OUTPUT_VIDEO2 = f'video_{timestamp}.mp4'

    image_dir = r'./picture'
    audio_dir = r'./audio'
    video_dir = r'./video'
    post_video_dir = r'./social-auto-upload/videos'
    
    # 构建完整路径
    image_path = os.path.join(image_dir, BACKGROUND_IMAGE)
    audio_path = os.path.join(audio_dir, AUDIO_FILE)
    output_path1 = os.path.join(video_dir, OUTPUT_VIDEO1)
    output_path2 = os.path.join(video_dir, OUTPUT_VIDEO2)
    output_path3 = os.path.join(post_video_dir, OUTPUT_VIDEO1)
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误：背景图片文件 '{image_path}' 不存在")
    elif not os.path.exists(audio_path):
        print(f"错误：音频文件 '{audio_path}' 不存在")
    else:
        # 创建视频
        create_video_with_audio(image_path, audio_path, output_path1)
        print(f"视频已成功生成：{output_path1}")
        create_video_with_audio(image_path, audio_path, output_path2)
        print(f"视频已成功生成：{output_path2}")
        create_video_with_audio(image_path, audio_path, output_path3)
        print(f"视频已成功生成：{output_path3}")