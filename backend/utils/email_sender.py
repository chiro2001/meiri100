import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from gbk_database.config import Constants


def send_email(sender: str, password: str, text: str, title_from: str, title_to: str, subject: str):
    msg = MIMEText(text, 'plain', 'utf-8')
    msg['From'] = formataddr((title_from, sender))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = formataddr((title_to, sender))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = subject  # 邮件的主题，也可以说是标题
    server = smtplib.SMTP_SSL(Constants.EMAIL_SMTP_SSL, Constants.EMAIL_SMTP_PORT)  # 发件人邮箱中的SMTP服务器，端口是465
    server.login(sender, password)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(sender, [sender, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接


if __name__ == '__main__':
    send_email(sender=Constants.EMAIL_SENDER,
               password=Constants.EMAIL_SMTP_PASSWORD,
               text="test text",
               title_from=Constants.EMAIL_ERROR_TITLE,
               title_to=f'Dear {Constants.OWNER}',
               subject=f"gbk v{Constants.VERSION}的新bug report")
