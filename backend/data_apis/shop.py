from data_apis.data_tools import *


class Shop(APIComponent):
    url = 'https://e.dianping.com/merchant/portal/common/cityshop'

    def __init__(self, request_func):
        super().__init__(request_func)
        self.shop_id = None

    def get_shop_id(self):
        js = self.request_func(self.url)
        self.shop_id = js['data']['currentShopId']
        return self.shop_id
