from gbk_scheduler.task import *
from gbk_system.action import ActionCycle
from gbk_system.task import sys_tasks


class TaskPool:
    """
    管理所有用户的任务池子
    """

    def __init__(self):
        self.pool = {}
        self.enabled = False
        self.load_all()

    def enable(self):
        if self.enabled:
            return
        self.enabled = True
        for uid in self.pool:
            self.pool[uid].enable_all()

    def disable(self):
        if not self.enabled:
            return
        self.enabled = False
        for uid in self.pool:
            self.pool[uid].disable_all()

    def add_task(self, uid: int, task: Task) -> int:
        if uid not in self.pool:
            self.pool[uid] = TaskManager(uid=uid)
            if self.enabled:
                self.pool[uid].enable_all()
        # logger.warning(f'will done {self.pool[uid]}')
        self.pool[uid].add_task(task)
        # logger.warning(f'add done {self.pool[uid]}')
        return task.tid if task.tid is not None else -1

    def remove_task(self, uid: int, tid: int) -> bool:
        if uid not in self.pool:
            return False
        res = self.pool[uid].remove_task(tid)
        if self.pool[uid].empty():
            self.pool[uid].disable_all()
            self.pool[uid].erase()
            del self.pool[uid]
        return res

    def get_manager(self, uid: int):
        # print(self.pool)
        return self.pool[uid] if uid in self.pool else None

    def __getstate__(self):
        state = {
            'enabled': self.enabled,
            'pool': {}
        }
        for k in self.pool:
            state['pool'][k] = self.pool[k].__getstate__()
        return state

    def __setstate__(self, state: dict):
        # self.enabled = state.get('enabled', False)
        self.enabled = False
        self.pool = state.get('pool', {})
        # logger.warning(f'pool: {self.pool}')
        for k in self.pool:
            self.pool[k] = TaskManager(self.pool[k].get('uid', -1)).__setstate__(self.pool[k]['data'])
        return self

    def load_all(self):
        all_data = db.task_manager.get_all()
        # logger.warning(f'all_data: {all_data}')
        self.__setstate__({
            'pool': all_data
        })

    def __repr__(self):
        return str(self.__getstate__())


class SystemTaskPool:
    """
    管理系统任务
    """

    def __init__(self):
        self.sys_tasks = {task: sys_tasks[task] for task in sys_tasks if sys_tasks[task] is not None}

    def enable(self):
        [self.sys_tasks[task].enable() for task in self.sys_tasks if isinstance(self.sys_tasks[task], Task)]

    def disable(self):
        [self.sys_tasks[task].disable() for task in self.sys_tasks if isinstance(self.sys_tasks[task], Task)]

    def update_uid(self, uid: int):
        _ = [[action.update_uid(uid) for action in self.sys_tasks[task].actions if isinstance(action, ActionCycle)]
             for task in self.sys_tasks if isinstance(self.sys_tasks[task], Task)]


task_pool = TaskPool()
task_sys_pool = SystemTaskPool()
