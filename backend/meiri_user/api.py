from utils.api_tools import *
from utils.vip_code import vip_code_check, generate_by_username


class User(Resource):
    args_signin = reqparse.RequestParser() \
        .add_argument("username", type=str, required=True, location=["json", ]) \
        .add_argument("password", type=str, required=True, location=["json", ]) \
        .add_argument("vip_code", type=str, required=True, location=["json", ])

    # 此处可能并非线程安全...使用的 args_signin 是静态变量
    # 但是parser使用的是全局request，所以应该安全
    @args_required_method(args_signin)
    def post(self):
        """
        注册
        :json username: 用户名
        :json password: 密码
        :json vip_code: 验证码
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
                'profile': {}
            })
        except meiri_exceptions.MeiRiUserExist:
            return make_result(400, message='用户已存在')
        db.session.insert(uid, password)
        # 添加对应任务
        task: Task = Task(name=f"meiri_get_task_{uid}",
                          actions=[ActionMeiriGetTasksCycle(uid=uid), ],
                          triggers=[IntervalTrigger(seconds=Constants.RUN_TASKS_DELAYS.get('user_get_task', 3)), ])
        task_pool.add_task(uid, task)
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
    @auth_required_method
    def post(self, uid: int):
        """
        更新用户信息
        :param uid: uid
        :return:
        """
        user = reqparse.RequestParser().parse_args()
        user['uid'] = uid
        result = db.user.update_one(user)
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
