import sys
import traceback


def get_traceback():
    traceback.print_exc()  # 打印异常信息
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error = str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))  # 将异常信息转为字符串
    return error
