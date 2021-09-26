import os
from flask import *
from utils.logger import logger
from utils.file_static import is_file_path_legal, get_static_file_path
from gbk_database.config import config

app = Flask(__name__, static_folder=config.data['file_server']['static_path'])


# 统一错误处理信息
@app.errorhandler(404)
def handler_404(error):
    logger.error(f"{error}")
    return f"<p>{error}</p><br><p>你来到了知识的荒原——</p>"


@app.route("/<path:path>")
def file_server(path: str):
    if path in config.data['file_server']['routers']:
        return index()
    file_path = get_static_file_path(config.data['file_server']['static_path'], path)
    if not is_file_path_legal(config.data['file_server']['static_path'], path):
        logger.warning(f'visiting illegal path: {file_path}')
        logger.warning(f'visiting illegal absolutely path: {os.path.abspath(file_path)}')
        return handler_404("路径不合法"), 404
    # 这里有些问题...得上一层文件夹
    return send_file(os.path.join('../', get_static_file_path(config.data['file_server']['static_path'], path)))


@app.route("/")
def index():
    return file_server(config.data['file_server']['index'])


if __name__ == '__main__':
    app.run("0.0.0.0", port=8080)
