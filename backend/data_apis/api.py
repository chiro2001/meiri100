import json
import time

import requests

from meiri_exceptions import *
from data_apis.meiri import MeiRi
from meiri_database.config import Constants


class API:
    def __init__(self, username: str = None, password: str = None, cookies: str = None):
        self.ua = Constants.REQUEST_UA
        self.username, self.password = username, password
        self.cookies = cookies
        # self.meiri = MeiRi(self.request_json)
        self.meiri = MeiRi(self.request_json_cookies, username=username, password=password)

    def init_data(self, **kwargs):
        if self.cookies is None:
            if self.password is None or self.password is None:
                raise MeiRiError("Error args")
            resp = self.meiri.login(self.username, self.password, **kwargs)
            if 'code' in resp and resp['code'] != 100:
                logger.error(f"user: {self.username} login error {resp}")
                return self
            if 'cookies' in resp:
                self.cookies = resp['cookies']
        return self

    @staticmethod
    def from_cookies(cookies: str):
        if cookies is None:
            raise MeiRiCookiesError("Got empty cookies")
        return API(cookies=cookies)

    @staticmethod
    def from_username_password(username: str, password: str):
        return API(username=username, password=password)

    def request_no_302(self, url: str):
        resp = requests.get(url, headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": self.ua,
            "Cookie": self.cookies
        }, allow_redirects=False)
        if resp.status_code != 200:
            return None
        text = resp.content.decode('utf8', errors='ignore')
        return text

    def request_json(self, url: str, method: str = 'GET', **kwargs):
        kwargs2 = {
            "headers": {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "User-Agent": self.ua,
                "Cookie": self.cookies
            }
        }
        kwargs2.update(kwargs)
        resp = requests.request(method, url, **kwargs2)
        if resp.status_code != 200:
            logger.warning(f"{url} Got code %s" % resp.status_code)
            raise MeiRiError(resp.text)
        try:
            js = resp.json()
        except json.decoder.JSONDecodeError as e:
            logger.error(f'Decode error: {url}, {e}')
            raise MeiRiError(resp.text)
        if 'code' in js and (js['code'] != 200 and js['code'] != 0):
            logger.warning("Got code %s and message: %s" % (js.get('code', None), js.get('message', None)))
            logger.warning(js)
            raise MeiRiPermissionError(js)
        return js

    def request_json_cookies(self, url: str, method: str = 'GET', **kwargs):
        kwargs2 = {
            "headers": {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "User-Agent": self.ua,
                "Cookie": self.cookies
            }
        }
        kwargs2.update(kwargs)
        resp = requests.request(method, url, **kwargs2)
        if resp.status_code != 200:
            logger.warning(f"{url} Got code %s" % resp.status_code)
            raise MeiRiError(resp.text)
        try:
            js = resp.json()
        except json.decoder.JSONDecodeError as e:
            if len(resp.text) == 0:
                # ????????????
                return None
            logger.error(f'Decode error: {url}, {e}')
            raise MeiRiError(resp.text)
        # if 'code' in js and (js['code'] != 200 and js['code'] != 0):
        #     logger.warning("Got code %s and message: %s" % (js.get('code', None), js.get('message', None)))
        #     logger.warning(js)
        #     raise MeiRiPermissionError(js)
        cookies_values = resp.cookies.get_dict()
        if isinstance(js, dict):
            js['cookies'] = ';'.join([f'{key}={cookies_values[key]}' for key in cookies_values]) + ';'
        return js


if __name__ == '__main__':
    _a = API.from_cookies(Constants.REQUEST_DEBUG_COOKIES)
    # print(_a.trade_data.get(
    #     int(time.mktime(time.strptime("2021-04-01", "%Y-%m-%d")) * 1000),
    #     int(time.mktime(time.strptime("2021-05-01", "%Y-%m-%d")) * 1000),
    #     1, 1164657484
    # ))
    # _res = _a.flow_data.get('2021-04-01', 1164657484, end_time='2021-05-01')
    # print(_res)
    # _js = json.dumps(_res)
    # with open("../data/flow_data.json", 'w') as f:
    #     f.write(_js)
