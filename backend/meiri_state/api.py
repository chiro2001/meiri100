from utils.api_tools import *


class MeiriState(Resource):
    @auth_required_method
    def get(self, uid: int):
        fetched_task = db.state.get_fetched_task_number(uid)
        return make_result(data={
            'state': {
                'fetched_task': fetched_task
            }
        })
