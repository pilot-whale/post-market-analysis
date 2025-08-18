import datetime
import subprocess
import os
from apscheduler.schedulers.blocking import BlockingScheduler


def run_script():
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建script.py的完整路径
    script_path = os.path.join(current_dir, 'script.py')
    # 执行script.py
    subprocess.run(['python', script_path], check=True)


# 创建调度器：BlockingScheduler
scheduler = BlockingScheduler(timezone='Asia/Shanghai')

daily_starting_time = ['0800', '0900', '1000', '1100', '1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900']

# 添加任务
for time_point in daily_starting_time:
    scheduler.add_job(func=run_script, trigger='cron', day_of_week="0-4", hour=time_point[:-2],
                      minute=time_point[-2:],
                      misfire_grace_time=120)

scheduler.start()