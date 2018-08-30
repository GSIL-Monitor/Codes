# -*- coding: utf-8 -*-
import os, sys
import traceback
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import requests

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config

#logger
loghelper.init_logger("email_send", stream=True)
logger = loghelper.get_logger("email_send")


def send_mail(from_alias, reply_alias, reply_email, to, subject, content):
    return sendcloud_send_mail(from_alias, reply_alias, reply_email, to, subject, content)
    #return smtp_send_mail(from_alias, reply_alias, reply_email, to, subject, content)

def send_mail_file(from_alias, reply_alias, reply_email, to, subject, content, file):
    return sendcloud_send_mail_attach(from_alias, reply_alias, reply_email, to, subject, content, file)
    #return smtp_send_mail(from_alias, reply_alias, reply_email, to, subject, content)


# smtp方式发送
def smtp_send_mail(from_alias, reply_alias, reply_email, to, subject, content):
    (SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, HOST) = config.get_smtp_config()
    msg = MIMEText(content,_subtype='html',_charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = formataddr((str(Header(from_alias, 'utf-8')), SMTP_USERNAME))
    msg['Reply-to'] = formataddr((str(Header(reply_alias, 'utf-8')), reply_email))
    msg['To'] = to
    try:
        s = smtplib.SMTP()
        s.connect(SMTP_SERVER)  #连接smtp服务器
        s.login(SMTP_USERNAME, SMTP_PASSWORD)  #登陆服务器
        s.sendmail(SMTP_USERNAME, to, msg.as_string())  #发送邮件
        s.close()
        return True
    except:
        traceback.print_exc()
        return False


# sendclound
def sendcloud_send_mail(from_alias, reply_alias, reply_email, to, subject, content):
    url = "http://api.sendcloud.net/apiv2/mail/send"

    API_USER, API_KEY = config.get_sendcloud_config()

    params = {
        "apiUser": API_USER, # 使用api_user和api_key进行验证
        "apiKey" : API_KEY,
        "to" : to, # 收件人地址, 用正确邮件地址替代, 多个地址用';'分隔
        "from": reply_email,
        "fromName": reply_alias,
        "subject" : subject,
        "html": content
    }

    r = requests.post(url, data=params)
    logger.info(r.text)


# sendclound
def sendcloud_send_mail_attach(from_alias, reply_alias, reply_email, to, subject, content, file):
    url = "http://api.sendcloud.net/apiv2/mail/send"

    API_USER, API_KEY = config.get_sendcloud_config()

    params = {
        "apiUser": API_USER, # 使用api_user和api_key进行验证
        "apiKey" : API_KEY,
        "to" : to, # 收件人地址, 用正确邮件地址替代, 多个地址用';'分隔
        "from": reply_email,
        "fromName": reply_alias,
        "subject" : subject,
        "html": content
    }
    files = {'attachments': open(file, 'rb')}  # 文件

    r = requests.post(url, data=params, files=files)
    logger.info(r.text)