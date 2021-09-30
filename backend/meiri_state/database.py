from meiri_database.tools import *


class MeiriStateDB(BaseDB):
    def __init__(self, d):
        super().__init__(d, 'state')

    # def increase_fetched_task(self, uid: int):
    #     fetched_task = self.get_fetched_task(uid=uid)
    #     auto_time_update(self.col, {'uid': uid}, {'fetched_task': fetched_task + 1})

    def record_fetched_task(self, uid: int, username: str, task: dict):
        auto_time_insert(self.col, {'uid': uid, "username": username, 'task': task})

    def get_fetched_task(self, uid: int, start=None, end=None) -> list:
        # data = find_one(self.col, {'uid': uid})
        filter_dict = {'uid': uid}
        if start is not None:
            filter_dict.update({'updated_at': {'$lte': start}})
        if end is not None:
            filter_dict.update({'updated_at': {'$gte': start}})
        return find_many(self.col, filter_dict)

    def get_fetched_task_number(self, uid: int, start=None, end=None) -> int:
        # data = find_one(self.col, {'uid': uid})
        filter_dict = {'uid': uid}
        if start is not None:
            filter_dict.update({'updated_at': {'$lte': start}})
        if end is not None:
            filter_dict.update({'updated_at': {'$gte': start}})
        data = int(self.col.count_documents(filter_dict))
        if data is None:
            return 0
        return data
