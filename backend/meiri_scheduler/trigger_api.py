from utils.api_tools import *
from gbk_scheduler.task import *


class TriggerAPI(Resource):
    args_trigger = reqparse.RequestParser().add_argument("trigger", type=dict, required=True, location=["json", ]) \
        .add_argument("args", type=dict, required=False, location=["json", ])

    @args_required_method(args_trigger)
    def post(self):
        """
        补全trigger信息
        """
        trigger = self.args_trigger.parse_args().get('trigger')
        args = self.args_trigger.parse_args().get('args')
        args = args if args is not None else {}
        trigger_type = trigger.get('trigger_type', 'base')
        if trigger_type not in trigger_types:
            return make_result(400, message=f"No trigger type as {trigger_type}")
        instance = trigger_types[trigger_type](**args)
        instance_data = instance.__getstate__()
        instance_data.update(trigger)
        return make_result(data=instance_data)

    def get(self):
        """
        获取可用trigger_type
        """
        # return make_result(data={
        #     'trigger_types': list(trigger_types.keys()),
        #     'trigger_data': {trigger: trigger_get_info(trigger) for trigger in list(trigger_types.keys())},
        #     'trigger_names': trigger_names
        # })
        return make_result(data={
            'triggers': {trigger: {
                "data": trigger_get_info(trigger),
                'desc': trigger_desc.get(trigger, None),
                'name': trigger_names_available.get(trigger),
                'type': trigger,
                'args': trigger_args.get(trigger)
            } for trigger in trigger_names_available}
        })


class TriggerName(Resource):
    args_trigger_optional = reqparse.RequestParser().add_argument("trigger", type=dict, required=False,
                                                                  location=["json", ]) \
        .add_argument("args", type=dict, required=False, location=["json", ])

    def get(self, trigger_type: str):
        """
        获取对应名称的trigger信息
        """
        if trigger_type not in trigger_types:
            return make_result(400, message=f"No trigger type as {trigger_type}")
        instance = trigger_types[trigger_type]()
        instance_data = instance.__getstate__()
        instance_data = task_data_encode(instance_data)
        logger.info(f'{trigger_type} data: {instance_data}')
        return make_result(data=instance_data)

    @args_required_method(args_trigger_optional)
    def post(self, trigger_type: str):
        """
        获取对应名称的trigger信息（可以更新数据）
        """
        if trigger_type not in trigger_types:
            return make_result(400, message=f"No trigger type as {trigger_type}")
        trigger = self.args_trigger_optional.parse_args().get('trigger')
        trigger = trigger if trigger is not None else {}
        args = self.args_trigger_optional.parse_args().get('args')
        args = args if args is not None else {}
        # 以url参数为准
        if 'trigger_type' in trigger:
            del trigger['trigger_type']
        instance = trigger_types[trigger_type](**args)
        instance_data = instance.__getstate__()
        instance_data = task_data_encode(instance_data)
        instance_data.update(trigger)
        return make_result(data=instance_data)
