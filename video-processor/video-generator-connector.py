from moviepy import ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips
import os
import glob
import re
from concurrent.futures import ThreadPoolExecutor

# 优化：定义全局常量
FPS = 24
MAX_WORKERS = 4  # 根据CPU核心数调整

def create_video_clip(image_path, audio_path, fps=FPS):
    """
    创建视频片段但不立即保存
    返回视频剪辑对象
    """
    try:
        image_clip = ImageClip(image_path, duration=None)
        audio_clip = AudioFileClip(audio_path)
        video_clip = image_clip.with_duration(audio_clip.duration).with_fps(fps).with_audio(audio_clip)
        return True, video_clip
    except Exception as e:
        return False, f"{image_path}: {str(e)}"

def process_media_pair(args):
    filename, image_path, audio_path = args
    return filename, create_video_clip(image_path, audio_path)

def natural_sort_key(s):
    """自然排序函数"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def process_and_connect_media():
    """
    处理所有媒体文件并连接成一个视频
    直接在内存中处理，避免中间文件存储
    """
    # 路径设置
    base_dir = os.path.dirname(__file__)
    image_dir = os.path.abspath(os.path.join(base_dir, '..', 'picture', 'textAdded'))
    audio_dir = os.path.abspath(os.path.join(base_dir, '..', 'audio'))
    video_dir = os.path.abspath(os.path.join(base_dir, '..', 'video'))
    video_remote_dir = os.path.abspath(os.path.join(base_dir, '..', 'social-auto-upload/videos'))

    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(video_remote_dir, exist_ok=True)

    # 获取文件
    image_files = glob.glob(os.path.join(image_dir, '*.*'))
    audio_files = glob.glob(os.path.join(audio_dir, '*.*'))

    # 创建映射时转换为小写以确保跨平台兼容性
    image_map = {os.path.splitext(os.path.basename(f).lower())[0]: f for f in image_files 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))}
    audio_map = {os.path.splitext(os.path.basename(f).lower())[0]: f for f in audio_files 
                 if f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a'))}

    common_filenames = set(image_map.keys()) & set(audio_map.keys())

    if not common_filenames:
        print("没有找到匹配的图片和音频文件")
        return

    # 使用线程池并行处理
    print(f"开始处理 {len(common_filenames)} 个媒体对...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        args_list = [(f, image_map[f], audio_map[f]) for f in common_filenames]
        results = executor.map(process_media_pair, args_list)

        # 收集成功的视频剪辑
        clips = []
        filenames = []
        success_count = 0

        for filename, (success, result) in results:
            if success:
                clips.append(result)
                filenames.append(filename)
                success_count += 1
                print(f"已生成视频片段: {filename}")
            else:
                print(f"处理失败: {result}")

    print(f"\n处理完成: 成功 {success_count}/{len(common_filenames)}")

    # 按照文件名自然排序视频片段
    if clips:
        # 结合文件名和剪辑，排序后再分离
        paired_clips = list(zip(filenames, clips))
        paired_clips.sort(key=lambda x: natural_sort_key(x[0]))
        sorted_clips = [clip for _, clip in paired_clips]

        # 拼接视频
        print("开始拼接视频...")
        final_clip = concatenate_videoclips(sorted_clips)

        # 保存拼接后的视频
        output_file_local = os.path.join(video_dir, 'latest.mp4')
        output_file_remote = os.path.join(video_remote_dir, 'latest.mp4')

        try:
            # 优化编码参数
            final_clip.write_videofile(
                output_file_local,
                codec='libx264',
                audio_codec='aac',
                threads=MAX_WORKERS,
                preset='fast',
                ffmpeg_params=['-movflags', '+faststart']
            )
            print(f"视频已成功拼接并保存为: {output_file_local}")

            # 保存到远程目录
            final_clip.write_videofile(
                output_file_remote,
                codec='libx264',
                audio_codec='aac',
                threads=MAX_WORKERS,
                preset='fast',
                ffmpeg_params=['-movflags', '+faststart']
            )
            print(f"视频已成功拼接并保存为: {output_file_remote}")
        finally:
            # 关闭所有视频剪辑
            for clip in clips:
                clip.close()
            final_clip.close()
    else:
        print("没有成功生成任何视频片段，无法拼接")


if __name__ == "__main__":
    import time
    start = time.time()
    process_and_connect_media()
    print(f"总耗时: {time.time()-start:.2f}秒")