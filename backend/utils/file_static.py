import os
import re


# 检查请求路径有效性
def is_file_path_legal(static_path: str, path: str):
    # 文件要存在
    file_path = get_static_file_path(static_path, path)
    # logger.info('abspath: %s' % os.path.abspath(file_path))
    # logger.info('os.path.exists(file_path): %s' % os.path.exists(file_path))
    # logger.info('os.path.isfile(file_path): %s' % os.path.isfile(file_path))
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        return False
    # 不能使用两个点向上目录
    if '..' in re.split(r"[/\\]", file_path):
        return False
    return True


def get_static_file_path(static_path: str, path: str):
    return os.path.join(static_path, path)
