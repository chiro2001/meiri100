import json
import os

import requests
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosClientError

import secrets
from gbk_database.config import Constants, Statics
from utils.logger import logger

cos_config: CosConfig = None
cos_client: CosS3Client = None


def init_auth():
    global cos_config, cos_client
    try:
        resp = json.loads(requests.get(secrets.SECRET_COS_API + secrets.SECRET_COS_PASSWORD).content)
    except Exception as e:
        logger.error(e)
        return
    Statics.cos_secret_id, Statics.cos_secret_key = resp['id'], resp['key']
    cos_config = CosConfig(Region=secrets.SECRET_COS_REGION, SecretId=Statics.cos_secret_id,
                           SecretKey=Statics.cos_secret_key)
    cos_client = CosS3Client(cos_config)
    logger.info('COS loaded done')


def upload_file(key: str, data: bytes):
    try:
        response = cos_client.put_object(
            Bucket=secrets.SECRET_COS_BUCKET,
            Body=data,
            Key=key,
            StorageClass='STANDARD',
            EnableMD5=False
        )
        if len(data) == 0:
            logger.warning('uploading empty data!')
        logger.info(f'uploaded {len(data)} bytes to https://{secrets.SECRET_COS_BUCKET}.cos.{secrets.SECRET_COS_REGION}.myqcloud.com/{key}, {response}')
    except Exception as e:
        logger.error(f'uploading error: {e}')


# # 由主进程启动的进程不重新初始化COS
# if os.getenv(Constants.PROC_DISMISS_COS) is None:
#     os.environ.setdefault(Constants.PROC_DISMISS_COS, f"{os.getpid()}")
#
# if os.getenv(Constants.PROC_DISMISS_REBASE) != f"{os.getppid()}":
#     init_auth()

init_auth()