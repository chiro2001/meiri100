import pymongo
import datetime
from gbk_database.config import Constants
from gbk_exceptions import *
from utils.logger import logger


def dict_update(dist: dict, src: dict) -> dict:
    result = dist
    for k in src:
        v = src[k]
        if k in dist:
            if type(dist[k]) is type(dict):
                result[k] = dict_update(dist[k], v)
            else:
                result[k] = v
        else:
            dist[k] = v
    return result


def dict_remove_empty(data, delete=None):
    if data is None:
        return None
    if isinstance(data, list):
        return [dict_remove_empty(d) for d in data]
    if not isinstance(data, dict):
        return data
    return {k: dict_remove_empty(data[k]) for k in data if data[k] != delete}


def insert_id_if_not_exist(col: pymongo.collection.Collection, key_name: str, value):
    result = col.find_one({"_id": key_name})
    # logger.warning(f'result: {result}, key_name: {key_name}')
    if result is None:
        # logger.warning(f'insert key_name: {key_name}')
        col.insert_one({"_id": key_name, "sequence_value": value})


def auto_time_insert(col: pymongo.collection.Collection,
                     insert_dict: dict):
    dt0 = datetime.datetime.utcnow()
    insert_dict['created_at'] = dt0
    return col.insert_one(insert_dict)


def auto_time_update(col: pymongo.collection.Collection,
                     filter_dict: dict, update_dict: dict, insert_if_necessary: bool = False):
    if insert_if_necessary:
        # 先看看原来有没有数据
        res = find_one(col, filter_dict)
        if res is None:
            all_data = {k: filter_dict[k] for k in filter_dict if '.' not in k}
            all_data.update(update_dict)
            return auto_time_insert(col, all_data)
    dt0 = datetime.datetime.utcnow()
    update_dict['updated_at'] = dt0
    update_dict = {'$set': update_dict, '$setOnInsert': {'created_at': dt0}}
    return col.update_one(filter_dict, update_dict, upsert=True)


def find_one(col: pymongo.collection.Collection,
             filter_dict: dict, include_id: bool = False) -> dict or None:
    result = col.find_one(filter_dict, {"_id": 1 if include_id else 0})
    if result is None:
        return None
    return dict(result)


def find_many(col: pymongo.collection.Collection,
              filter_dict: dict,
              sort_by: str = None,
              reverse: bool = False,
              limit: int = Constants.FIND_LIMIT,
              offset: int = 0,
              include_id: bool = False) -> list:
    result = col.find(filter_dict, {"_id": 1 if include_id else 0})
    if sort_by is not None:
        result = result.sort(sort_by, pymongo.DESCENDING if reverse else pymongo.ASCENDING)
    result = result.skip(offset).limit(limit)
    return list(result)


def tree_update_path(tree: dict, path: str = None, splits: list = None):
    if path is None and splits is None:
        return tree
    if path is not None:
        splits = [_ for _ in path.split('/') if len(_) > 0]
    if splits is None:
        return tree
    if len(splits) == 0:
        return tree
    if splits[0] not in tree or len(splits) == 2:
        tree[splits[0]] = {}
    if len(splits) == 1:
        tree[splits[0]] = None
    if tree[splits[0]] is not None:
        tree[splits[0]].update(tree_update_path(tree[splits[0]], splits=splits[1:]))
    else:
        return tree
    return tree


def tree_delete_path(tree, path: str) -> (dict, bool):
    splits = [_ for _ in path.split('/') if len(_) > 0]
    if len(splits) == 0 and path == '/':
        return {}, True
    try:
        exec(f"""del tree{''.join([f'["{i}"]' for i in splits])}""")
    except KeyError:
        return tree, False
    return tree, True


class BaseDB:
    def __init__(self, d, col_name: str):
        self.d = d
        self.col: pymongo.collection.Collection = d[col_name]


# 根据 uid 和 data_type 保存数据
class DataDB(BaseDB):
    def __init__(self, d, col_name: str):
        super().__init__(d, col_name)

    def delete(self, uid: int, data_type: str = "base"):
        try:
            self.col.delete_one({'uid': uid, 'data_type': data_type})
        except Exception as e:
            logger.error(e)

    def save(self, uid: int, data, data_type: str = 'base', filter_: dict = None):
        fil = {'uid': uid, 'data_type': data_type}
        fil.update(filter_ if filter_ is not None else {})
        auto_time_update(self.col,
                         fil,
                         {'data': data},
                         insert_if_necessary=True)

    def load(self, uid: int, data_type: str = 'base', filter_: dict = None):
        if uid is None:
            return find_many(self.col, {'data_type': data_type})
        fil = {'uid': uid, 'data_type': data_type}
        fil.update(filter_ if filter_ is not None else {})
        return find_one(self.col, fil)


# 根据 uid, key 和 data_type 保存数据
class DataKeyDB(BaseDB):
    def __init__(self, d, col_name: str):
        super().__init__(d, col_name)

    def delete(self, uid: int, data_type: str = "base", key: str = None):
        try:
            query = {'uid': uid, 'data_type': data_type}
            if key is not None:
                query['key'] = key
            self.col.delete_one(query)
        except Exception as e:
            logger.error(e)

    def save(self, uid: int, data, data_type: str = 'base', key: str = None):
        if key is None:
            raise GBKError("Cannot save without key")
        auto_time_update(self.col, {'uid': uid, 'data_type': data_type, 'key': key}, {'data': data},
                         insert_if_necessary=True)

    def load(self, uid: int, data_type: str = 'base', key: str = None):
        if uid is None and key is None:
            raise GBKError("Operation error")
        if uid is None:
            return find_many(self.col, {'data_type': data_type, 'key': key})
        return find_one(self.col, {'uid': uid, 'data_type': data_type, 'key': key})


def init_sequence_id(col: pymongo.collection.Collection, id_name: str, default_value: int = 0):
    insert_id_if_not_exist(col, id_name, default_value)


def get_next_id(col: pymongo.collection.Collection, id_name: str) -> int:
    # logger.warning(f'id_name: {id_name}')
    ret = col.find_one_and_update({"_id": id_name},
                                  {"$inc": {"sequence_value": 1}},
                                  new=True)
    new_id = ret["sequence_value"]
    return new_id


def get_current_id(col: pymongo.collection.Collection, id_name: str) -> int:
    ret = col.find_one({"_id": id_name})
    cnt_id = ret["sequence_value"]
    return cnt_id


def get_next_exist_id(col: pymongo.collection.Collection, id_name: str, now: int) -> int:
    ret = list(col.find({id_name: {"$gt": now}}, {'_id': 0}).sort(id_name, 1).limit(1))
    if len(ret) > 0:
        return ret[0][id_name]
    return None


def get_first_exist_id(col: pymongo.collection.Collection, id_name: str) -> int:
    return get_next_exist_id(col, id_name, -1)
