from utils.api_tools import *


class Account(Resource):
    args_add_account = reqparse.RequestParser() \
        .add_argument("username", type=str, required=True, location=["json", ]) \
        .add_argument("password", type=str, required=True, location=["json", ])
    args_get_account = reqparse.RequestParser() \
        .add_argument("username", type=str, required=False, location=["args", ])
    args_remove_account = reqparse.RequestParser() \
        .add_argument("username", type=str, required=True, location=["args", ])
    args_set_account_on = reqparse.RequestParser() \
        .add_argument("username", type=str, required=True, location=["args", ]) \
        .add_argument("enabled", type=int, required=True, location=["args", ])

    @args_required_method(args_add_account)
    @auth_required_method
    def post(self, uid: int):
        """
        添加 account
        """
        args = self.args_add_account.parse_args()
        username, password = args.get('username'), args.get('password')
        db.account.add_account(uid, username, password)
        return make_result()

    @args_required_method(args_get_account)
    @auth_required_method
    def get(self, uid: int):
        args = self.args_get_account.parse_args()
        username = args.get('username', None)
        if username is not None:
            account = db.account.get_one_account(uid, username)
            return make_result(data={
                'accounts': [account, ]
            })
        else:
            accounts = db.account.get_by_uid(uid)
            return make_result(data={
                'accounts': accounts
            })

    @args_required_method(args_remove_account)
    @auth_required_method
    def delete(self, uid: int):
        args = self.args_remove_account.parse_args()
        username = args.get('username')
        if not db.account.remove_account(uid, username):
            return make_result(400)
        return make_result()

    @args_required_method(args_set_account_on)
    @auth_required_method
    def patch(self, uid: int):
        args = self.args_set_account_on.parse_args()
        username, enabled = args.get('username'), args.get('enabled')
        db.account.set_account_on(uid, username, int(enabled) > 0)
        return make_result()
