import schedule
import threading
import time

t = 0


def do_async(fn):
    def wrapper(*args, **kwargs):
        th = threading.Thread(target=fn)
        th.setDaemon(True)
        th.start()

    return wrapper


# 定义需要执行的方法
@do_async
def job():
    global schedule, t
    print("a simple scheduler...", end='')
    time.sleep(2.5)
    print("in python.")


# 设置调度的参数，这里是每2秒执行一次
schedule.every(1).seconds.do(job)
if __name__ == '__main__':
    while True:
        schedule.run_pending()
