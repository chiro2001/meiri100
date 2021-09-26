import os
import time

from meiri_database.database import db, Constants
from data_apis.api import API
from meiri_exceptions import *
from utils.time_formats import get_date_today, get_date_timestamp, get_timestamp_date

daemon_types = [
    "cookies", "shop_info", "solution_id", "reserve_date", "reserve_table", "room_stock"
]


class DaemonBean:
    def __init__(self, uid: int, cookies: str = None, shop_info: dict = None, shops: dict = None,
                 solution_id: int = None, reserve_date: dict = None,
                 reserve_table: dict = None, room_stock: dict = None):
        self.uid: int = uid
        self.cookies: str = cookies

    def __getstate__(self):
        return self.__dict__

    def get_api(self):
        # return API.from_all(cookies=self.cookies, solution_id=self.solution_id, shop_id=self.shop_info['shopId'])
        return API.from_cookies(cookies=self.cookies)

    def refresh(self):
        self.cookies = db.daemon.load(self.uid, data_type='cookies')
        self.cookies = self.cookies.get('data') if isinstance(self.cookies, dict) else None
        return self

    def save(self, select: list = None):
        select = select if select is not None else self.__getstate__().keys()
        select = [select, ] if isinstance(select, str) else select
        if 'cookies' in select:
            db.daemon.save(self.uid, self.cookies, data_type='cookies') if self.cookies is not None else None
        return self


class Daemon:
    def __init__(self, init_data: bool = True):
        self.pool = {}
        # 初始化所有已经远程登录的 daemon
        data = db.daemon.load(None, data_type='cookies')
        if init_data:
            for d in data:
                # print('data', d)
                try:
                    self.pool[d['uid']] = self.init_data(d['uid'], cookies=d['data'])
                except (MeiRiLoginError, MeiRiPermissionError) as e:
                    logger.error(f'[{d["uid"]}] {e}, retrying')
                    try:
                        self.pool[d['uid']] = self.init_data(d['uid'])
                    except (MeiRiLoginError, MeiRiPermissionError) as e:
                        logger.error(f'[{d["uid"]}] {e}, passing uid {d["uid"]}')

        self.data_inited = init_data

    def delete_daemon(self, uid: int, select_types: list = None):
        if uid is None:
            return False
        if uid not in self.pool:
            return False
        del self.pool[uid]
        select_types = daemon_types if select_types is None else select_types
        for daemon_type in select_types:
            db.daemon.delete(uid, daemon_type)
        return True

    def get_daemon(self, uid: int, init_new: bool = False, cookies: str = None):
        # return self.pool.get(uid, default=None)
        if uid is None:
            raise MeiRiError()
        if uid in self.pool:
            return self.pool[uid]
        if init_new and cookies is None:
            cookies = db.daemon.load(uid, data_type='cookies')
            cookies = cookies.get("data") if cookies is not None else None
        if init_new and cookies is not None:
            self.pool[uid] = self.init_data(uid, cookies=cookies)
            return self.pool[uid]
        return None

    @staticmethod
    def get_base_info(uid: int) -> tuple:
        solution_id = db.daemon.load(uid, data_type='solution_id')
        solution_id = solution_id.get('data') if solution_id is not None else None
        shop_info = db.daemon.load(uid, data_type='shop_info')
        shop_info = shop_info.get('data') if shop_info is not None else None
        return solution_id, shop_info

    def get_api(self, uid: int, cookies: str):
        api: API

        solution_id, shop_info = self.get_base_info(uid)
        if solution_id is None or shop_info is None:
            api = API.from_cookies(cookies)
        else:
            api = API.from_cookies(cookies=cookies)
        logger.info(f'[{uid}] shop_info: {shop_info}')
        return api

    def update_data(self, uid: int, api: API = None, cookies: str = None, update_all: bool = False, **kwargs):
        if api is None:
            if cookies is None:
                cookies = db.daemon.load(uid, data_type='cookies')
                cookies = cookies.get('data', None) if cookies is not None else None
                if cookies is None:
                    raise MeiRiLoginError(Constants.EXCEPTION_LOGIN)
            # api = self.get_api(uid, cookies=cookies)
        daemon_data = DaemonBean(uid=uid).refresh()
        return daemon_data

    def init_data(self, uid: int, cookies: str = None, update_data: bool = False, **kwargs):
        daemon_data: DaemonBean = self.pool.get(uid)
        if cookies is not None:
            db.daemon.save(uid, cookies, data_type='cookies')
        else:
            cookies = db.daemon.load(uid, data_type='cookies')
            cookies = cookies.get('data') if cookies is not None else None
        api: API = self.get_api(uid, cookies=cookies)
        solution_id, shop_info = self.get_base_info(uid)
        if update_data:
            daemon_data = self.update_data(uid, api=api, update_all=True, **kwargs)
        if daemon_data is None:
            daemon_data = DaemonBean(uid, cookies=cookies, shop_info=shop_info, solution_id=solution_id)
        # daemon_data.shop_info = shop_info
        # daemon_data.solution_id = solution_id
        return daemon_data


# 由主进程启动的进程不重新初始化数据库
if os.getenv(Constants.PROC_DISMISS_DAEMON_INIT) is None:
    os.environ.setdefault(Constants.PROC_DISMISS_DAEMON_INIT, f"{os.getpid()}")

daemon = Daemon(init_data=os.getenv(Constants.PROC_DISMISS_DAEMON_INIT) != f"{os.getppid()}")
