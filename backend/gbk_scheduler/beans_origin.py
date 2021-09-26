class RoomItem:
    def __init__(self, itemId, price, foodDesc, singHours, stock, itemType, periodType, roomType, periodId=None,
                 date=None):
        self.itemId, self.price, self.foodDesc, self.singHours, self.stock, self.itemType, self.periodType, self.periodId, self.date, self.roomType = \
            itemId, price, foodDesc, singHours, stock, itemType, periodType, periodId, date, roomType

    @staticmethod
    def from_json(js):
        return RoomItem(js['itemId'], js['price'], js['foodDesc'], js['singHours'], js['stock'],
                        js['itemType'], js['periodType'], js['roomType'], js.get('periodId', None),
                        js.get('date', None))

    def to_json(self):
        return self.__dict__()


class RoomStockType:
    def __init__(self, roomName, itemStockNo, reserveDate, saleCount, remainCount, acceptOrder):
        self.roomName, self.itemStockNo, self.reserveDate, self.saleCount, self.remainCount, self.acceptOrder = \
            roomName, itemStockNo, reserveDate, saleCount, remainCount, acceptOrder

    @staticmethod
    def from_json(js):
        return RoomStockType(js['roomName'], js['itemStockNo'], js['reserveDate'],
                             js['saleCount'], js['remainCount'], js['acceptOrder'])
