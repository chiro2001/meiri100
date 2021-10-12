import asyncio
import logging
import random

from data_apis.api import API
# from meiri_daemon.daemon import daemon, DaemonBean
from meiri_account.action import get_tasks
from meiri_database.database import db
from meiri_database.tools import *
from utils.email_sender import send_email
from utils.proxies import get_proxy, get_proxy_2
from utils.time_formats import get_date_today, get_date_yesterday


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

accounts_cookies = {}


# 如果一个管理账号存在被管理账号，
# 就选择一个账号检查有无任务
class ActionMeiriGetTasksCycle(Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = kwargs.get('uid', None)
        self.action_type = 'meiri_get_tasks'

    def __setstate__(self, state: dict):
        super(ActionMeiriGetTasksCycle, self).__setstate__(state)
        self.uid = state.get('uid', self.uid)

    async def exec_one(self, proxy: str = None, proxy_list: list = None):
        try:
            accounts = db.account.get_by_uid(self.uid)
            for username in accounts_cookies:
                for i in range(len(accounts)):
                    if accounts[i].get('username') == username:
                        accounts[i]['cookies'] = accounts_cookies[username]
            if len(accounts) == 0:
                # del meiri_get_tasks_pool[self.uid]
                return
            # 随机选择一个用户
            account = random.choice(accounts)
            logger.debug(
                f"using {proxy} {account.get('username')} cookies: {account.get('username') in accounts_cookies}")
            if account.get('username') in accounts_cookies:
                api = API.from_cookies(accounts_cookies[account['username']])
            else:
                api = API.from_username_password(username=account['username'], password=account['password']) \
                    .init_data(proxy=proxy)
                accounts_cookies[account['username']] = api.cookies
            if api.cookies is None:
                logger.error(f"meiri_get_tasks uid: {self.uid} run failed (username {account['username']})")
                db.log.log(self.uid, logging.ERROR, f"用户 {account['username']} 登录失败！无法检查任务列表情况！")
                # del meiri_get_tasks_pool[self.uid]
                return
            tasks = api.meiri.get_tasks(proxy=proxy)
            if len(tasks) > 0:
                logger.info(f"got tasks: {tasks}")
                # 来活了！
                db.log.log(self.uid, logging.INFO, f"用户 {account['username']} 获取到 {len(tasks)} 个任务！"
                                                   f"分配给 {len(accounts)} 个账号...")
                # try:
                #     loop = asyncio.get_event_loop()
                # except RuntimeError as e:
                #     new_loop = asyncio.new_event_loop()
                #     asyncio.set_event_loop(new_loop)
                #     loop = asyncio.get_event_loop()
                # loop.run_until_complete(get_tasks(accounts, tasks))
                # await get_tasks(accounts, tasks, proxy)
                if proxy_list is None:
                    await get_tasks(accounts, tasks, proxy=proxy)
                else:
                    await get_tasks(accounts, tasks, proxy_list=proxy_list)
            else:
                # db.log.log(self.uid, logging.DEBUG, f"用户 {account['username']} 获取到空任务列表。")
                pass
        except Exception as e:
            logger.error(f"meiri_get_tasks error {e.__class__.__name__} {str(e)[:100]}")
        # del meiri_get_tasks_pool[self.uid]

    def exec(self):
        # logger.warning(f"Run ActionMeiriGetTasksCycle()!")
        if self.uid is None:
            logger.error(f"got none uid!")
            return
        # if self.uid in meiri_get_tasks_pool:
        #     logger.warning(f"meiri_get_task[{self.uid}] running!")
        #     return
        # meiri_get_tasks_pool[self.uid] = True
        # 获取到 代理列表
        # proxies_pool = [None, *[get_proxy().get("proxy") for _ in range(Constants.PROXY_POOL_SIZE)], *get_proxy_2()]
        proxies_pool = [None, *[get_proxy().get("proxy") for _ in range(Constants.PROXY_POOL_SIZE)]]
        logger.debug(f"got proxies: {proxies_pool}")
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            loop = asyncio.get_event_loop()

        async def run_all(tasks: list, args_list: list, kwargs_list: list):
            # task_pool = [None for _ in range(len(tasks))]
            task_pool = []
            for i in range(len(tasks)):
                # task_pool[i] = tasks[i](*(args_list[i] if len(args_list) > i else []),
                #                         **(kwargs_list[i] if len(kwargs_list) > i else {}))20log
                task_pool.append(tasks[i](*(args_list[i] if len(args_list) > i else []),
                                          **(kwargs_list[i] if len(kwargs_list) > i else {})))
            for task in task_pool:
                await task

        loop.run_until_complete(
            run_all([self.exec_one for _ in range(len(proxies_pool))],
                    [[] for proxy in proxies_pool],
                    [{"proxy_list": proxies_pool, "proxy": p} for p in proxies_pool]))


class ActionMeiriReport(Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = kwargs.get('uid', None)
        self.action_type = 'meiri_report'

    def __setstate__(self, state: dict):
        super(ActionMeiriReport, self).__setstate__(state)
        self.uid = state.get('uid', self.uid)

    def exec(self):
        # logger.warning(f"Run {self.__class__.__name__}()!")
        if self.uid is None:
            logger.error(f"got none uid!")
            return
        user = db.user.get_by_uid(self.uid)
        email = user.get('profile', {}).get('contact', {}).get('email', None)
        if email is None:
            logger.warning(f"uid {self.uid} has empty email!")
            return
        config = db.sync.find_by_uid(self.uid)
        # 默认开启
        enabled = True
        if config is not None:
            if not config.get('enable_email', True):
                enabled = False
        if not enabled:
            return
        user = db.user.get_by_uid(self.uid)
        # 获取统计信息, 1d
        username_tasks = db.state.get_fetched_task(uid=self.uid, start=get_date_yesterday())
        tasks = [ut.get('task', {}) for ut in username_tasks]
        tasks_info = [f"用户: {ut.get('username')}; 标题: {ut.get('task', {}).get('order_title')[:10]}; "
                      f"时间: {ut.get('task', {}).get('order_time')}; "
                      f"标题: {ut.get('task', {}).get('title')}" for ut in username_tasks]
        content = Constants.REPORT_EMAIL_CONTENT.format(
            number=len(tasks),
            content='\n'.join(tasks_info)
        )
        send_email(sender=Constants.EMAIL_SENDER,
                   send_to=email,
                   password=Constants.EMAIL_SMTP_PASSWORD,
                   text=content,
                   title_from=Constants.USERS_OWNER_USERNAME,
                   title_to=f'亲爱的用户 {user.get("username")}',
                   subject=Constants.REPORT_EMAIL_TITLE.format(date=get_date_today()))
        db.log.log(self.uid, level=logging.INFO, text=f"向您的邮箱({email})发送了今日({get_date_today()})的报告邮件。")


action_types = {
    'base': Action,
    'simple_run': ActionSimpleRun,
    'meiri_get_tasks': ActionMeiriGetTasksCycle,
    'meiri_report': ActionMeiriReport
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
