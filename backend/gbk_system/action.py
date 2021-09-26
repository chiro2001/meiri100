import multiprocessing
import os
import shutil
import threading
import time
import zipfile
from io import BytesIO

import secrets
from data_apis.api import API
from gbk_daemon.daemon import DaemonBean, daemon
from gbk_database.database import db, Constants
from gbk_database.tools import get_next_exist_id, get_current_id
from gbk_exceptions import GBKError, GBKPermissionError, GBKLoginError
from gbk_scheduler.action import Action, get_first_exist_id, ActionPriceAdjust
from gbk_scheduler.task import TaskManager
# from gbk_scheduler.task_pool import task_pool
from gbk_scheduler.trigger import StockTrigger
from gbk_system.database import SystemDB
from utils.cos_uploader import upload_file
from utils.files import del_file, folder2zip
from utils.formats import year_month_to_timestamp
from utils.logger import logger
from utils.time_formats import get_date_today, get_next_week_date, get_timestamp_date


class ActionCycle(Action):
    FIRST_YEAR = 2020

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_type = kwargs.get('service_type', 'base')
        self.service: dict = db.system.get_service(self.service_type)
        self.uid: int = get_first_exist_id(db.user.col, 'uid')
        self.year: int = self.FIRST_YEAR
        self.month: int = 1
        self.page: int = 1
        self.page_count: int = None
        self.shop_id: int = None
        self.cookies: str = None
        # self.item_list: list = None
        self.uid_list: list = []
        self.load()
        self.save(state=SystemDB.SERVICE_STOP)

    def load(self):
        # logger.warning(f'loading {self.service}')
        if self.service is not None:
            self.uid = self.service.get('uid', self.uid)
            self.year = self.service.get('year', self.year)
            self.month = self.service.get('month', self.month)
            self.page = self.service.get('page', self.page)
            self.page_count = self.service.get('page_count', self.page_count)
            # self.item_list = self.service.get('item_list', self.item_list)

    def save(self, state: str = SystemDB.SERVICE_RUNNING):
        db.system.update_service_state(self.service_type, state=state, data=self.__getstate__())

    def __getstate__(self):
        # return {
        #     'uid': self.uid,
        #     'year': self.year,
        #     'month': self.month,
        #     'page': self.page,
        #     'page_count': self.page_count,
        #     # 'item_list': self.item_list
        # }
        d = self.__dict__
        if 'service' in d:
            del d['service']
        return d

    def update_uid(self, uid: int):
        self.uid_list = [uid, ].extend(self.uid_list) if isinstance(self.uid_list, list) else []

    def next_uid(self):
        if self.uid_list is None or len(self.uid_list) == 0 or not isinstance(self.uid_list, list):
            self.uid_list = []
            next_uid = get_first_exist_id(db.user.col, 'uid')
            while next_uid is not None:
                self.uid_list.append(next_uid)
                next_uid = get_next_exist_id(db.user.col, 'uid', next_uid)
        if len(self.uid_list) != 0:
            next_uid = get_next_exist_id(db.user.col, 'uid', self.uid_list[-1])
            if next_uid is None:
                next_uid = get_first_exist_id(db.user.col, 'uid')
            self.uid_list.append(next_uid)
            self.uid = self.uid_list[0]
            self.uid_list = self.uid_list[1:]
            if Constants.RUN_WITH_SYS_TASK_LOG:
                logger.warning(f'new uid: {self.uid}')
        else:
            raise GBKError("Users not enough!")
        self.year = self.FIRST_YEAR
        self.month = 1
        self.shop_id = None
        self.cookies = None

    def next_month(self):
        self.month += 1
        # self.item_list = None
        self.page_count = None
        if self.month > 12:
            self.month = 1
            self.year += 1
            if self.is_time_over():
                self.next_uid()

    def next_page(self):
        if self.page_count is None:
            self.next_month()
            self.page = 1
            return
        self.page += 1
        if self.page == self.page_count + 1:
            self.page = 1
            self.next_month()

    def is_time_over(self) -> bool:
        return time.time() < year_month_to_timestamp(self.year, self.month)

    def get_next_month_timestamp(self):
        if self.month == 12:
            return year_month_to_timestamp(self.year + 1, 1)
        return year_month_to_timestamp(self.year, self.month + 1)

    def get_timestamp(self):
        return year_month_to_timestamp(self.year, self.month)

    def update_shop_id(self):
        if self.shop_id is None:
            if self.cookies is None:
                cookies = db.daemon.load(self.uid, 'cookies')
                cookies = cookies if cookies is None else cookies.get('data')
                # T-O-D-O: Cookies校验
                if cookies is None:
                    self.next_uid()
                    return
                self.cookies = cookies
            try:
                api = API.from_cookies(self.cookies)
            except GBKLoginError as e:
                # 删除该cookies
                db.daemon.delete(self.uid, data_type="cookies")
                raise e
            self.shop_id = api.shop_id


