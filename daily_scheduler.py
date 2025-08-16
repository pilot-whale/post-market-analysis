import datetime
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler

def run_daily_news_script():
    print(f"{datetime.datetime.now()} - 开始执行 daily_news 脚本")
    try:
        # 使用 subprocess.run() 运行外部脚本
        result = subprocess.run(
            ["python", r"./script.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"{datetime.datetime.now()} - 脚本执行成功")
        print("输出结果:", result.stdout)
        if result.stderr:
            print("错误信息:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"{datetime.datetime.now()} - 脚本执行失败（返回码 {e.returncode}）")
        print("错误输出:", e.stderr)
    except Exception as e:
        print(f"{datetime.datetime.now()} - 发生未知错误: {str(e)}")

# 创建调度器，设置时区为上海
scheduler = BlockingScheduler(timezone='Asia/Shanghai')

# 添加任务：每天 7:00 执行
scheduler.add_job(
    func=run_daily_news_script,
    trigger='cron',
    hour=7,
    minute=0,
    misfire_grace_time=60
)

print("定时任务已启动，每天 7:00 执行 script.py... (按 Ctrl+C 退出)")
scheduler.start()