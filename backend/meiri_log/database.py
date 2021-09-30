from meiri_database.tools import *


class MeiriLogDB(BaseDB):
    def __init__(self, d):
        super().__init__(d, 'log')

    def log(self, uid: int, level: int, text: str):
        # logger.log(level, text)
        logger.info(f"uid: {uid}, level: {level}, text: {text}")
        auto_time_insert(self.col, {
            'uid': uid,
            'level': level,
            'text': text
        })

    def fetch(self, uid: int = None, level: str = None, offset: int = 0, limit: int = 30):
        filter_dict = {}
        if uid is not None:
            filter_dict['uid'] = uid
        if level is not None:
            filter_dict['level'] = {
                '$gte': level
            }
        data = find_many(self.col, filter_dict, sort_by='created_at', reverse=True, limit=limit, offset=offset)
        return data
