from gbk_database.tools import *
from utils.formats import *
import gbk_exceptions


class UserDB(BaseDB):
    def __init__(self, d):
        super().__init__(d, 'user')
        init_sequence_id(self.d.user_uid, "cnt_uid", 0)

    def get_next_uid(self):
        return get_next_id(self.d.user_uid, "cnt_uid")

    def insert(self, user: dict) -> int:
        user_data = self.find_by_username(user.get('username'))
        if user_data is not None:
            raise gbk_exceptions.GBKUserExist
        uid = self.get_next_uid()
        user['uid'] = uid
        auto_time_update(self.col, {'username': user.get('username')}, user)
        return uid

    def find(self, filter_dict: dict, limit: int = Constants.FIND_LIMIT, offset: int = 0) -> list:
        result = find_many(self.col, filter_dict, limit=limit, offset=offset)
        return result

    def update_one(self, user: dict) -> bool:
        uid = user.get('uid')
        user_data = self.get_by_uid(uid)
        if user_data is None:
            return False
        print('user_data', json_dumps_format(user_data))
        print('user', json_dumps_format(user))
        if 'created_at' in user_data:
            del user_data['created_at']
        dict_update(user_data, user)
        auto_time_update(self.col, {'uid': user}, user_data)
        return True

    def get_by_uid(self, uid: int) -> dict or None:
        return find_one(self.col, {'uid': uid})

    def find_by_username(self, username: str) -> dict or None:
        return find_one(self.col, {'username': username})

    def delete_user(self, uid: int):
        self.col.delete_one({'uid': uid})
