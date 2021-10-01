import asyncio
import logging
import random
import time

from data_apis.api import API
from meiri_database.database import db
# from meiri_scheduler.action import Action
from utils.logger import logger

task_ = {
    'order_title': '#十一假期 难得的假期时光你会如何度过呢？戳视频，“他们”偷偷和我说了一句什么心里话？',
    'order_time': '09/29 17:18',
    'php_remark': '',
    'title': '微信视频号-作品点赞',
    'residue_num': 47690,
    'limit_time': '2021-10-01 18:07:00.0',
    'account_id': 93982,
    'account_name': '四月1744',
    'zb_groupid': '',
    'task_price': 50,
    'task_type': '5',
    'order_id': 314,
    'order_type': '3',
    'site_name': '微信视频号',
    'task_type_name': '作品点赞'
}


async def get_task(account: dict, task: dict, retry: int = 5):
    api: API = API.from_username_password(username=account['username'], password=account['password'])
    for t in range(retry):
        api.init_data()
        if api.cookies is not None:
            break
        time.sleep(1)
    if api.cookies is None:
        db.log.log(account['uid'], logging.ERROR, f"用户 {account['username']} 尝试登录失败！无法获取任务！")
        return
    get_task_ok: bool = False
    resp: dict = None
    for t in range(retry):
        resp = api.meiri.get_task(task)
        if 'code' in resp and resp['code'] == 100 or resp['code'] is None:
            get_task_ok = True
            break
    if get_task_ok:
        # db.state.increase_fetched_task(account['uid'])
        db.state.record_fetched_task(account['uid'], task)
        db.log.log(account['uid'], logging.INFO, f"用户 {account['username']} "
                                                 f"获取任务 {task.get('title')}, "
                                                 f"获得积分 {task.get('task_price')}")
        logger.info(f"get_task for {account['username']} done!")
    else:
        logger.error(f"get_task failed for {account['username']}! {resp}")
        db.log.log(account['uid'], logging.ERROR, f"用户 {account['username']} "
                                                  f"获取任务 {task.get('title')} 错误: "
                                                  f"{resp['msg'] if 'msg' in resp else resp}")


async def get_tasks(accounts: list, tasks: list):
    task_pool = {}
    for account in accounts:
        if not account['enabled']:
            continue
        for task in tasks:
            task_pool[f'{account["username"]}_{task["order_id"]}'] = get_task(account, task)
    for key in task_pool:
        await task_pool[key]
