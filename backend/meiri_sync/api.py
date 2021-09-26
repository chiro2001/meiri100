from utils.api_tools import *


class Sync(Resource):
    args_upload = reqparse.RequestParser() \
        .add_argument("config", type=dict, required=True, location=["json", ])

    @args_required_method(args_upload)
    @auth_required_method
    def post(self, uid: int):
        """
        上传数据
        :return:
        """
        data = self.args_upload.parse_args()
        db.sync.update(uid, data)
        return make_result()

    @auth_required_method
    def get(self, uid: int):
        """
        下载数据
        :return:
        """
        data = db.sync.find_by_uid(uid)
        if data is None:
            return make_result(data={})
        return make_result(data=data.get('data'))
