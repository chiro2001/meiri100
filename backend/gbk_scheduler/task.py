from gbk_scheduler.action import *
import apscheduler.jobstores.base
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers import interval, cron, date
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from gbk_database.config import Constants
from gbk_database.database import db
from gbk_scheduler.trigger import StockTrigger
from utils.formats import task_data_encode, task_data_decode
from utils.make_result import limit_list
from utils.logger import logger
from gbk_exceptions import *

scheduler = BackgroundScheduler(**Constants.SCHEDULE_CONFIG)

trigger_types = {
    'interval': IntervalTrigger,
    'date': DateTrigger,
    'cron': CronTrigger,
    'stock': StockTrigger
}

trigger_names_available = {
    'interval': "间隔触发器",
    'date': "单次触发器",
    'stock': "库存触发器"
}

trigger_names_time = ['interval', 'date', 'cron']

trigger_names = {
    'interval': "间隔触发器",
    'date': "单次触发器",
    "cron": 'Cron触发器',
    'stock': "库存触发器"
}

trigger_desc = {
    'interval': "能够依照固定时间间隔执行动作。",
    'date': "能在指定时间点执行动作。",
    "cron": '使用Cron表达式实现复杂的执行规则。',
    'stock': "根据实时的库存变化情况来执行动作"
}


def trigger_get_info(trigger_type: str):
    instance = trigger_types[trigger_type]()
    instance_data = instance.__getstate__()
    instance_data = task_data_encode(instance_data)
    # logger.info(f'{trigger_type} data: {instance_data}')
    return instance_data


def action_get_info(action_type: str):
    instance = action_types[action_type]()
    instance_data = instance.__getstate__()
    return instance_data


trigger_args = {
    'interval': {
        'version': {'value': 2, 'editable': False},
        'timezone': {'value': 'timezone|Asia/Shanghai', 'editable': False},
        'start_date': {'value': trigger_get_info('interval').get('start_date'), 'type': 'datetime', 'editable': True},
        'end_date': {'value': trigger_get_info('interval').get('end_date'), 'type': 'datetime', 'editable': True},
        'interval': {'value': trigger_get_info('interval').get('interval'), 'type': 'timedelta', 'editable': True},
        'jitter': {'value': None, 'editable': False}
    },
    'date': {
        'version': {'value': 1, 'editable': False},
        'run_date': {'value': trigger_get_info('date').get('run_date'), 'type': 'datetime', 'editable': True}
    },
    "cron": {
        'version': {'value': 2, 'editable': False},
        'timezone': {'value': 'timezone|Asia/Shanghai', 'editable': False},
        'start_date': {'value': trigger_get_info('cron').get('start_date'), 'type': 'datetime', 'editable': True},
        'end_date': {'value': trigger_get_info('cron').get('end_date'), 'type': 'datetime', 'editable': True},
        # 这个咋弄啊
        'fields': {'value': [], 'editable': False},
        'jitter': {'value': None, 'editable': False}
    },
    "stock": {
        'trigger_type': {'value': 'stock', 'editable': False},
        'start_date': {'value': trigger_get_info('stock').get('start_date'), 'type': 'datetime', 'editable': True},
        'end_date': {'value': trigger_get_info('stock').get('end_date'), 'type': 'datetime', 'editable': True},
        'value': {'value': trigger_get_info('stock').get('value'), 'editable': True},
        'operator': {'value': '>', 'type': 'select',
                     'options': {
                         '>': '大于', '<': '小于',
                         '>=': '大于等于', '<=': '小于等于',
                         # 如果可以选择大于等于/小于等于的话，会有恢复task重复情况
                         '==': '等于', '!=': '不等于'
                     },
                     'editable': True}
    }
}

action_args = {
    'adjust_price': {
        'action_type': {'value': 'adjust_price', 'editable': False},
        'args': {'value': [], 'editable': False},
        'kwargs': {'value': {}, 'editable': False},
        'uid': {'value': None, 'editable': False},
        'item_id': {'value': 0, 'editable': True},
        'target_price': {'value': 0, 'editable': True},
        'periodDesc': {'value': None, 'editable': False},
        'roomName': {'value': None, 'editable': False}
    },
    'adjust_price_relative': {
        'action_type': {'value': 'adjust_price_relative', 'editable': False},
        'args': {'value': [], 'editable': False},
        'kwargs': {'value': {}, 'editable': False},
        'uid': {'value': None, 'editable': False},
        'item_id': {'value': 0, 'editable': True},
        'day': {'value': None, 'editable': False},
        'date': {'value': None, 'editable': False},
        'price_relative': {'value': 0, 'editable': True},
        'periodDesc': {'value': None, 'editable': False},
        'roomName': {'value': None, 'editable': False}
    },
    'base': {
        'action_type': {'value': 'base', 'editable': False},
        'args': {'value': [], 'editable': False},
        'kwargs': {'value': {}, 'editable': False},
        'uid': {'value': None, 'editable': False},
    },
    'simple_run': {
        'action_type': {'value': 'simple_run', 'editable': False},
        'args': {'value': [], 'editable': False},
        'kwargs': {'value': {}, 'editable': False},
        'uid': {'value': None, 'editable': False},
        'running': {'value': False, 'editable': False},
    },
}


