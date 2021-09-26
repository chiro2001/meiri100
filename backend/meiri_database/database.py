import os
import threading
import time
# from utils.logger import logger
from gbk_database.tools import *
from gbk_system.database import SystemDB, SpiderDB
from gbk_user.database import UserDB
from gbk_session.database import SessionDB
from gbk_scheduler.task_database import TaskManagerDB
from gbk_sync.database import SyncDB
from gbk_daemon.database import DaemonDB
from utils.error_report import send_report


class DataBase:
    # 用到的所有数据集合
    COLLECTIONS = [
        'user', 'user_uid', 'gbk_bug', 'session', 'session_disabled_token',
        'task_manager', 'task_tid', 'daemon', 'cookies', 'sync', 'system',
        'service', 'spider'
    ]

    def __init__(self, dismiss_rebase=False):
        self.client = None
        self.db = None
        self.connect_init()
        self.user: UserDB = None
        self.session: SessionDB = None
        self.task_manager: TaskManagerDB = None
        self.system: SystemDB = None
        self.spider: SpiderDB = None
        self.sync: SyncDB = None
        self.daemon: DaemonDB = None
        self.init_parts()
        self.first_start = not dismiss_rebase
        if Constants.RUN_REBASE and not dismiss_rebase:
            self.rebase()

    def init_parts(self):
        self.user = UserDB(self.db)
        self.session = SessionDB(self.db)
        self.task_manager = TaskManagerDB(self.db)
        self.system = SystemDB(self.db)
        self.spider = SpiderDB(self.db)
        self.sync = SyncDB(self.db)
        self.daemon = DaemonDB(self.db)

    def rebase(self):
        for col in DataBase.COLLECTIONS:
            logger.info(f'Dropping {col}')
            self.db[col].drop()
        self.init_parts()
        uid = self.user.insert(Constants.USERS_OWNER)
        self.session.insert(uid=uid, password=Constants.USERS_OWNER_PASSWORD)

    def connect_init(self):
        if len(Constants.DATABASE_URI) > 0:
            self.client = pymongo.MongoClient(Constants.DATABASE_URI)
        else:
            self.client = pymongo.MongoClient()
        self.db = self.client[Constants.DATABASE_NAME]

    def error_report(self, error, error_type: str = 'backend'):
        try:
            self.db.gbk_bug.insert_one({'time': time.asctime(), 'error': error, 'error_type': error_type})
        except Exception as e:
            logger.error(f'wanna to report err then {e}')
            self.db.gbk_bug.insert_one({'time': time.asctime(), 'error': str(error), 'error_type': error_type})
        if Constants.EMAIL_SENDING:
            send_report(error)

    def start_error_report(self, error, error_type: str = 'backend'):
        th = threading.Thread(target=self.error_report, args=(error, ), kwargs={'error_type': error_type})
        th.setDaemon(True)
        th.start()


# 由主进程启动的进程不重新初始化数据库
if os.getenv(Constants.PROC_DISMISS_REBASE) is None:
    os.environ.setdefault(Constants.PROC_DISMISS_REBASE, f"{os.getpid()}")

db = DataBase(dismiss_rebase=os.getenv(Constants.PROC_DISMISS_REBASE) == f"{os.getppid()}")

if __name__ == '__main__':
    pass
    # db.rebase()
    # db.session.insert('chiro', '3521')
    # logger.info(db.session.find_by_username('chiro'))
    # logger.info(db.session.check_password('chiro', '3521'))
    db.system.update_service_state(1, 'flow_data', db.system.SERVICE_START)
    print(get_next_exist_id(db.user.col, 'uid', 1))
    print(get_first_exist_id(db.user.col, 'uid'))
