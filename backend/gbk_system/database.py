from gbk_database.tools import *


class SystemDB(DataDB):
    SERVICE_START = 'service_start'
    SERVICE_RUNNING = 'service_running'
    SERVICE_STOP = 'service_stop'

    def __init__(self, d):
        super().__init__(d, 'system')
        # 后台进程相关
        self.col_service = self.d.service

    # 更新service运行状态, data为下一次运行数据
    def update_service_state(self, service_type: str, state: str, data: dict = None):
        auto_time_update(self.col_service, {'service_type': service_type},
                         {'state': state, 'data': data}, insert_if_necessary=True)

    # 获取service状态
    def get_service(self, service_type: str):
        res = self.get_service_info(service_type)
        return res if res is None else res.get('data')

    # 获取service信息
    def get_service_info(self, service_type: str):
        res = find_one(self.col_service, {'service_type': service_type})
        return res

    def load_key(self, uid: int, key, data_type: str = 'base'):
        return self.load(uid, data_type=data_type, filter_={'data.key': key})

    def save_key(self, uid: int, key, data: dict, data_type: str = 'base'):
        if not isinstance(data, dict):
            logger.error(f'Must be dict data')
            return
        data.update({'key': key})
        return self.save(uid, data, data_type=data_type, filter_={'data.key': key})


class SpiderDB(DataKeyDB):
    def __init__(self, d):
        super().__init__(d, "spider")
