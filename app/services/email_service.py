import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str, html: bool = False):
    """
    发送邮件
    :param to_email: 收件人邮箱
    :param subject: 邮件主题
    :param body: 邮件正文
    :param html: 是否为HTML格式
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = formataddr((settings.EMAIL_FROM_NAME, settings.EMAIL_FROM))
        msg['To'] = to_email
        msg['Subject'] = subject

        if html:
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if settings.SMTP_TLS:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, [to_email], msg.as_string())
        server.quit()
        logger.info(f"邮件已发送到: {to_email}")
        return True
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False

if __name__ == "__main__":
    # 测试参数
    to_email = input("请输入收件人邮箱: ")
    subject = "Gmail SMTP 测试"
    body = "这是一封通过 Gmail SMTP 发送的测试邮件。"
    result = send_email(to_email, subject, body, html=False)
    if result:
        print("邮件发送成功！")
    else:
        print("邮件发送失败，请检查日志和SMTP配置。") 