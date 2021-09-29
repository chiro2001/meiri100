from flask_restful import Resource
import re
from meiri_auth.tjw_auth import *
from utils.args_decorators import args_required_method
from utils.make_result import make_result
from utils.password_check import password_check
from meiri_database.config import Statics
from meiri_database.database import db
from meiri_scheduler.task_pool import *
import meiri_exceptions

args_selector = reqparse.RequestParser() \
    .add_argument("limit", type=int, required=False, location=["args", ]) \
    .add_argument("offset", type=int, required=False, location=["args", ])
