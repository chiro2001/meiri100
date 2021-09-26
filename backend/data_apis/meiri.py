from data_apis.data_tools import *


class MeiRi(APIComponent):
    url_base = 'http://yqdz.meiri100.cn/'
    url_login = 'login/login_ok'
    url_get_tasks = 'gzTask/get_Tasklist?p=1'
    url_get_sign = 'wxforward/getSignature?url=http%3A%2F%2Fyqdz.meiri100.cn%2FtaskIssue%2Fcustom_orderInfo%3Forder_id' \
                   '%3D296%26account_name%3D%25E5%259B%259B%25E6%259C%25881744'
    url_get_task = 'taskIssue/custom_get_task?order_id=%s&uid=%s&order_type=3'

    def __init__(self, request_func):
        super().__init__(request_func)

    def login(self, username: str, password: str) -> str:
        resp = self.request_func(self.url_login, method='POST', data={
            'username': username, 'password': password
        })
        return resp
