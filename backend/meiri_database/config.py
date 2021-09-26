import os
import platform
import pymongo
from utils.logger import logger
import secrets
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSS
from pytz import utc
# from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


# 运行时常量
class Constants:
    # Version info
    # 版本信息和开发者信息
    VERSION = "0.0.1"
    OWNER = "Chiro"
    EMAIL = "Chiro2001@163.com"
    # 当前环境判断，['release', 'dev']
    # Environment
    ENVIRONMENT = os.environ.get("ENV") if os.environ.get("ENV") is not None else (
        "release" if platform.system() == 'Linux' else "dev")
    # Database
    DATABASE_URI = secrets.SECRET_MONGO_URI
    DATABASE_NAME = DATABASE_URI.split('/')[-1]
    DATABASE_COL_NAME = 'config'
    # Email
    EMAIL_SENDER = "LanceLiang2018@163.com"
    EMAIL_SMTP_PASSWORD = secrets.SECRET_EMAIL_SMTP_PASSWORD
    EMAIL_ERROR_TITLE = "meiri errors"
    EMAIL_SMTP_SSL = 'smtp.163.com'
    EMAIL_SMTP_PORT = 465
    # release 环境才发消息
    EMAIL_SENDING = ENVIRONMENT == 'release'
    # API config
    # 总的API Path
    API_PATH = '/api/v1'
    # Running config，运行配置
    RUN_LISTENING = "0.0.0.0"
    RUN_PORT = int(os.environ.get("PORT", 8088))
    # 调试用热重载（并不好用
    RUN_USE_RELOAD = False
    # 开启时候是否重置数据库
    # RUN_REBASE = True
    RUN_REBASE = False
    # 是否加载 tensorflow
    RUN_WITH_PREDICTS = ENVIRONMENT == 'release'
    RUN_IGNORE_TF_WARNINGS = True
    # dev 环境下打开 api 中的删库跑路操作（
    RUN_WITH_DROP_DATA = ENVIRONMENT == 'dev'
    # 调试模式下输出系统的TASK信息
    RUN_WITH_SYS_TASK_LOG = ENVIRONMENT != 'release'
    # 调试模式下忽略这些系统task（是爬虫
    RUN_DISMISS_TASK = [] if ENVIRONMENT == 'release' else []
    # 系统task运行间隔
    RUN_TASKS_DELAYS = {

    } if ENVIRONMENT == 'release' else {

    }
    # Schedule
    # 配置使用内存做 Job 储存，因为已经在数据库自己实现一套储存结构了
    SCHEDULE_JOBSTORES = {
        # 'default': MongoDBJobStore(
        #     client=(pymongo.MongoClient(DATABASE_URI) if len(DATABASE_URI) > 0 else pymongo.MongoClient)),
        'default': MemoryJobStore()
    }
    SCHEDULE_EXECUTORS = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }
    SCHEDULE_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 300,
        'misfire_grace_time': 10
    }
    SCHEDULE_CONFIG = {
        'jobstores': SCHEDULE_JOBSTORES, 'executors': SCHEDULE_EXECUTORS, 'job_defaults': SCHEDULE_JOB_DEFAULTS,
        'timezone': utc
    }
    # Request API
    # 对外部 API 进行请求的时候的公用参数
    REQUEST_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"
    REQUEST_DEBUG_COOKIES = "PHPSESSID=ib16uod9ccd8nrl2nk7cgjftt1;"
    # Dismiss rebase for multiprocessing
    # 多进程状态下的兼容参数
    PROC_DISMISS_REBASE = 'GBK_DB_RUNNING_PID'
    PROC_DISMISS_COS = 'GBK_COS_RUNNING_PID'
    PROC_DISMISS_DAEMON_INIT = "GBK_DAEMON_RUNNING_PID"
    # 兼容参数：raise 一个 Exception 时候的固定参数
    EXCEPTION_LOGIN = "No cookies!"


# 运行中静态数据
class Statics:
    pass


# 可以及时调整的存在数据库的参数
class Config:
    def __init__(self):
        self.data_default = {
            "version": Constants.VERSION,
            "api_server": {
                "upgradable": True,
                "api_prefix": Constants.API_PATH
            },
            # 调试的时候用的静态文件服务器
            "file_server": {
                "upgradable": True,
                "static_path": "./public",
                "index": "index.html",
                "routers": []
            }
        }
        self.data = self.data_default
        self.load()

    # 这存取数据库单独处理不用database
    # 防止循环引用
    def save(self):
        client = pymongo.MongoClient(Constants.DATABASE_URI)
        db = client[Constants.DATABASE_NAME]
        col = db[Constants.DATABASE_COL_NAME]
        result = col.find_one({'version': {'$exists': True}}, {'_id': 0})
        if result is None:
            col.insert_one(self.data)
        else:
            col.update_one({'version': {'$exists': True}}, {'$set': self.data})
        client.close()

    def load(self):
        client = pymongo.MongoClient(Constants.DATABASE_URI)
        db = client[Constants.DATABASE_NAME]
        col = db[Constants.DATABASE_COL_NAME]
        result = col.find_one({'version': {'$exists': True}}, {'_id': 0})
        if result is None:
            logger.warning('loading default config data...')
            self.data = self.data_default
        else:
            self.data = result
        self.save()
        client.close()


config = Config()
