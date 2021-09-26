from data_apis.api import API
from gbk_scheduler.task_pool import task_sys_pool
from utils.api_tools import *
from gbk_daemon.daemon import daemon, DaemonBean
from gbk_exceptions import *
from utils.formats import cookies_check


def post_cookies(uid: int, cookies: str, use_this_cookies: bool = True):
    # 检查格式，提取
    cookies = cookies_check(cookies)
    if cookies is None:
        return make_result(400)
    # print(cookies)
    if use_this_cookies:
        db.daemon.save(uid, cookies, data_type='cookies')
    try:
        d = daemon.get_daemon(uid, init_new=True, cookies=cookies)
    except (GBKLoginError, GBKPermissionError) as e:
        logger.error(f"error updating daemon: {e}")
        # 删除整个daemon
        daemon.delete_daemon(uid)
        return make_result(400, message=f'{e}')
    # 更新 shops 表
    api = API.from_cookies(cookies)
    if api.shop_id is not None:
        shop_info = api.shop_info
        # TODO: 添加系统线程使得cookies始终最新，不是最新则删除数据
        shop_info.update({'cookies': cookies})
        d.shops[str(api.shop_id)] = shop_info
        d.save(select='shops')
    # 添加到最新 uid 列表
    task_sys_pool.update_uid(uid)
    return make_result()


class RemoteLoginAPI(Resource):
    args_set_cookies = reqparse.RequestParser().add_argument("cookies", type=str, required=True, location=["json", ])
    # args_delete_cookies = reqparse.RequestParser() \
    #     .add_argument("cookies", type=str, required=False, location=["json", ]) \
    #     .add_argument("shop_id", type=int, required=False, location=["json", ])

    @auth_required_method
    def get(self, uid: int):
        """
        检查远程登录状态
        """
        d: DaemonBean = daemon.get_daemon(uid)
        if d is None:
            return make_result(200, message='has not remote login yet')
        return make_result(200, data=d.__getstate__())

    def patch(self):
        """
        获取远程服务器信息
        """
        url = Constants.LOGIN_SERVER
        if url is None:
            url = f"{Constants.LOGIN_SERVER_PROTOCOL}://{Constants.LOGIN_SERVER_HOST}:{Constants.LOGIN_SERVER_PORT}"
        return make_result(data={
            'server': url,
            'servers': [
                {
                    'url': url
                }
            ]
        })

    # Bug: DELETE 请求并不能含有 body，所以不能在 body 解析 json 。
    # @args_required_method(args_delete_cookies)
    @auth_required_method
    def delete(self, uid: int):
        """
        删除登录凭据
        """
        # cookies = self.args_delete_cookies.parse_args().get('cookies')
        # shop_id = self.args_delete_cookies.parse_args().get('shop_id')
        cookies = None
        shop_id = None
        if cookies is None and shop_id is None:
            # 不指定就删除整个daemon
            if not daemon.delete_daemon(uid):
                return make_result(500)
        else:
            # 指定了就只删除指定部分
            if shop_id is None:
                api = API.from_cookies(cookies)
                if api.shop_id is None:
                    return make_result(400)
                shop_id = api.shop_id
            d = daemon.get_daemon(uid)
            d.shops = {str(shop['shopId']): shop for shop in d.shops if shop['shopId'] != shop_id}
            d.cookies = None if d.shop_info['shopId'] == shop_id else d.cookies
            d.shop_info = None if d.shop_info['shopId'] == shop_id else d.shop_info
            daemon.delete_daemon(uid)
            d.save()
        return make_result()

    @args_required_method(args_set_cookies)
    @auth_required_method
    def post(self, uid: int):
        """
        设置 Cookies
        """
        cookies = self.args_set_cookies.parse_args().get('cookies')
        return post_cookies(uid, cookies)
