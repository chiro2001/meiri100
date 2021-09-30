from utils.api_tools import *
from utils.vip_code import vip_code_check, generate_by_username


class User(Resource):
    args_signin = reqparse.RequestParser() \
        .add_argument("username", type=str, required=True, location=["json", ]) \
        .add_argument("password", type=str, required=True, location=["json", ]) \
        .add_argument("vip_code", type=str, required=True, location=["json", ]) \
        .add_argument("email", type=str, required=True, location=["json", ])

    # 此处可能并非线程安全...使用的 args_signin 是静态变量
    # 但是parser使用的是全局request，所以应该安全
    @args_required_method(args_signin)
    def post(self):
        """
        注册
        :json username: 用户名
        :json password: 密码
        :json vip_code: 验证码
        :json email: 邮箱
        :return:
        """
        args = self.args_signin.parse_args()
        username, password = args.get('username'), args.get('password')
        vip_code = args.get('vip_code')
        if not vip_code_check(vip_code=vip_code, username=username):
            return make_result(400, message="验证码错误！")
        result, text = password_check(password)
        if not result:
            return make_result(400, message=text)
        # check_result = db.session.check_password(username=username, password=password)
        # if not check_result:
        #     return make_result(403)
        try:
            uid = db.user.insert({
                'username': username,
                'nick': username,
                'level': 1,
                'state': 'normal',
                'profile': {
                    'contact': {
                        'email': args.get('email')
                    }
                }
            })
        except meiri_exceptions.MeiRiUserExist:
            return make_result(400, message='用户已存在')
        db.session.insert(uid, password)
        # 添加对应任务
        task: Task = Task(name=f"meiri_get_task_{uid}",
                          actions=[ActionMeiriGetTasksCycle(uid=uid), ],
                          triggers=[IntervalTrigger(seconds=Constants.RUN_TASKS_DELAYS.get('user_get_task', 3)), ])
        # logger.warning(f"uid: {uid} will add task: {task}")
        task_pool.add_task(uid, task)
        task_email = Task(name=f"meiri_report_{uid}",
                          actions=[ActionMeiriReport(uid=uid), ],
                          triggers=[
                              IntervalTrigger(seconds=Constants.RUN_TASKS_DELAYS.get('user_report', 60 * 60 * 24)), ])
        # logger.warning(f"uid: {uid} will add task_email: {task_email}")
        task_pool.add_task(uid, task_email)
        # logger.warning(f"Jobs now: ")
        # scheduler.print_jobs()
        return make_result(data={'uid': uid})

    @auth_required_method
    def get(self, uid: int):
        """
        获取用户信息
        :param uid: uid
        :return:
        """
        user = db.user.get_by_uid(uid)
        return make_result(data={'user': user})

    @auth_required_method
    def delete(self, uid: int):
        """
        删除自己用户
        :param uid: uid
        :return:
        """
        db.user.delete_user(uid)
        return make_result()


class UserInfo(Resource):
    args_update_info = reqparse.RequestParser() \
        .add_argument("contact", type=dict, required=True, location=["json", ])

    @args_required_method(args_update_info)
    @auth_required_method
    def post(self, uid: int):
        """
        更新用户信息
        :param uid: uid
        :return:
        """
        user_info = self.args_update_info.parse_args()
        user_raw = db.user.get_by_uid(uid)
        if 'created_at' in user_info:
            del user_info['created_at']
        user_raw['profile'].update(user_info)
        result = db.user.update_one(user_raw)
        if not result:
            return make_result(400)
        return make_result()


class UserUid(Resource):
    def get(self, uid: int):
        """
        获取 uid 对应用户信息
        :param uid: uid
        :return:
        """
        user = db.user.get_by_uid(uid)
        return make_result(data={'user': user})


class VipCodeGenerate(Resource):
    args_vip_code = reqparse.RequestParser() \
        .add_argument("username", type=str, required=True, location=["args", ])

    @args_required_method(args_vip_code)
    @auth_required_method
    def get(self, uid: int):
        if uid != 1:
            return make_result(403)
        args = self.args_vip_code.parse_args()
        username = args.get('username')
        return make_result(data={
            'vip_code': generate_by_username(username)
        })
