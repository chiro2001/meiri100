from utils.logger import logger


class GBKBaseError(Exception):
    def __init__(self, data: str = None):
        self.data = data
        logger.error(self.__str__())

    def __str__(self):
        return f"Error: {self.__class__.__name__}{(' : %s' % self.data) if self.data is not None else ''}"


class GBKUserExist(GBKBaseError):
    pass


class GBKPermissionError(GBKBaseError):
    pass


class GBKLoginError(GBKBaseError):
    pass


class GBKShopIdError(GBKBaseError):
    pass


class GBKError(GBKBaseError):
    pass


class GBKCookiesError(GBKBaseError):
    pass
