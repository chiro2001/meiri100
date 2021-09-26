from data_apis.data_tools import *


class FlowData(APIComponent):
    url = 'https://e.dianping.com/gateway/mda/defaultData'

    def __init__(self, request_func, shop_id: int = None):
        super().__init__(request_func)
        self.shop_id = shop_id

    def get(self, date_time: str, shop_id: int = None, end_time: str = None):
        shop_id = shop_id if shop_id is not None else self.shop_id
        request_param = {'pageType': 'flowAnalysis'}
        request_data = {'source': 1, 'device': 'pc', 'pageType': 'flowAnalysis', 'shopIds': shop_id, 'platform': 0,
                        'date': date_time + ',' + (date_time if end_time is None else end_time)}
        return self.request_func(self.url, method='POST', params=request_param, data=request_data)