class ActionFetchFlowData(ActionCycle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, service_type='flow_data')

    def exec(self):
        new_service_info = db.system.get_service_info(self.service_type)
        key = "%d-%02d-02" % (self.year, self.month)
        next_key = "%d-%02d-01" % (self.year if self.month != 12 else self.year + 1,
                                   self.month + 1 if self.month != 12 else 1)
        if new_service_info['state'] != SystemDB.SERVICE_STOP and Constants.RUN_WITH_SYS_TASK_LOG:
            logger.warning(f"[ flow_data ] uid:{self.uid}, {key} => {next_key} ( SKIP )")
            self.next_month()
            self.save(state=SystemDB.SERVICE_STOP)
            return
        self.save(state=SystemDB.SERVICE_RUNNING)
        if Constants.RUN_WITH_SYS_TASK_LOG:
            logger.warning(f"[ flow_data ] uid:{self.uid}, {key} => {next_key}")
        self.update_shop_id()
        try:
            resp: dict = API(self.cookies).flow_data.get(key,
                                                         shop_id=self.shop_id,
                                                         end_time=next_key)
        except GBKPermissionError as e:
            logger.error(f"[ flow_data ] {e}")
            db.daemon.delete(uid=self.uid, data_type="cookies")
            self.cookies = None
            self.next_uid()
            self.save(state=SystemDB.SERVICE_STOP)
            # raise e
            return
        if 'code' not in resp or \
                ('code' in resp and resp['code'] != 200 and resp['code'] != 0) or \
                'data' not in resp:
            logger.error(f"[ flow_data ] Resp error: uid:{self.uid}, {key} => {next_key}")
            logger.debug(resp)
            self.next_month()
            self.save(state=SystemDB.SERVICE_STOP)
            raise GBKPermissionError()
        db.spider.save(self.uid, {
            'flow_data': resp['data'],
            'task_data': self.__getstate__()
        }, 'flow_data', key)
        self.next_month()
        self.save(state=SystemDB.SERVICE_STOP)


# 内部Action，定时执行：TradeData
class ActionFetchTradeData(ActionCycle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, service_type='trade_data')

    def exec(self):
        new_service_info = db.system.get_service_info(self.service_type)
        key = "%d-%02d" % (self.year, self.month)
        if new_service_info['state'] != SystemDB.SERVICE_STOP and Constants.RUN_WITH_SYS_TASK_LOG:
            logger.warning(f"[ trade_data ] uid:{self.uid}, {key}, page: {self.page} ( SKIP )")
            return
        self.save(state=SystemDB.SERVICE_RUNNING)
        if Constants.RUN_WITH_SYS_TASK_LOG:
            logger.warning(
                f"[ trade_data ] uid:{self.uid}, {key}, page: {self.page} "
                f"({'%4.2f%%' % ((self.page / self.page_count * 100) if self.page_count is not None else 0)})")
        self.update_shop_id()
        try:
            resp: dict = API(self.cookies).trade_data.get(self.get_timestamp() * 1000,
                                                          self.get_next_month_timestamp() * 1000,
                                                          page=self.page, shop_id=self.shop_id)
        except GBKPermissionError as e:
            logger.error(f"[ trade_data ] {e}")
            db.daemon.delete(uid=self.uid, data_type="cookies")
            self.cookies = None
            self.next_uid()
            self.save(state=SystemDB.SERVICE_STOP)
            # raise e
            return
        if 'code' not in resp or ('code' in resp and resp['code'] != 200):
            logger.error(f"[ trade_data ] Resp error: uid:{self.uid}, {key}, page: {self.page}")
            self.next_page()
            self.save(state=SystemDB.SERVICE_STOP)
            raise GBKPermissionError()
        try:
            trade_data_list = resp['data']['itemList']
            self.page_count = resp['data']['pageCount']
        except KeyError as e:
            if Constants.RUN_WITH_SYS_TASK_LOG:
                logger.error(f'[ trade_data ] KeyError, {resp.keys()}, {e}')
            logger.debug(resp)
            self.next_page()
            return
        # if self.item_list is None:
        #     self.item_list = []
        # self.item_list.extend(trade_data_list)
        # db.spider.save(self.uid, self.item_list, 'trade_data', key)
        db.spider.save(self.uid, {
            'item_list': trade_data_list,
            'task_data': self.__getstate__()
        }, 'trade_data', key)
        self.next_page()
        self.save(state=SystemDB.SERVICE_STOP)


