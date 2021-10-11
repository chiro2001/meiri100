from copy import deepcopy

import requests

from meiri_database.config import Constants
from utils.logger import logger

proxy_last = None


def get_proxy() -> dict:
    global proxy_last
    try:
        js = requests.get(f"{Constants.PROXY_POOL_API}get/", timeout=2).json()
        if 'proxy' in js:
            proxy_last = deepcopy(js)
            return js
        else:
            return {}
    except Exception as e:
        logger.warning(f"Cannot get proxy: {e}")
    if proxy_last is not None:
        return proxy_last
    return {}


def delete_proxy(proxy):
    requests.get(f"{Constants.PROXY_POOL_API}delete/?proxy={proxy}")


proxy_last_2 = None


def get_proxy_2() -> list:
    global proxy_last_2
    try:
        text = requests.get(f"{Constants.PROXY_POOL_API_2}", timeout=2).text
        li = text.split('\r\n')
        li = [line for line in li if len(line) > 0]
        proxy_last_2 = deepcopy(li)
        return li
    except Exception as e:
        logger.warning(f'Cannot get proxy: {e}')
    return [] if proxy_last_2 is None else proxy_last_2


# your spider code

def get_html():
    # ....
    retry_count = 5
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            html = requests.get('http://www.example.com', proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 删除代理池中代理
    delete_proxy(proxy)
    return None
