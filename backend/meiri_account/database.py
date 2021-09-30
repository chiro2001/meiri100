from meiri_database.tools import *
import datetime


# from utils.logger import logger


class AccountDB(BaseDB):
    def __init__(self, d):
        super().__init__(d, 'account')

    def get_by_uid(self, uid: int) -> list or None:
        return find_many(self.col, {'uid': uid})

    def get_one_account(self, uid: int, username: str) -> dict:
        return find_one(self.col, {"uid": uid, "username": username})

    def add_account(self, uid: int, username: str, password: str, enabled: bool = True):
        auto_time_update(self.col, {"uid": uid, "username": username},
                         {"uid": uid, "username": username, "password": password, 'enabled': enabled},
                         insert_if_necessary=True)

    def set_account_on(self, uid, username: str, enabled: bool):
        auto_time_update(self.col, {"uid": uid, "username": username},
                         {"uid": uid, 'enabled': enabled},
                         insert_if_necessary=False)

    def remove_account(self, uid: int, username: str) -> bool:
        account = self.get_one_account(uid, username)
        if account is None:
            return False
        self.col.delete_one({"uid": uid, "username": username})
        return True

# def update_one(self, session: dict) -> bool:
#     uid = session.get('uid')
#     session_data = self.get_by_uid(uid)
#     if session_data is None:
#         return False
#     # print('session_data', json_dumps_format(session_data))
#     # print('session', json_dumps_format(session))
#     if 'created_at' in session_data:
#         del session_data['created_at']
#     dict_update(session_data, session)
#     return auto_time_update(self.col, {'uid': uid}, session_data)
#
# def update_login(self, uid: int) -> bool:
#     session = self.get_by_uid(uid)
#     if session is None:
#         return False
#     if 'created_at' in session:
#         del session['created_at']
#     session['last_login'] = datetime.datetime.utcnow()
#     return self.update_one(session)
#
# def insert(self, uid: int, password: str):
#     auto_time_update(self.col, {'uid': uid}, {'uid': uid, 'password': password})
#
# def remove(self, uid: int):
#     self.col.delete_one({'uid': uid})
#
# def disable_token(self, access_token: str = None, refresh_token: str = None):
#     if access_token is not None:
#         self.col_disabled_token.insert_one({
#             'token': access_token,
#             'time': datetime.datetime.utcnow() + datetime.timedelta(seconds=Constants.JWT_ACCESS_TIME)
#         })
#     if refresh_token is not None:
#         self.col_disabled_token.insert_one({
#             'token': refresh_token,
#             'time': datetime.datetime.utcnow() + datetime.timedelta(seconds=Constants.JWT_REFRESH_TIME)
#         })
#
# def token_available(self, token: str) -> bool:
#     result = self.col_disabled_token.find_one({'token': token})
#     # logger.warning(f'token: ...{token[-5:]} {"available" if result is None else "disabled"}')
#     if result is None:
#         return True
#     return False
