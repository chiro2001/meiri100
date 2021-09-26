import re
import json
import time
from utils.time_formats import *
from gbk_exceptions import *


class APIComponent:
    def __init__(self, request_func):
        self.request_func = request_func
