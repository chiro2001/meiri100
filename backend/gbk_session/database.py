from gbk_database.tools import *
import datetime
# from utils.logger import logger


class SessionDB(BaseDB):
    def __init__(self, d):
        super().__init__(d, 'session')
        self.col_disabled_token: pymongo.collection.Collection = d.session_disabled_token
        # 创建TTL索引，根据两个有限时间确定自动删除时间（会不会太长？）
        self.col_disabled_token.create_index([("time", pymongo.ASCENDING)], expireAfterSeconds=0)

    def get_by_uid(self, uid: int) -> dict or None:
        return find_one(self.col, {'uid': uid})

    def check_password(self, uid: int, password: str) -> bool:
        user_data = find_one(self.col, {'uid': uid, 'password': password})
        if user_data is None:
            return False
        if user_data.get('password') != password:
            return False
        return True

    def update_one(self, session: dict) -> bool:
        uid = session.get('uid')
        session_data = self.get_by_uid(uid)
        if session_data is None:
            return False
        # print('session_data', json_dumps_format(session_data))
        # print('session', json_dumps_format(session))
        if 'created_at' in session_data:
            del session_data['created_at']
        dict_update(session_data, session)
        return auto_time_update(self.col, {'uid': uid}, session_data)

    def update_login(self, uid: int) -> bool:
        session = self.get_by_uid(uid)
        if session is None:
            return False
        if 'created_at' in session:
            del session['created_at']
        session['last_login'] = datetime.datetime.utcnow()
        return self.update_one(session)

    def insert(self, uid: int, password: str):
        auto_time_update(self.col, {'uid': uid}, {'uid': uid, 'password': password})

    def remove(self, uid: int):
        self.col.delete_one({'uid': uid})

    def disable_token(self, access_token: str = None, refresh_token: str = None):
        if access_token is not None:
            self.col_disabled_token.insert_one({
                'token': access_token,
                'time': datetime.datetime.utcnow() + datetime.timedelta(seconds=Constants.JWT_ACCESS_TIME)
            })
        if refresh_token is not None:
            self.col_disabled_token.insert_one({
                'token': refresh_token,
                'time': datetime.datetime.utcnow() + datetime.timedelta(seconds=Constants.JWT_REFRESH_TIME)
            })

    def token_available(self, token: str) -> bool:
        result = self.col_disabled_token.find_one({'token': token})
        # logger.warning(f'token: ...{token[-5:]} {"available" if result is None else "disabled"}')
        if result is None:
            return True
        return False