class ActionBackupData(ActionCycle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, service_type='backup')

    @staticmethod
    def run():
        os.chdir('./logs')
        if os.path.exists('dump') and os.path.isdir('dump'):
            # del_file("dump")
            shutil.rmtree('dump')
        os.system(f"mongodump --gzip --uri {secrets.SECRET_MONGO_URI}")

        # file_data = BytesIO()
        # zip_file = zipfile.ZipFile(file_data, 'w')
        # zip_file.write('dump', compress_type=zipfile.ZIP_DEFLATED)
        # zip_file.close()
        # file_data.seek(0)
        # upload_file(f"mongo/gbk/{time.asctime().replace(' ', '_').replace(':', '-')}.zip",
        #             file_data.read())

        file_data = folder2zip('dump')
        upload_file(f"mongo/gbk/{int(time.time())}_{time.asctime().replace(' ', '_').replace(':', '-')}.zip",
                    file_data)
        if os.path.exists('dump') and os.path.isdir('dump'):
            # del_file("dump")
            shutil.rmtree('dump')

    def exec(self):
        p = multiprocessing.Process(target=ActionBackupData.run)
        p.start()


class ActionUpdateStockData(ActionCycle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, service_type='stock')

    def exec(self):
        new_service_info = db.system.get_service_info(self.service_type)
        if new_service_info is None:
            logger.warning('got None new_service_info!')
            return
        if new_service_info['state'] != SystemDB.SERVICE_STOP and Constants.RUN_WITH_SYS_TASK_LOG:
            logger.warning(f"[ stock ] uid:{self.uid} ( SKIP )")
            self.next_uid()
            self.save(state=SystemDB.SERVICE_STOP)
            return
        self.save(state=SystemDB.SERVICE_RUNNING)
        if Constants.RUN_WITH_SYS_TASK_LOG:
            logger.warning(f"[ stock ] uid:{self.uid}")
        d: DaemonBean = daemon.get_daemon(self.uid)
        if d is None:
            logger.debug(f"[ stock ] uid:{self.uid}, no daemon!")
            return
        if self.cookies is None:
            self.cookies = d.cookies
            if self.cookies is None:
                self.update_shop_id()
        try:
            resp: dict = d.get_api().room_stock.get_room_stock()
        except GBKPermissionError as e:
            logger.error(f"[ stock ] {e}")
            db.daemon.delete(uid=self.uid, data_type="cookies")
            self.cookies = None
            self.next_uid()
            self.save(state=SystemDB.SERVICE_STOP)
            # raise e
            return
        if 'code' not in resp or ('code' in resp and resp['code'] != 200) or 'data' not in resp:
            logger.error(f"[ stock ] Resp error: uid:{self.uid}")
            logger.debug(resp)
            self.next_uid()
            self.save(state=SystemDB.SERVICE_STOP)
            raise GBKPermissionError()
        d.room_stock = {
            'room_stock': resp['data'],
            'task_data': self.__getstate__()
        }
        d.save('room_stock')
        self.next_uid()
        self.save(state=SystemDB.SERVICE_STOP)


