from datetime import datetime


class BaseTrigger:
    def __init__(self, trigger_type: str):
        self.trigger_type: str = trigger_type

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.trigger_type = state.get('trigger_type')


class StockTrigger(BaseTrigger):
    def __init__(self):
        super().__init__(trigger_type='stock')
        self.start_date: datetime = datetime.now()
        self.end_date: datetime = None
        self.value: int = 5
        self.operator: str = '>'
