import requests

from data_apis.data_tools import *


class TradeData(APIComponent):
    url = 'https://e.dianping.com/ktv/api/queryTradeRecord.wbc'

    def __init__(self, request_func, shop_id: int = None):
        super().__init__(request_func)
        self.shop_id = shop_id

    def get(self, begin_time: int, end_time: int, page: int = 1, shop_id: int = None):
        shop_id = shop_id if shop_id is not None else self.shop_id
        request_param = {
            'shopid': shop_id, 'tradeBeginTime': begin_time, 'tradeEndTime': end_time,
            'tradeModes': '1,2,3,4',
            'countType': '1', 'page': page
        }
        return self.request_func(url=self.url, params=request_param)
