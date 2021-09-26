from utils.api_tools import *


class Session(Resource):
    args_login = reqparse.RequestParser() \
        .add_argument("username", type=str, required=True, location=["json", ]) \
        .add_argument("password", type=str, required=True, location=["json", ])
    args_update = reqparse.RequestParser() \
        .add_argument("Refresh", type=str, required=True, location=Constants.JWT_LOCATIONS)

    @args_required_method(args_login)
    def post(self):
        """
        登录
        :return:
        """
        args = self.args_login.parse_args()
        username, password = args.get('username'), args.get('password')
        user = db.user.find_by_username(username=username)
        if user is None:
            return make_result(403)
        uid = user.get('uid')
        result = db.session.check_password(uid=uid, password=password)
        if not result:
            return make_result(403)
        db.session.update_login(uid)
        token_payload = {'uid': uid}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        return make_result(data={'access_token': access_token, 'refresh_token': refresh_token})

    @args_required_method(args_update)
    def get(self):
        """
        更新 access_token
        :return:
        """
        refresh_token = self.args_update.parse_args(http_error_code=401).get('Refresh')
        try:
            data = Statics.tjw_refresh_token.loads(refresh_token)
        except (BadSignature, BadData, BadHeader, BadPayload) as e:
            return make_result(422, message=f"Bad token: {e}")
        except BadTimeSignature:
            return make_result(424)
        # 禁用原来的 refresh_token
        db.session.disable_token(refresh_token=refresh_token)
        uid = data.get('uid')
        payload = {
            'uid': uid
        }
        access_token = create_access_token(payload)
        refresh_token_new = create_refresh_token(payload)
        return make_result(data={
            'access_token': access_token,
            'refresh_token': refresh_token_new
        })

    @auth_required_method
    def delete(self, access_token: str):
        """
        注销
        :return:
        """
        # logger.warning('access_token: ' + access_token)
        refresh_token = self.args_update.parse_args(http_error_code=401).get('Refresh')
        # logger.warning('refresh_token: ' + refresh_token)
        try:
            Statics.tjw_refresh_token.loads(refresh_token)
        except (BadSignature, BadData, BadHeader, BadPayload) as e:
            return make_result(422, message=f"Bad token: {e}")
        except BadTimeSignature:
            return make_result(424)
        db.session.disable_token(access_token=access_token, refresh_token=refresh_token)
        return make_result()


class Password(Resource):
    # 更新密码
    args_update_password = reqparse.RequestParser() \
        .add_argument("password")

    @args_required_method(args_update_password)
    @auth_required_method
    def post(self, uid: int):
        password = self.args_update_password.parse_args().get('password')
        if not db.session.update_one({'uid': uid, 'password': password}):
            return make_result(400)
        # logger.error(f'update password done: uid={uid}, password={password}')
        return make_result()