def get_trigger_name_from_dict(trigger: dict):
    if 'data' in trigger:
        trigger = trigger['data']
    if 'trigger_type' in trigger:
        return trigger['trigger_type']
    return 'interval' if 'interval' in trigger else 'date' if 'run_date' in trigger else 'cron'


def get_trigger_name_from_instance(trigger):
    return 'interval' if isinstance(trigger, IntervalTrigger) \
        else 'date' if isinstance(trigger, DateTrigger) \
        else 'cron' if isinstance(trigger, CronTrigger) \
        else 'stock'


class Task:
    def __init__(self, tid: int = None, name: str = None, triggers: list = None, actions: list = None):
        self.triggers, self.actions = triggers if triggers is not None else [], actions if actions is not None else []
        # 全部参数都是空的时候不拿新的 tid
        self.tid = tid if (not (tid is None and name is None and
                                triggers is None and actions is None)) else db.task_manager.get_next_tid()
        if self.tid is None:
            self.tid = db.task_manager.get_current_tid()
        self.task_name = name if name is not None else self.get_name_by_actions()
        self._name = name
        self.jobs = []

    def get_triggers_by_class(self, classobj):
        return [trigger for trigger in self.triggers if isinstance(trigger, classobj)]

    def get_actions_by_class(self, classobj):
        return [action for action in self.actions if isinstance(action, classobj)]

    def get_name_by_actions(self):
        return '_'.join(
            [f'{action.action_type}#{("H" + str(action.__hash__())[-4:]) if self.tid is None else self.tid}' for action
             in self.actions])

    def enable(self):
        if len(self.jobs) > 0:
            self.disable()
        # 保证每一个trigger都会触发所有action
        for i in range(len(self.actions)):
            for j in range(len(self.triggers)):
                trigger_the_args = self.triggers[j].__getstate__()
                if 'version' in trigger_the_args:
                    del trigger_the_args['version']
                if 'trigger_type' not in trigger_the_args or \
                        ('trigger_type' in trigger_the_args and trigger_the_args['trigger_type'] in trigger_names_time):
                    job = scheduler.add_job(self.actions[i].exec, self.triggers[j])
                    # logger.warning(f'trigger: {self.triggers[j]}')
                    # logger.warning(f'trigger_args: {trigger_args}')
                    # logger.warning(f'job: {job}')
                    self.jobs.append(job)
                else:
                    logger.warning(f'trigger that need not a scheduler: {trigger_the_args}')
        # logger.warning(f'enable jobs: {self.jobs}')
        return self

    def disable(self):
        # logger.warning(f'disable jobs: {self.jobs}')
        for job in self.jobs:
            # logger.warning(f'removing job: {job}')
            try:
                scheduler.remove_job(job_id=job.id)
            except apscheduler.jobstores.base.JobLookupError:
                # raise GBKError("Cannot remove job!")
                logger.warning("Cannot remove job!")
            # scheduler.remove_job(job_id=job.id)
        self.jobs = []
        return self

    def add_trigger(self, trigger):
        self.triggers.append(trigger)
        return self

    def add_action(self, action):
        self.actions.append(action)
        if self._name is None:
            self.task_name = self.get_name_by_actions()
        return self

    def get_task_data(self):
        return self.__getstate__()

    def set_task_data(self, data: dict):
        self.__setstate__(data)

    @staticmethod
    def from_task_data(data: dict):
        task = Task()
        task.set_task_data(data)
        return task

    def __getstate__(self):
        return {
            'triggers': [trigger.__getstate__() for trigger in self.triggers],
            'actions': [action.__getstate__() for action in self.actions],
            'task_name': self.task_name,
            'tid': self.tid
        }

    def __setstate__(self, state: dict):
        if 'triggers' in state:
            self.triggers = [trigger_types[get_trigger_name_from_dict(trigger)]() for trigger in state['triggers']]
            for i in range(len(state['triggers'])):
                d = state['triggers'][i]
                if 'data' in d:
                    d = d['data']
                data = task_data_decode(d)
                # logger.warning(f"self.triggers[i]: {self.triggers[i]}, data: {data}, state['triggers'][i]: {state['triggers'][i]}")
                data_default = self.triggers[i].__getstate__()
                # logger.warning(f'data        : {data}')
                # logger.warning(f'data_default: {data_default}')
                data_default.update(data)
                self.triggers[i].__setstate__(data_default)
        if 'actions' in state:
            self.actions = [action_types[action['data']['action_type']]()
                            if 'data' in action else action_types[action['action_type']]()
                            for action in state['actions']]
            for i in range(len(state['actions'])):
                self.actions[i].__setstate__(task_data_decode(
                    state['actions'][i]['data'] if 'data' in state['actions'][i] else state['actions'][i]))
        if 'task_name' in state:
            self.task_name = state['task_name']
        else:
            self.task_name = self.get_name_by_actions()
        if 'tid' in state:
            if state['tid'] is not None:
                self.tid = state['tid']
            else:
                self.tid = db.task_manager.get_next_tid()
        return self

    def __repr__(self):
        return str(self.__getstate__())


