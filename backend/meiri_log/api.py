import logging

from utils.api_tools import *


class MeiriLog(Resource):
    args_get = reqparse.RequestParser() \
        .add_argument("offset", type=int, required=False, location=["args", ]) \
        .add_argument("limit", type=int, required=False, location=["args", ]) \
        .add_argument("level", type=int, required=False, location=["args", ])

    @args_required_method(args_get)
    @auth_required_method
    def get(self, uid: int):
        args = self.args_get.parse_args()
        offset, limit, level = args.get('offset', 0), args.get('limit', 30), args.get('level', logging.INFO)
        data = db.log.fetch(uid=uid, offset=offset, limit=limit, level=level)
        return make_result(data={
            'logs': data
        })
