from meiri_database.tools import *


class MeiriStateDB(BaseDB):
    def __init__(self, d):
        super().__init__(d, 'state')

    def increase_fetched_task(self):
        pass

    def get_fetched_task(self) -> int:
        pass