import sys
import os
import json
from utils.logger import logger
from gbk_database.config import Constants
from utils.email_sender import send_email


def send_report(report):
    try:
        if type(report) is dict:
            report = json.dumps(report)
        send_email(sender=Constants.EMAIL_SENDER,
                   password=Constants.EMAIL_SMTP_PASSWORD,
                   text=str(report),
                   title_from=Constants.EMAIL_ERROR_TITLE,
                   title_to=f'Dear {Constants.OWNER}',
                   subject=f"gbk v{Constants.VERSION}的新bug report")
    except Exception as e:
        logger.error('错误信息邮件发送失败！ %s' % e)


def form_report(e):
    report = {
        'string': str(e),
        'file': e.__traceback__.tb_frame.f_globals['__file__'],
        'line': e.__traceback__.tb_lineno
    }
    return report


def report_it(e):
    logger.error("产生了无法预知的错误")
    logger.error("错误内容如下:")
    error = form_report(e)
    logger.error(error['string'])
    logger.error('文件 %s' % error['file'])
    logger.error('行号 %s' % error['line'])
    logger.info('正在尝试反馈错误...')
    logger.info('尝试发送bug报告邮件...')
    send_report(error)
    logger.info('发送bug报告邮件成功')
    try:
        logger.info('尝试把bug发送到远程数据库...')
        from gbk_database.database import DataBase
        _db = DataBase()
        _db.error_report(error)
    except Exception as e2:
        logger.error('把bug发送到远程数据库失败')
        send_report(e2)
    logger.info('发送bug报告完成。')
    sys.exit(1)
