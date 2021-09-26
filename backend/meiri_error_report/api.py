from utils.api_tools import *


class ErrorReport(Resource):
    args_error = reqparse.RequestParser() \
        .add_argument("error", type=dict, required=True, location=['json', ])

    # predicts
    @args_required_method(args_error)
    @auth_required_method
    def post(self):
        err = self.args_error.parse_args().get("error", None)
        if err is None:
            return make_result(400)
        db.start_error_report(err)
        return make_result()
