import datetime
from schedule import every, repeat, run_pending
import time
import logging
import os 


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

now = datetime.datetime.now() # 获取当前时间

# 每天上午8点到12点，下午2点到6点为工作时间
start_time1 = datetime.time(hour=8, minute=0) 
end_time1 = datetime.time(hour=12, minute=0) 
start_time2 = datetime.time(hour=14, minute=0) 
end_time2 = datetime.time(hour=18, minute=0) 

def main():
    logging.debug("Starting to schedule.....")
    # 判断当前时间是否再工作时间内
    if start_time1 <= now.time() <= end_time1 or start_time2 <= now.time() <= end_time2:

        # 如果当前是周末（六、日），则20分钟抓取一下OA首页
        # 非周末则10分钟抓取一下
        if now.weekday() == (5 or 6):
            # 这里的时间调度使用了 schedule 的repeat 包装器
            # schedule 模块的文档参见： https://schedule.readthedocs.io/en/stable/
            @repeat(every(20).minutes)
            def job():
                    os.system("python main.py")
        else:
            @repeat(every(10).minutes)
            def job():
                    os.system("python main.py")
            
        while True:
            # 进行调度
            run_pending()
            time.sleep(5)

if __name__ == "__main__":
    while True:
        logging.debug(f"{now.time()}")
        main()
        time.sleep(60)