import requests
import os
import time
from urllib.parse import urljoin


timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')  # 新格式：年-月-日_时-分-秒
text_filename = f'text_{timestamp}.txt'
audio_filename = f'audio_{timestamp}.wav'
text_dir = r'./text'
audio_dir = r'./audio'

# 配置参数
API_KEY = '39e65a79-75f7-4fdc-ad4e-81def170685b'
target_text = '扮演财经主播，用60秒口播今日5大股市要闻。结构：编号+事件影响+核心数据+股市对应的机会与风险，结尾加1句”投资有风险，入市需谨慎！“。风格：动词开头（如‘爆涨’‘引爆’）、适合口头传播。禁忌：不用‘的/了’、禁用个股名称、禁用专业术语如‘息差’，‘再贷款’。（注意尽量不要用多音字，回答必须是严格的中文文本，不可以有英文字母，不要有符号）'

# 构建请求头
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# 构造请求体
payload = {
    "model": "doubao-seed-1-6-250615",
    "messages": [{
        "role": "user",
        "content": target_text
    }]
}

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
        # 发送API请求
        response = requests.post(
          'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
          headers=headers,
          json=payload
      )
    
      # 处理响应
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']

            # # 1. 在小标题（数字. ）后添加换行
            # processed_answer = re.sub(r'(\d+\.\s)', r'\1\n', answer)
            # # 2. 将所有标点符号替换为换行
            # processed_answer = re.sub(r'[，。、；：！？“”‘’（）【】]', r'\n', processed_answer)
            # # 3. 将所有空格替换为换行
            # processed_answer = processed_answer.replace(' ', '\n')
        
           # 保存到独立文件
            with open(os.path.join(text_dir, text_filename), 'w', encoding='utf-8') as f:
                f.write(f"问题：{target_text}\n\n回答：{answer}")
            print(f'结果已保存至{text_filename}')

            # 同时写入latest.txt（覆盖模式）
            with open(os.path.join(text_dir, 'latest.txt'), 'w', encoding='utf-8') as f:
                f.write(f"{answer}")
            print(f'结果已更新至"latest.txt"')
        else:
            print(f'API调用失败: {response.status_code} {response.text}')

    except Exception as e:
        print(f'发生异常: {str(e)}')


    tts_client = ChatTTSClient()
    
    # 生成音频
    text_to_speak = answer
    audio_url = tts_client.generate_audio(text_to_speak)
    
    if audio_url:
        print(f"音频生成成功，URL: {audio_url}")
        
        # 下载音频
        audio_save_path = os.path.join(audio_dir, audio_filename)
        saved_file = tts_client.download_audio(audio_url, save_path=audio_save_path)
        if saved_file:
            print(f"音频已保存到: {audio_save_path}")

        audio_save_path = os.path.join(audio_dir, "latest.wav")
        saved_file = tts_client.download_audio(audio_url, save_path=audio_save_path)
        if saved_file:
            print(f"音频已保存到: latest.wav")

    else:
        print("音频生成失败")