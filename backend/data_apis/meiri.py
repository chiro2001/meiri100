from data_apis.data_tools import *


class MeiRi(APIComponent):
    url_base = 'http://yqdz.meiri100.cn/'
    url_login = url_base + 'login/login_ok'
    url_get_tasks = url_base + 'gzTask/get_Tasklist?p=1'
    url_get_sign = url_base + 'wxforward/getSignature?url=http%3A%2F%2Fyqdz.meiri100.cn%2FtaskIssue%2Fcustom_order' \
                              'Info%3Forder_id%3D296%26account_name%3D%25E5%259B%259B%25E6%259C%25881744'
    url_get_task = url_base + 'taskIssue/custom_get_task?order_id=%s&uid=%s&order_type=%s'

    def __init__(self, request_func, username: str = None, password: str = None):
        super().__init__(request_func)
        self.username, self.password = username, password
        self.cookies: str = None
        # 对应网站的 uid
        self.uid: str = None

    def login(self, username: str = None, password: str = None, proxy: str = None, proxies: dict = None) -> dict:
        self.username = username if username is not None else username
        self.password = password if password is not None else password
        if proxies is None and proxy is not None:
            proxies = ({'http': f"http://{proxy}", 'https': f"http://{proxy}"})
        resp = self.request_func(self.url_login, method='POST', data={
            'username': self.username, 'password': self.password
        }, proxies=proxies)
        if 'code' in resp and resp['code'] == 100:
            if 'cookies' in resp:
                self.cookies = resp['cookies']
            if 'uid' in resp:
                self.uid = resp['uid']
        return resp

    def get_tasks(self, proxy: str = None, **kwargs) -> list:
        resp = self.request_func(self.url_get_tasks, proxies=(
            {'http': f"http://{proxy}", 'https': f"http://{proxy}"}) if proxy is not None else None, **kwargs)
        if resp is None:
            return []
        return resp

    def get_task(self, task: dict, **kwargs):
        resp = self.request_func(self.url_get_task % (task['order_id'], self.uid, task['order_type']), **kwargs)
        return resp
