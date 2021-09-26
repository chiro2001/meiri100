from utils.api_tools import *
from gbk_daemon.daemon import daemon, DaemonBean


class DaemonAPI(Resource):
    args_daemon_update = reqparse.RequestParser() \
        .add_argument("daemon_args", type=dict, required=True, location=["json", ])

    @auth_required_method
    def get(self, uid: int):
        """
        获取deamon
        """
        d: DaemonBean = daemon.get_daemon(uid)
        if d is None:
            return make_result(200, message='has not remote login yet')
        return make_result(200, data=d.__getstate__())

    @args_required_method(args_daemon_update)
    @auth_required_method
    def post(self, uid: int):
        """
        依照参数更新Daemon
        """
        args = self.args_daemon_update.parse_args().get("daemon_args")
        d: DaemonBean = daemon.get_daemon(uid, init_new=True)
        if d is None:
            return make_result(200, message='has not remote login yet')
        d = daemon.update_data(uid=uid, **args)
        return make_result(200, data=d.__getstate__())
