from gbk_database.tools import *


class SyncDB(BaseDB):
    def __init__(self, d):
        super().__init__(d, 'sync')

    def find_by_uid(self, uid: int):
        return find_one(self.col, {'uid': uid})

    def update(self, uid: int, data: dict):
        now = self.find_by_uid(uid)
        struct = {'uid': uid, 'data': data}
        if now is None:
            auto_time_insert(self.col, struct)
        else:
            auto_time_update(self.col, {'uid': uid}, struct)
