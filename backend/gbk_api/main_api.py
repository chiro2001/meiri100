import os
import json
from flask import Flask, Response
from flask_cors import CORS
from flask_restful import Resource, Api

from gbk_error_report.api import ErrorReport
from utils.error_report import form_report
from utils.logger import logger
from utils.docs import get_class_docs
from utils.make_result import make_result
from gbk_database.database import db

from gbk_user.api import *
from gbk_session.api import *
from gbk_scheduler.task_api import *
from gbk_sync.api import *
from gbk_scheduler.action_api import *
from gbk_scheduler.trigger_api import *
from gbk_remote_login.api import *
from gbk_daemon.api import *


class MainAPI(Resource):
    """
    文档测试
    """

    def get(self):
        """
        文档：get
        """
        return make_result(data={
            'document': {endpoint: get_class_docs(resources[endpoint]) for endpoint in resources},
            'curdir': os.path.abspath(os.curdir)
        })


class DropData(Resource):
    def get(self):
        db.rebase()
        return make_result()


resources = {}


def add_resource(class_type: Resource, endpoint: str):
    global resources
    resources[endpoint] = class_type


def apply_resource(api_: Api):
    for endpoint in resources:
        api_.add_resource(resources[endpoint], endpoint)


app = Flask(__name__)
api = Api(app)
add_resource(MainAPI, '/')
add_resource(User, "/user")
add_resource(UserUid, "/user/<int:uid>")
add_resource(UserInfo, "/user_info")
add_resource(Session, "/session")
add_resource(Password, '/password')
if Constants.RUN_WITH_DROP_DATA:
    add_resource(DropData, '/drop_data')
add_resource(TaskManagerAPI, '/task')
add_resource(TaskManagerTid, '/task/<int:tid>')
add_resource(ActionAPI, '/action')
add_resource(ActionName, '/action/<string:action_type>')
add_resource(TriggerAPI, '/trigger')
add_resource(TriggerName, '/trigger/<string:trigger_type>')
add_resource(Sync, '/sync')
add_resource(RemoteLoginAPI, '/remote_login')
add_resource(DaemonAPI, '/daemon')
add_resource(ErrorReport, '/error_report')
if Constants.RUN_WITH_PREDICTS:
    if Constants.RUN_IGNORE_TF_WARNINGS:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    logger.info('Loading Tensorflow...')
    from gbk_predicts.api import Predicts

    add_resource(Predicts, '/predicts')

apply_resource(api)

CORS(app)


@app.after_request
def api_after(res: Response):
    # 对遇到的Exception做包装...
    if len(res.data) > 0:
        try:
            js = json.loads(res.data)
            if isinstance(js, str):
                # decode 到 str 表示 raise 了 Error...但是为什么呢？？
                if js == Constants.EXCEPTION_LOGIN:
                    # http code 424 表示需要重新远程登录了
                    js = make_result(424, message=js)[0]
                else:
                    js = make_result(400, message=js)[0]
                res.data = json.dumps(js).encode()
                res.status_code = js['code']
            else:
                js['code'] = res.status_code
                res.data = json.dumps(js).encode()
            if js['code'] != 200:
                logger.warning(f'response: {js}')
            if js['code'] == 500:
                db.start_error_report(js)
        except Exception as e:
            logger.error(e)
            logger.error(f'data: {res.data}')
            res.data = json.dumps(make_result(500, message=f'{e}')[0])
            db.start_error_report(form_report(e))
            res.status_code = 500
    return res


if __name__ == '__main__':
    app.run()
