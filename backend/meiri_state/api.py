from utils.api_tools import *


class MeiriState(Resource):
    @auth_required_method
    def get(self, uid: int):
        return make_result()
