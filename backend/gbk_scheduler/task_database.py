from gbk_database.tools import *


class TaskManagerDB(BaseDB):
    def __init__(self, d):
        super().__init__(d, 'task_manager')
        init_sequence_id(self.d.task_tid, "cnt_tid")

    def get_next_tid(self):
        return get_next_id(self.d.task_tid, "cnt_tid")

    def get_current_tid(self):
        return get_current_id(self.d.task_tid, "cnt_tid")

    def get_raw(self, uid: int) -> dict:
        result = self.col.find_one({'uid': uid}, {'_id': False})
        result = dict_remove_empty(result)
        # if result is None:
        #     return
        # # ~~可能是start_date不同导致的~~
        # if 'data' in result and 'tasks' in result['data']:
        #     for i in range(len(result['data']['tasks'])):
        #         for j in range(len(result['data']['tasks'][i]['triggers'])):
        #             if 'start_date' in result['data']['tasks'][i]['triggers'][j]:
        #                 del result['data']['tasks'][i]['triggers'][j]['start_date']
        # logger.warning(f'got uid:{uid} from db: {result}')
        return result

    def save(self, uid: int, data: dict):
        # print('manager db saving', data)
        if self.get_raw(uid) is None:
            self.col.insert_one({'uid': uid, 'data': data})
        else:
            self.col.update_one({'uid': uid}, {'$set': {'data': data}})

    def load(self, uid: int) -> dict:
        now = self.get_raw(uid)
        return now.get('data', None) if now is not None else None

    def get_all(self) -> dict:
        result = self.col.find({}, {'_id': False})
        res = {}
        for r in result:
            res[r.get('uid', -1)] = r
        # print('manage db got all', res)
        return res

    def remove(self, uid: int):
        res = self.get_raw(uid)
        if res is None:
            return
        self.col.delete_one({'uid': uid})