class TaskManager:
    """
    单个用户的任务管理器
    """

    def __init__(self, uid: int):
        self.uid = uid
        self.tasks = []
        self.enabled = False
        self.load()

    def find_task_by_tid(self, tid: int):
        for task in self.tasks:
            if task.tid == tid:
                return task
        return None

    def find_task_by_trigger_class(self, classobj):
        return [task for task in self.tasks if len(task.get_triggers_by_class(classobj)) > 0]

    def add_task(self, task: Task):
        # logger.warning(f'before insert {self}, {task}')
        # 保证唯一tid
        task_old = self.find_task_by_tid(task.tid)
        if task_old is not None:
            if not self.remove_task(task_old.tid):
                raise GBKError("Cannot remove task!")
        if self.enabled:
            task.enable()
        self.tasks.append(task)
        self.save()
        # logger.warning(f'after insert {self}')

    def remove_task(self, tid: int) -> bool:
        """
        移除一个任务
        :param tid:
        :return: 移除成功与否
        """
        target_index = None
        for i in range(len(self.tasks)):
            if self.tasks[i].tid == tid:
                target_index = i
                break
        if target_index is None:
            return False
        # logger.warning(
        #     f'will disable {self.tasks[target_index].tid} job: {self.tasks[target_index].jobs}, {self.tasks[target_index]}')
        self.tasks[target_index].disable()
        del self.tasks[target_index]
        self.save()
        return True

    def enable_all(self):
        if self.enabled:
            return
        [task.enable() for task in self.tasks]
        self.enabled = True

    def disable_all(self):
        if not self.enabled:
            return
        [task.disable() for task in self.tasks]
        self.enabled = False

    def get_tasks_data(self, offset: int = None, limit: int = None):
        data = self.__getstate__(offset=offset, limit=limit)
        data = task_data_encode(data)
        return data

    def set_tasks_data(self, data: dict):
        data = task_data_decode(data)
        self.__setstate__(data)

    def save(self):
        data = self.get_tasks_data()
        db.task_manager.save(self.uid, data)
        # Fix: 只会运行一个任务
        # self.set_tasks_data(data)

    def load(self):
        data = db.task_manager.load(self.uid)
        if data is not None:
            task_data_decode(data)

    def erase(self):
        # logger.warning(f'erasing {self.uid}')
        db.task_manager.remove(self.uid)

    def empty(self) -> bool:
        # logger.warning(f'empty? {len(self.tasks) == 0}')
        return len(self.tasks) == 0

    def __getstate__(self, offset: int = None, limit: int = None):
        # print('tasks', self.tasks, [task.__getstate__() for task in self.tasks])
        return {
            'enabled': self.enabled,
            'tasks': limit_list([task.__getstate__() for task in self.tasks], offset=offset, limit=limit)
        }

    def __setstate__(self, state: dict):
        # self.enabled = state.get('enabled', False)
        self.enabled = False
        self.tasks = [Task.from_task_data(task) for task in state.get('tasks', [])]
        # logger.warning(f'state: {state}, TaskManager tasks: {self.tasks}')
        if self.enabled:
            self.enable_all()
        return self

    def __repr__(self):
        return str(self.__getstate__())
