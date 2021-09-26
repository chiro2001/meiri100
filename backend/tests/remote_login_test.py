from gbk_database.config import Constants
from utils.logger import logger
import websocket

websocket.enableTrace(True)
ws: websocket.WebSocketApp = None


def on_message(ws, message):
    print(ws)
    print(message)


def on_error(ws, error):
    print(ws)
    print(error)


def on_close(ws):
    print(ws)
    print("### closed ###")


def start_connection():
    global ws
    url = f"{Constants.LOGIN_SERVER_PROTOCOL}://{Constants.LOGIN_SERVER_HOST}:{Constants.LOGIN_SERVER_PORT}"
    logger.info(url)
    ws = websocket.WebSocketApp(url, on_message=on_message, on_close=on_close, on_error=on_error)


if __name__ == '__main__':
    start_connection()
    ws.run_forever()
