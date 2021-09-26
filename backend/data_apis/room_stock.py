from data_apis.data_tools import *


class RoomsStock(APIComponent):
    url_base = 'https://e.dianping.com/ktv/api/'
    url_load_price_table = url_base + 'loadpricetable.wbc?shopid=%s'  # 参数：shopid

    def __init__(self, request_func, shop_id: int):
        super().__init__(request_func)
        self.shop_id = shop_id

    def set_shop_id(self, shop_id):
        self.shop_id = shop_id

    def get_room_stock(self):
        resp = self.request_func(self.url_load_price_table % self.shop_id)
        return resp
