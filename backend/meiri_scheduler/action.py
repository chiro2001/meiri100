import asyncio
import logging
import random

from data_apis.api import API
# from meiri_daemon.daemon import daemon, DaemonBean
from meiri_account.action import get_tasks
from meiri_database.database import db
from meiri_database.tools import *
from utils.time_formats import get_date_today


class Action:
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        self.action_type = 'base'
        self.uid = kwargs.get('uid')
        # if self.uid is None:
        #     logger.warning('git empty uid')

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.action_type = state.get('action_type', self.action_type)
        self.args = state.get('args', self.args)
        self.kwargs = state.get('kwargs', self.kwargs)
        self.uid = state.get('uid')

    def get_self_name(self):
        return f"#{self.__class__.__name__}{str(self.__hash__())[-4:]}"


class ActionSimpleRun(Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_type = 'simple_run'
        self.running = False
        # logger.warning(f"constructor: {__class__.__name__}")

    def __setstate__(self, state):
        super(ActionSimpleRun, self).__setstate__(state)

    def exec(self):
        logger.info(f"#{str(self.__hash__())[-4:]}, self.args: {self.args}, self.kwargs: {self.kwargs}")
        # if not self.running:
        #     # logger.info(self.__getstate__())
        #     logger.info(f"#{str(self.__hash__())[-4:]}, self.args: {self.args}, self.kwargs: {self.kwargs}")
        #     self.running = True
        # else:
        #     print('.', end='')


# class ActionPriceAdjust(Action):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.action_type = 'adjust_price'
#         self.target_price = kwargs.get('price', None)
#         if self.target_price is None:
#             logger.warning('got empty price!')
#             self.target_price = 0
#         self.item_id = kwargs.get('item_id')
#         if self.item_id is None:
#             logger.warning('got empty item_id')
#             self.item_id = 0
#         self.periodDesc: str = kwargs.get('periodDesc')
#         self.roomName: str = kwargs.get('roomName')
#         self.day: int = kwargs.get('day')
#         self.date: str = kwargs.get('date')
#
#     def exec(self):
#         logger.info(f'adjusting price to {self.target_price}')
#         if self.uid is None:
#             raise MeiRiError(f"Empty uid")
#         daemon_bean: DaemonBean = daemon.get_daemon(self.uid, init_new=True)
#         api: API = daemon_bean.get_api()
#         resp = api.ktv.update_price(item_id=self.item_id, price=self.target_price)
#         logger.debug(f'{self.get_self_name()}: resp = {resp}')
#
#     def __setstate__(self, state: dict):
#         super(ActionPriceAdjust, self).__setstate__(state)
#         self.target_price = state.get('target_price')
#         self.item_id = state.get('item_id')
#         self.periodDesc = state.get('periodDesc')
#         self.roomName = state.get('roomName')
#         self.day: int = state.get('day')
#         self.date: str = state.get('date')
#
#
# # 按照相对值改变价格
# class ActionPriceAdjustRelative(ActionPriceAdjust):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.action_type = 'adjust_price_relative'
#         del self.target_price
#         self.price_relative = kwargs.get('price_relative', None)
#         if self.price_relative is None:
#             logger.warning('got empty price!')
#             self.price_relative = 0
#
#     def exec(self):
#         logger.info(f'adjusting price by {self.price_relative}')
#         if self.uid is None:
#             raise MeiRiError(f"Empty uid")
#         d: DaemonBean = daemon.get_daemon(self.uid, init_new=True)
#         api: API = d.get_api()
#         # 获取当前价格
#         date_today = get_date_today()
#         changed: bool = False
#         if d.reserve_table is None:
#             d.reserve_table = {date_today: api.ktv.get_reserve_table(date=date_today)}
#             changed = True
#         if date_today not in d.reserve_table or True:
#             d.reserve_table[date_today] = api.ktv.get_reserve_table(date=date_today)
#             changed = True
#         if changed:
#             d.save('reserve_table')
#         if d.reserve_table is None:
#             d.reserve_table = {}
#         # 找到当前价格数据
#         if date_today not in d.reserve_table:
#             logger.warning(f'Cannot find reserve table now!')
#             return
#         target_room_item = None
#         for period_list in d.reserve_table[date_today]['periodList']:
#             if period_list['periodDesc'] == self.periodDesc:
#                 if self.roomName in period_list['roomMapItemEntry']:
#                     for room_item in period_list['roomMapItemEntry'][self.roomName]:
#                         if room_item['itemId'] == self.item_id:
#                             target_room_item = room_item
#                             break
#         if target_room_item is None:
#             logger.warning(f'Cannot find target room item now!')
#             return
#         target_price = target_room_item['price'] + self.price_relative
#         resp = api.ktv.update_price(item_id=self.item_id, price=target_price)
#         logger.info(f'updating price by {self.price_relative}, to {target_price}')
#         logger.debug(f'{self.get_self_name()}: resp = {resp}')
#
#     def __setstate__(self, state: dict):
#         super(ActionPriceAdjustRelative, self).__setstate__(state)
#         self.price_relative = state.get('price_relative')


meiri_get_tasks_pool = {}


# 如果一个管理账号存在被管理账号，
# 就选择一个账号检查有无任务
class ActionMeiriGetTasksCycle(Action):
    def __init__(self, uid: int = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = uid
        self.action_type = 'meiri_get_tasks'

    def __setstate__(self, state: dict):
        super(ActionMeiriGetTasksCycle, self).__setstate__(state)
        self.uid = state.get('uid', self.uid)

    def exec(self):
        if self.uid is None:
            logger.error(f"got none uid!")
            return
        if self.uid in meiri_get_tasks_pool:
            logger.warning(f"meiri_get_task[{self.uid}] running!")
            return
        meiri_get_tasks_pool[self.uid] = True
        try:
            accounts = db.account.get_by_uid(self.uid)
            if len(accounts) == 0:
                raise RuntimeError
            # 随机选择一个用户
            account = random.choice(accounts)
            logger.info(f"using {account}")
            api = API.from_username_password(username=account['username'], password=account['password']).init_data()
            if api.cookies is None:
                logger.error(f"meiri_get_tasks uid: {self.uid} run failed (username {account['username']})")
                db.log.log(self.uid, logging.ERROR, f"用户 {account['username']} 登录失败！无法检查任务列表情况！")
                raise RuntimeError
            tasks = api.meiri.get_tasks()
            logger.info(f"got tasks: {tasks}")
            if len(tasks) > 0:
                # 来活了！
                db.log.log(self.uid, logging.DEBUG, f"用户 {account['username']} 获取到 {len(tasks)} 个任务！")
                loop = asyncio.get_event_loop()
                loop.run_until_complete(get_tasks(accounts, tasks))
            else:
                db.log.log(self.uid, logging.DEBUG, f"用户 {account['username']} 获取到空任务列表。")
        except RuntimeError:
            pass
        except Exception as e:
            logger.error(f"meiri_get_tasks error {e.__class__.__name__} {str(e)[32:]}")
        del meiri_get_tasks_pool[self.uid]


action_types = {
    'base': Action,
    'simple_run': ActionSimpleRun,
    'meiri_get_tasks': ActionMeiriGetTasksCycle
    # 'adjust_price': ActionPriceAdjust,
    # 'adjust_price_relative': ActionPriceAdjustRelative
}

# 能够让用户操作的Action
action_names_available = {
    # 'adjust_price': "调整价格动作",
    # 'adjust_price_relative': "调整相对价格动作"
}

action_desc = {
    # 'adjust_price': "利用此动作可以调整价格到目标价格，设定价格上调、下调目标。",
    # 'adjust_price_relative': "利用此动作可以依照当前价格调整价格上浮/下调。"
}

action_names = {
    'base': "基础action",
    'simple_run': "简单action",
    # 'adjust_price': "调整价格工作",
    # 'adjust_price_relative': "调整相对价格动作"
}
