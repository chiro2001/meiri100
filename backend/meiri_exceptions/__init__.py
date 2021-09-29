from utils.logger import logger


class MeiRiBaseError(Exception):
    def __init__(self, data: str = None):
        self.data = data
        logger.error(self.__str__())

    def __str__(self):
        return f"Error: {self.__class__.__name__}{(' : %s' % self.data) if self.data is not None else ''}"


class MeiRiUserExist(MeiRiBaseError):
    pass


class MeiRiPermissionError(MeiRiBaseError):
    pass


class MeiRiLoginError(MeiRiBaseError):
    pass


class MeiRiShopIdError(MeiRiBaseError):
    pass


class MeiRiError(MeiRiBaseError):
    pass


class MeiRiCookiesError(MeiRiBaseError):
    pass
