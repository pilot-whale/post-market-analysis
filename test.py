import edge_tts
import asyncio

async def main():
    # 生成语音并保存为文件
    voice = edge_tts.Communicate(text="你好，这是Edge TTS生成的中文语音。", voice="zh-CN-YunxiNeural")
    await voice.save("output.mp3")  # 使用await等待协程完成

# 运行主函数
asyncio.run(main())