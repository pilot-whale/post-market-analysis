import requests
import os
import time
import re
from urllib.parse import urljoin


timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')  # 新格式：年-月-日_时-分-秒
audio_dir = r'./audio'
subtitle_dir = r'./text/subtitle'  # 字幕目录
# 确保 audio 和 subtitle 目录存在
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(subtitle_dir, exist_ok=True)

# 配置参数
# API_KEY 不再需要，因为我们不再调用火山引擎API

#------------------------------------------------------

class ChatTTSClient:
    def __init__(self, base_url="http://127.0.0.1:9966"):
        self.base_url = base_url
        self.tts_endpoint = urljoin(base_url, "/tts")
        
    def generate_audio(self, text, prompt="", voice="5555", temperature=0.00001, 
                      top_p=0.7, top_k=20, refine_max_new_token="384", 
                      infer_max_new_token="2048", skip_refine=0, is_split=1, 
                      custom_voice=0):
        """
        生成语音音频
        
        参数:
            text: 要转换为语音的文本
            其他参数: 参见API文档
            
        返回:
            成功时返回音频文件URL，失败时返回None
        """
        payload = {
            "text": text,
            "prompt": prompt,
            "voice": voice,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "refine_max_new_token": refine_max_new_token,
            "infer_max_new_token": infer_max_new_token,
            "skip_refine": skip_refine,
            "is_split": is_split,
            "custom_voice": custom_voice
        }
        
        try:
            response = requests.post(self.tts_endpoint, data=payload)
            result = response.json()
            
            if result.get("code") == 0 and "audio_files" in result:
                audio_url = result["audio_files"][0]["url"]
                full_audio_url = urljoin(self.base_url, audio_url)
                return full_audio_url
            else:
                print(f"Error: {result.get('msg', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"解析响应失败: {e}")
            return None
    
    def download_audio(self, audio_url, save_path=None):
        """
        下载生成的音频文件
        
        参数:
            audio_url: generate_audio返回的URL
            save_path: 保存路径(可选)
            
        返回:
            成功时返回保存的文件路径，失败时返回None
        """
        if not audio_url:
            return None
            
        try:
            response = requests.get(audio_url, stream=True)
            response.raise_for_status()
            
            if save_path is None:
                # 如果没有指定保存路径，使用URL中的文件名
                filename = os.path.basename(audio_url)
                save_path = os.path.join(os.getcwd(), filename)
                
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            return save_path
            
        except requests.exceptions.RequestException as e:
            print(f"下载音频失败: {e}")
            return None


# 使用示例
if __name__ == "__main__":
    try:
        # 读取 text/target/latest.txt 文件
        latest_file_path = os.path.join('text', 'target', 'latest.txt')
        with open(latest_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f'已读取文件: {latest_file_path}')

        # 按空行分割段落
        paragraphs = re.split(r'\n\s*\n', content.strip())
        print(f'共分割出 {len(paragraphs)} 个段落')

        # 初始化 TTS 客户端
        tts_client = ChatTTSClient()

        # 为每个段落生成音频和保存字幕
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue

            print(f'正在处理第 {i+1} 个段落...')
            print(f'段落内容: {paragraph}')

            # 保存字幕到 text/subtitle 目录
            # subtitle_filename = f"subtitle_{timestamp}_paragraph_{i+1}.txt"
            # subtitle_save_path = os.path.join(subtitle_dir, subtitle_filename)
            subtitle_filename = f"{i+1}.txt"
            subtitle_save_path = os.path.join(subtitle_dir, subtitle_filename)
            with open(subtitle_save_path, 'w', encoding='utf-8') as f:
                f.write(paragraph)
            print(f"第 {i+1} 个段落字幕已保存到: {subtitle_save_path}")

            # 生成音频
            audio_url = tts_client.generate_audio(paragraph)

            if audio_url:
                print(f"第 {i+1} 个段落音频生成成功，URL: {audio_url}")

                # 下载音频
                # paragraph_audio_filename = f"audio_{timestamp}_paragraph_{i+1}.wav"
                # audio_save_path = os.path.join(audio_dir, paragraph_audio_filename)
                paragraph_audio_filename = f"{i+1}.wav"
                audio_save_path = os.path.join(audio_dir, paragraph_audio_filename)
                saved_file = tts_client.download_audio(audio_url, save_path=audio_save_path)
                if saved_file:
                    print(f"第 {i+1} 个段落音频已保存到: {audio_save_path}")
            else:
                print(f"第 {i+1} 个段落音频生成失败")

    except Exception as e:
        print(f'发生异常: {str(e)}')