class ActionRoomStockCheck(ActionCycle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, service_type='stock_check')

    @staticmethod
    def check_one(uid: int, api: API = None, manager: TaskManager = None):
        logger.debug(f'uid: {uid}')
        d: DaemonBean = daemon.get_daemon(uid)
        if d is not None:
            api = d.get_api()
        if api is None:
            logger.debug(f'[ stock_check_one ] uid:{uid} got empty api!')
            return
        if d.room_stock is None:
            logger.debug(f'[ stock_check_one ] uid:{uid} got empty room stock data!')
            return
        from gbk_scheduler.task_pool import task_pool
        if manager is None:
            manager = task_pool.get_manager(uid)
        if manager is None:
            logger.debug(f"[ stock_check_one ] uid:{uid} ( NO MANAGER )")
            # print(task_pool)
            return

        def find_room_from_stock(stocks: list, date: str, period_desc_: str, room_name: str):
            for daily_stock in stocks:
                reserve_date = get_timestamp_date(daily_stock['reserveDate'])
                if reserve_date == date:
                    for period_stock in daily_stock['periodStockList']:
                        if period_stock['periodDesc'] == period_desc_:
                            for room_stock in period_stock['roomStockList']:
                                if room_stock['roomName'] == room_name:
                                    return room_stock
            return None

        def check_stock_trigger(stock_trigger: StockTrigger, stock: dict):
            if stock_trigger.operator == '<':
                return stock_trigger.value < stock['remainCount']
            elif stock_trigger.operator == '>':
                return stock_trigger.value > stock['remainCount']
            elif stock_trigger.operator == '==':
                return stock_trigger.value == stock['remainCount']
            elif stock_trigger.operator == '<=':
                return stock_trigger.value <= stock['remainCount']
            elif stock_trigger.operator == '>=':
                return stock_trigger.value >= stock['remainCount']
            elif stock_trigger.operator == '!=':
                return stock_trigger.value != stock['remainCount']
            logger.warning(f'[ stock_check_one ] uid:{uid}, check_failed!')
            return False

        # 找到根据库存调整的任务
        for task in manager.find_task_by_trigger_class(StockTrigger):
            # 找到对应Actions
            actions: list = task.get_actions_by_class(ActionPriceAdjust)
            triggers: list = task.get_triggers_by_class(StockTrigger)
            # 通过 Action 找 RoomStock
            for action in actions:
                # action = ActionPriceAdjust()
                if not isinstance(action, ActionPriceAdjust):
                    continue
                if action.day is None:
                    logger.warning(f'[ stock_check_one ] uid:{uid}, got empty day!')
                    continue
                next_date: int = get_next_week_date(action.day)
                logger.debug(f'next_date: {next_date}')
                period_desc: str = action.periodDesc[:-2] if action.periodDesc.endswith('包段') else action.periodDesc
                logger.debug(f'period_desc: {period_desc}')
                # 在 room_stock 中找到对应的 StockItem
                stock = find_room_from_stock(d.room_stock['room_stock']['dailyStockList'], next_date, period_desc,
                                             action.roomName)
                if stock is None:
                    logger.warning(f'[ stock_check_one ] uid:{uid}, got empty stock!')
                # item_id 可能随时间变化
                # sys_key = f'{task.tid}_{action.item_id}'
                sys_key = {
                    'tid': task.tid,
                    'day': action.day,
                    'periodDesc': period_desc,
                    'roomName': action.roomName
                }
                logger.debug(f'sys_key: {sys_key}')
                running_state: dict = db.system.load_key(uid=uid, key=sys_key, data_type='room_stock_check')
                running_state: dict = running_state.get('data') if running_state is not None else None
                if running_state is not None and \
                        isinstance(running_state, dict) and \
                        'state' in running_state and \
                        running_state['state'] == 'effecting':
                    logger.warning(f'[ stock_check_one ] uid:{uid}, {sys_key}, ( SKIP )')
                    continue
                else:
                    logger.warning(f'[ stock_check_one ] uid:{uid}, running_state: {running_state}')
                to_adjust: bool = False
                for trigger in triggers:
                    if not check_stock_trigger(trigger, stock):
                        logger.debug(f'[ stock_check_one ] uid:{uid}, not to adjust...')
                        continue
                    else:
                        logger.info(f'[ stock_check_one ] uid:{uid}, to adjust...')
                        to_adjust = True
                if not to_adjust:
                    # 恢复状态
                    db.system.save_key(uid=uid, key=sys_key, data={
                        'state': 'available'
                    }, data_type='room_stock_check')
                    logger.info(f'[ stock_check_one ] uid:{uid}, resume.')
                else:
                    db.system.save_key(uid=uid, key=sys_key, data={
                        'state': 'effecting'
                    }, data_type='room_stock_check')
                    logger.info(f'[ stock_check_one ] uid:{uid}, effecting')
                    action.exec()

    @staticmethod
    def start_branch():
        # 获取所有uid
        uid_cnt = get_current_id(db.user.d.user_uid, "cnt_uid")
        ths = []
        for uid in range(1, uid_cnt + 1):
            t = threading.Thread(target=ActionRoomStockCheck.check_one, args=(uid,))
            t.setDaemon(True)
            t.start()
            ths.append(t)
        for t in ths:
            t.join()

    # 需要在一次执行过程中检查所有用户的库存信息
    # 对需要执行任务的房间，建立价格调整任务
    def exec(self):
        new_service_info = db.system.get_service_info(self.service_type)
        if new_service_info is None:
            logger.warning('got None new_service_info!')
            return
        if new_service_info['state'] != SystemDB.SERVICE_STOP and Constants.RUN_WITH_SYS_TASK_LOG:
            logger.warning(f"[ stock_check ] ( SKIP )")
            self.save(state=SystemDB.SERVICE_STOP)
            return
        self.save(state=SystemDB.SERVICE_RUNNING)
        if Constants.RUN_WITH_SYS_TASK_LOG:
            logger.warning(f"[ stock_check ]")

        self.start_branch()
        self.save(state=SystemDB.SERVICE_STOP)

# T-O-D-O: 1. fix [x] 前端点击无反应
#  2.
#  3. [x] fix 前端计划计数
#  4. [x] fix got empty day
#  5. [x] 添加简便用法
#  6. [x] fix 有些任务不显示

# TODO: fix 后端根据索引而不是id改变价格
