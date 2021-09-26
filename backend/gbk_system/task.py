from apscheduler.triggers.interval import IntervalTrigger

from gbk_scheduler.task import Task, Constants
from gbk_system.action import ActionFetchTradeData, ActionFetchFlowData, ActionBackupData, ActionUpdateStockData, \
    ActionRoomStockCheck

sys_tasks_delays = Constants.RUN_TASKS_DELAYS

sys_tasks = {
    'sys_trade_data': Task(name="sys_trade_data",
                           actions=[ActionFetchTradeData(), ],
                           triggers=[IntervalTrigger(seconds=sys_tasks_delays[
                               'sys_trade_data']), ]) if 'sys_trade_data' not in Constants.RUN_DISMISS_TASK else None,
    'sys_flow_data': Task(name="sys_flow_data",
                          actions=[ActionFetchFlowData(), ],
                          triggers=[IntervalTrigger(seconds=sys_tasks_delays[
                              'sys_flow_data']), ]) if 'sys_flow_data' not in Constants.RUN_DISMISS_TASK else None,
    'sys_backup': Task(name="sys_backup",
                       actions=[ActionBackupData(), ],
                       triggers=[IntervalTrigger(seconds=sys_tasks_delays[
                           'sys_backup']), ]) if 'sys_backup' not in Constants.RUN_DISMISS_TASK else None,
    'user_room_stock': Task(name="user_room_stock",
                            actions=[ActionUpdateStockData(), ],
                            triggers=[IntervalTrigger(seconds=sys_tasks_delays[
                                'user_room_stock']), ]) if 'user_room_stock' not in Constants.RUN_DISMISS_TASK else None,
    'user_stock_check': Task(name="user_stock_check",
                             actions=[ActionRoomStockCheck(), ],
                             triggers=[IntervalTrigger(seconds=sys_tasks_delays[
                                 'user_stock_check']), ]) if 'user_stock_check' not in Constants.RUN_DISMISS_TASK else None,
}

# TODO: fix: 遇到不可用的cookies

if __name__ == '__main__':
    ActionBackupData().exec()
