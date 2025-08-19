from moviepy import ImageClip, AudioFileClip
import os
import glob
from concurrent.futures import ThreadPoolExecutor

def create_video_with_audio(image_path, audio_path, output_path, fps=24):
    try:
        # 使用更高效的图片加载方式
        image_clip = ImageClip(image_path, duration=None)  # 先不设置时长
        audio_clip = AudioFileClip(audio_path)
        
        # 直接设置带音频的clip
        video_clip = image_clip.with_duration(audio_clip.duration).with_fps(fps).with_audio(audio_clip)

        
        # 优化编码参数
        video_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            threads=4,  # 使用多线程
            preset='fast',  # 更快的编码预设
            ffmpeg_params=['-movflags', '+faststart']  # 网络优化
        )
        return True, output_path
    except Exception as e:
        return False, f"{image_path}: {str(e)}"

def process_media_pair(args):
    filename, image_path, audio_path, video_dir = args
    output_path = os.path.join(video_dir, f'{filename}.mp4')
    return create_video_with_audio(image_path, audio_path, output_path)

def process_all_media():
    # 路径设置
    base_dir = os.path.dirname(__file__)
    image_dir = os.path.abspath(os.path.join(base_dir, '..', 'picture', 'textAdded'))
    audio_dir = os.path.abspath(os.path.join(base_dir, '..', 'audio'))
    video_dir = os.path.abspath(os.path.join(base_dir, '..', 'video'))
    
    os.makedirs(video_dir, exist_ok=True)
    
    # 获取文件更高效的方式
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
    with ThreadPoolExecutor(max_workers=4) as executor:  # 根据CPU核心数调整
        args_list = [(f, image_map[f], audio_map[f], video_dir) for f in common_filenames]
        results = executor.map(process_media_pair, args_list)
        
        success_count = 0
        for success, result in results:
            if success:
                print(f"视频已生成: {result}")
                success_count += 1
            else:
                print(f"处理失败: {result}")
                
        print(f"\n处理完成: 成功 {success_count}/{len(common_filenames)}")

if __name__ == "__main__":
    import time
    start = time.time()
    process_all_media()
    print(f"总耗时: {time.time()-start:.2f}秒")