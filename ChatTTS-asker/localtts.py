import os
import time
import re
import asyncio
import edge_tts
from concurrent.futures import ThreadPoolExecutor

# 全局变量设置
timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
audio_dir = r'./audio'
subtitle_dir = r'./text/subtitle'

# 确保目录存在
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(subtitle_dir, exist_ok=True)


class EdgeTTSClient:
    def __init__(self, voice="zh-CN-XiaoxiaoNeural"):
        self.voice = voice
        self.rate = "+0%"
        self.pitch = "+0Hz"

    async def generate_audio(self, text, save_path):
        """
        使用EdgeTTS生成语音并保存到文件

        参数:
            text: 要转换为语音的文本
            save_path: 保存路径

        返回:
            成功时返回保存的文件路径，失败时返回None
        """
        try:
            # 创建TTS对象
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)

            # 生成并保存音频
            await communicate.save(save_path)
            return save_path
        except Exception as e:
            print(f"生成音频失败: {e}")
            return None


async def process_paragraph(tts_client, paragraph, i):
    """处理单个段落的函数"""
    if not paragraph.strip():
        return

    print(f'正在处理第 {i+1} 个段落...')
    print(f'段落内容: {paragraph}')

    # 保存字幕
    subtitle_filename = f"{i+1}.txt"
    subtitle_save_path = os.path.join(subtitle_dir, subtitle_filename)
    with open(subtitle_save_path, 'w', encoding='utf-8') as f:
        f.write(paragraph)
    print(f"第 {i+1} 个段落字幕已保存到: {subtitle_save_path}")

    # 生成音频
    paragraph_audio_filename = f"{i+1}.mp3"
    audio_save_path = os.path.join(audio_dir, paragraph_audio_filename)

    saved_file = await tts_client.generate_audio(paragraph, audio_save_path)
    if saved_file:
        print(f"第 {i+1} 个段落音频已保存到: {audio_save_path}")
    else:
        print(f"第 {i+1} 个段落音频生成失败")


async def main():
    try:
        # 读取文本文件
        latest_file_path = os.path.join('text', 'target', 'latest.txt')
        with open(latest_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f'已读取文件: {latest_file_path}')

        # 按空行分割段落
        paragraphs = re.split(r'\n\s*\n', content.strip())
        print(f'共分割出 {len(paragraphs)} 个段落')

        # 初始化EdgeTTS客户端
        tts_client = EdgeTTSClient()

        # 创建任务列表
        tasks = []
        for i, paragraph in enumerate(paragraphs):
            tasks.append(process_paragraph(tts_client, paragraph, i))

        # 使用asyncio.gather并发执行所有任务
        await asyncio.gather(*tasks)

    except Exception as e:
        print(f'发生异常: {str(e)}')


def run_async_main():
    """运行异步主函数的包装函数"""
    asyncio.run(main())


if __name__ == "__main__":
    # 使用线程池运行异步主函数
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(run_async_main)