import os
import shutil
import io
from zipfile import ZipFile

from utils.logger import logger


def del_file(filepath):
    """
    删除某一目录下的所有文件或文件夹
    :param filepath: 路径
    :return:
    """
    del_list = os.listdir(filepath)
    for f in del_list:
        file_path = os.path.join(filepath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


# 原文链接：https://blog.csdn.net/Jean_821/article/details/104271785
def folder2zip(folder: str) -> bytes:
    data = io.BytesIO()
    file = ZipFile(data, 'w')
    for folder_name, sub_folders, files in os.walk(folder):  # 遍历文件夹
        logger.info('Adding files in ' + folder_name + '...')
        file.write(folder_name)
        for i in files:
            file.write(os.path.join(folder_name, i))
            logger.info('Adding ' + i)
    data.seek(0)
    return data.read()
