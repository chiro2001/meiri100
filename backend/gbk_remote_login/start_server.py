import os
import threading
import time


def chdir(path: str, delay=0.5):
    time.sleep(delay)
    os.chdir(path)


def run():
    path_origin = os.path.abspath(os.path.curdir)
    os.chdir('./login_server')
    # os.system("node server.js > server_log.txt")
    t = threading.Thread(target=chdir, args=(path_origin,))
    t.setDaemon(True)
    t.start()
    os.system("node server.js")


def start_server():
    th = threading.Thread(target=run)
    th.setDaemon(True)
    th.start()
