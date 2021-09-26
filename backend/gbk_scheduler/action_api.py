from utils.api_tools import *
from gbk_scheduler.task import *


def action_get_info(action_type: str):
    instance = action_types[action_type]()
    instance_data = instance.__getstate__()
    return instance_data


class ActionAPI(Resource):
    args_action = reqparse.RequestParser().add_argument("action", type=dict, required=True, location=["json", ])

    @args_required_method(args_action)
    def post(self):
        """
        补全action信息
        :return:
        """
        action = self.args_action.parse_args().get('action')
        action_type = action.get('action_type', 'base')
        if action_type not in action_types:
            return make_result(400, message=f"No action type as {action_type}")
        instance = action_types[action_type]()
        instance_data = instance.__getstate__()
        instance_data.update(action)
        return make_result(data=instance_data)

    def get(self):
        """
        获取可用action_type
        :return:
        """
        # return make_result(data={
        #     'action_types': list(action_types.keys())
        # })
        return make_result(data={
            'actions': {action: {
                "data": action_get_info(action),
                'desc': action_desc.get(action, None),
                'name': action_names_available.get(action),
                'type': action,
                'args': action_args.get(action)
            } for action in action_names_available}
        })


class ActionName(Resource):
    args_action_optional = reqparse.RequestParser().add_argument("action", type=dict, required=False,
                                                                 location=["json", ])

    def get(self, action_type: str):
        """
        获取对应名称的action信息
        :return:
        """
        if action_type not in action_types:
            return make_result(400, message=f"No action type as {action_type}")
        instance = action_types[action_type]()
        instance_data = instance.__getstate__()
        return make_result(data=instance_data)

    @args_required_method(args_action_optional)
    def post(self, action_type: str):
        """
        获取对应名称的action信息（可以更新数据）
        :param action_type:
        :return:
        """
        if action_type not in action_types:
            return make_result(400, message=f"No action type as {action_type}")
        action = self.args_action_optional.parse_args().get('action')
        action = action if action is not None else {}
        # 以url参数为准
        if 'action_type' in action:
            del action['action_type']
        instance = action_types[action_type]()
        instance_data = instance.__getstate__()
        instance_data.update(action)
        return make_result(data=instance_data)
