from flask_restful import reqparse
from itsdangerous import BadSignature, BadData, BadHeader, BadPayload, BadTimeSignature
from utils.logger import logger
from utils.make_result import make_result
from gbk_database.config import Statics, Constants
from gbk_database.database import db
import inspect


def create_access_token(identity: dict = None) -> str:
    if identity is None:
        return ""
    identity['type'] = 'access_token'
    return Statics.tjw_access_token.dumps(identity).decode()


def create_refresh_token(identity: dict = None) -> str:
    if identity is None:
        return ""
    identity['type'] = 'refresh_token'
    return Statics.tjw_refresh_token.dumps(identity).decode()


auth_reqparse = reqparse.RequestParser(bundle_errors=True)
auth_reqparse.add_argument(Constants.JWT_HEADER_NAME, type=str, required=True, location=Constants.JWT_LOCATIONS,
                           help=Constants.JWT_MESSAGE_401)


def auth_required(cls):
    class NewClass(cls):
        def __getattribute__(self, item):
            attr = super(NewClass, self).__getattribute__(item)
            if '__' not in item and callable(attr):
                return auth_required_method(attr)
            return attr

    return NewClass


def auth_not_required_method(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    wrapper.__auth_not_required__ = True
    return wrapper


def auth_required_method(fn):
    def wrapper(*args, **kwargs):
        # logger.warning(f"  auth now: {fn}, {dir(fn)}")
        if 'Resource.dispatch_request' in str(fn) or (
                '__auth_not_required__' in dir(fn) and fn.__auth_not_required__ is True) or \
                ('__inner__' in dir(fn) and (
                        "Resource.dispatch_request" in str(fn.__inner__) or
                        "__auth_not_required__" in str(fn.__inner__))):
            return fn(*args, **kwargs)
        args_ = auth_reqparse.parse_args(http_error_code=401)
        # logger.info(f"  auth args: {args_}, {fn.__inner__ if '__inner__' in dir(fn) else '(no inner)'}")
        auth = args_.get(Constants.JWT_HEADER_NAME, None)
        if auth is None:
            return make_result(401)
        try:
            if not db.session.token_available(auth):
                raise BadSignature("Token disabled.")
            data = Statics.tjw_access_token.loads(auth)
            if data.get('type', None) != 'access_token':
                raise BadSignature("Token type error.")
        except (BadSignature, BadData, BadHeader, BadPayload) as e:
            return make_result(422, message=f"Bad token: {e}")
        except BadTimeSignature:
            return make_result(423)
        # logger.info(f"data: {data}")
        fn_data = inspect.getfullargspec(fn)
        if 'uid' in fn_data.args:
            kwargs['uid'] = data.get('uid')
        if 'access_token' in fn_data.args:
            kwargs['access_token'] = auth
        return fn(*args, **kwargs)

    wrapper.__inner__ = fn
    return wrapper
