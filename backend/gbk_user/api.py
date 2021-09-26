from utils.api_tools import *


class User(Resource):
    args_signin = reqparse.RequestParser() \
        .add_argument("username", type=str, required=True, location=["json", ]) \
        .add_argument("password", type=str, required=True, location=["json", ])

    # 此处可能并非线程安全...使用的 args_signin 是静态变量
    # 但是parser使用的是全局request，所以应该安全
    @args_required_method(args_signin)
    def post(self):
        """
        注册
        :json username: 用户名
        :json password: 密码
        :return:
        """
        args = self.args_signin.parse_args()
        username, password = args.get('username'), args.get('password')
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
        except gbk_exceptions.GBKUserExist:
            return make_result(400, message='用户已存在')
        db.session.insert(uid, password)
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
