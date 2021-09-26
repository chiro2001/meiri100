from gbk_database.tools import *


class DaemonDB(DataDB):
    def __init__(self, d):
        super().__init__(d, 'daemon')
