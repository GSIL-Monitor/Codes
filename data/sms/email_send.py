# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import traceback
from mako.template import Template
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import requests, json
from aliyun_monitor import AliyunMonitor

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("email_send", stream=True)
logger = loghelper.get_logger("email_send")

#smtp
(SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, HOST) = config.get_smtp_config()

# kafka
kafkaConsumer = None


def init_kafka():
    global kafkaConsumer, kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("send_verify_code", group_id="email_send",
                bootstrap_servers=[url],
                auto_offset_reset='smallest')


def send_mail(from_alias, reply_alias, reply_email, to, subject, content):
    return sendcloud_send_mail(from_alias, reply_alias, reply_email, to, subject, content)
    #return smtp_send_mail(from_alias, reply_alias, reply_email, to, subject, content)

# smtp方式发送
def smtp_send_mail(from_alias, reply_alias, reply_email, to, subject, content):
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


def sendcloud_send_mail(from_alias, reply_alias, reply_email, to, subject, content):
    url = "http://api.sendcloud.net/apiv2/mail/send"

    API_USER, API_KEY = config.get_sendcloud_config()

    params = {
        "apiUser": API_USER, # 使用api_user和api_key进行验证
        "apiKey" : API_KEY,
        "to" : to, # 收件人地址, 用正确邮件地址替代, 多个地址用';'分隔
        "from": reply_email,
        "fromName": reply_alias,
        #"from" : "noreply@sendmail1.xiniudata.com", # 发信人, 用正确邮件地址替代
        #"fromName" : from_alias,
        #"replyTo": reply_email,
        "subject" : subject,
        "html": content
    }

    r = requests.post(url, data=params)
    print r.text


# 阿里云邮件推送-使用api
# def send_mail_by_aliyun(to, subject, content):
#     payload = {
#         'Action': 'SingleSendMail',
#         'AccountName': 'noreply@sendmail.xiniudata.com',
#         'ReplyToAddress': 'true',
#         'AddressType': 0,
#         'ToAddress': to,
#         'FromAlias': '烯牛数据',
#         'Subject': subject,
#         'HtmlBody': content
#     }
#
#     aliyun = AliyunMonitor()
#     post_data = aliyun.make_post_data(payload)
#
#     request = requests.post("http://dm.aliyuncs.com", post_data)
#
#     # print request.text
#     return True


def process(_id, manual=False):
    conn = db.connect_torndb()
    item = conn.get("select * from email_task where id=%s", _id)
    if item is None:
        conn.close()
        return

    flag = True
    if item["type"] == 63010:
        #找回密码
        if item["createTime"] + datetime.timedelta(minutes=10) < datetime.datetime.now():
            conn.update("update email_task set sent='T',sendTime=now() where id=%s",item["id"])
            conn.close()
            return
        user = conn.get("select * from user where email=%s and (emailVerify='Y' or emailVerify='O')", item["email"])
        if user:
            data ={
                "host":HOST,
                "user":user,
                "task":item
            }
            t = Template(filename='template/findpwd.html', input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
            content = t.render(data=data)
            #logger.info(content)
            send_mail("烯牛数据","烯牛数据","noreply@xiniudata.com", item["email"], "烯牛数据-找回密码", content)
    elif item["type"] == 63020:
        #注册成功后的欢迎邮件
        user = conn.get("select * from user where id=%s", item["userId"])
        if user:
            data ={
                "host":HOST,
                "user":user
            }
            if user["userIdentify"] == 61010:
                template_file = "template/registration_welcome_investor.html"
                t = Template(filename=template_file, input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
                content = t.render(data=data)
                #logger.info(content)
                send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", item["email"], "烯牛数据-欢迎进入量化VC时代", content)
            elif user["userIdentify"] == 61020:
                template_file = "template/registration_welcome_fa.html"
                t = Template(filename=template_file, input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
                content = t.render(data=data)
                #logger.info(content)
                send_mail("烯牛数据 产品经理Teddy", "烯牛数据 产品经理Teddy", "teddy@xiniudata.com", item["email"], "烯牛数据-欢迎进入量化VC时代", content)
    elif item["type"] == 63030:
        #投资人认证通过的通知邮件
        user = conn.get("select * from user where id=%s", item["userId"])
        if user:
            data ={
                "host":HOST,
                "user":user
            }
            t = Template(filename='template/verified_investor_inform.html', input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
            content = t.render(data=data)
            #logger.info(content)
            send_mail("烯牛数据 李锦香", "烯牛数据 李锦香", "avery@xiniudata.com", item["email"], "烯牛数据-投资人认证通过，感谢你的信任！", content)
    elif item["type"] == 63040:
        #邮箱验证
        if item["createTime"] + datetime.timedelta(minutes=10) < datetime.datetime.now():
            conn.update("update email_task set sent='T',sendTime=now() where id=%s",item["id"])
            conn.close()
            return
        user = conn.get("select * from user where id=%s", item["userId"])
        data ={
            "host":HOST,
            "user":user,
            "task":item
        }
        t = Template(filename='template/email_verify.html', input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
        content = t.render(data=data)
        #logger.info(content)
        send_mail("烯牛数据","烯牛数据","noreply@xiniudata.com",item["email"], "烯牛数据-绑定邮箱", content)
    elif item["type"] == 63050:
        #用户邀请同事发邮件
        user = conn.get("select * from user where id=%s", item["userId"])
        data ={
            "host":HOST,
            "task":item,
            "user":user
        }
        t = Template(filename='template/user_invite_colleague.html', input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
        content = t.render(data=data)
        #logger.info(content)
        send_mail("烯牛数据","烯牛数据","noreply@xiniudata.com",item["email"], "%s邀请您加入烯牛数据" % user["username"], content)
    elif item["type"] == 63060:
        #［开始试用］机构版，给同机构用户发邀请邮件，邀请他们来体验机构版
        # 查询所有同机构的用户,给他们发邮件, 不能给自己发
        user = conn.get("select * from user where id=%s", item["userId"])
        org = conn.get("select o.* from organization o join user_organization_rel r on o.id=r.organizationId "
                       "where r.userId=%s and o.grade=33010", user["id"])
        if org:
            left_days = (org["serviceEndDate"] - datetime.datetime.now()).days
            logger.info("left_days: %s", left_days)
            if left_days <= 0:
                left_days = 1

            org_users = get_not_trial_org_users(org)
            for u in org_users:
                if u["id"] == user["id"]:
                    continue
                #if u["email"] != "avery@xiniudata.com":
                #    continue
                data ={
                    "host":HOST,
                    "task":item,
                    "from_user":user,
                    "to_user":u,
                    "org":org,
                    "left_days":left_days
                }
                logger.info("%s %s", u['username'], u["email"])
                t = Template(filename='template/invite_trial_enterprise_version.html', input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
                content = t.render(data=data)
                #logger.info(content)
                send_mail("烯牛数据","烯牛数据","noreply@xiniudata.com",u["email"], "%s发起了「烯牛数据」机构版试用，邀您体验量化VC" % user["username"], content)
    elif item["type"] == 63070:
        # 还有10天到期
        # 查询所有同机构的用户,给他们发邮件
        org = conn.get("select * from organization where id=%s", item["orgId"])
        if org:
            left_days = (org["serviceEndDate"] - datetime.datetime.now()).days
            logger.info("left_days: %s", left_days)
            if left_days <= 0:
                left_days = 1

            org_users = get_all_org_users(org)
            for u in org_users:
                # if u["email"] != "862911876@qq.com":
                #    continue
                data ={
                    "host":HOST,
                    "task":item,
                    "to_user":u,
                    "org":org,
                    "left_days":left_days
                }
                logger.info("%s %s", u['username'], u["email"])
                t = Template(filename='template/trial_enterprise_will_expire.html', input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
                content = t.render(data=data)
                #logger.info(content)
                send_mail("烯牛数据","烯牛数据","noreply@xiniudata.com",u["email"], "「烯牛数据」机构版试用还剩【%s】天，立即升级为正式版" % left_days, content)
    elif item["type"] == 63080:
        # 到期
        org = conn.get("select * from organization where id=%s", item["orgId"])
        if org:
            org_users = get_all_org_users(org)
            for u in org_users:
                # if u["email"] != "862911876@qq.com":
                #    continue
                data = {
                    "host": HOST,
                    "task": item,
                    "to_user": u,
                    "org": org
                }
                logger.info("%s %s", u['username'], u["email"])
                t = Template(filename='template/trial_enterprise_expired.html', input_encoding='utf-8',
                             output_encoding='utf-8', encoding_errors='replace')
                content = t.render(data=data)
                # logger.info(content)
                send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", u["email"],
                          "「烯牛数据」机构版试用已结束，立即升级为正式版 ", content)


    if flag:
        conn.update("update email_task set sent='Y',sendTime=now() where id=%s",item["id"])
    else:
        if item["sendFailCount"] is None:
            sendFailCount = 0
        else:
            sendFailCount = item["sendFailCount"] + 1
        conn.update("update email_task set sent='N',sendTime=now(), sendFailCount=%s where id=%s",sendFailCount,item["id"])
    conn.close()


def get_not_trial_org_users(org):
    # 包括认证的和潜在的
    conn = db.connect_torndb()
    org_users = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                           "where r.organizationId=%s and r.active='N'", org["id"])
    org_users1 = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                            "join organization o on r.organizationId=o.id "
                            "where o.grade=33020 and o.id != %s and o.name=%s",
                            org["id"], org["name"])
    merge_users(org_users, org_users1)
    if org["emailDomain"] is not None and org["emailDomain"].strip() != "":
        org_users2 = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                                "join organization o on r.organizationId=o.id "
                                "where o.grade=33020 and o.id != %s and o.emailDomain=%s",
                                org["id"], org["emailDomain"])
        merge_users(org_users, org_users2)
    conn.close()

    return org_users


def get_all_org_users(org):
    # 包括认证的和潜在的
    conn = db.connect_torndb()
    org_users = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                           "where r.organizationId=%s", org["id"])
    org_users1 = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                            "join organization o on r.organizationId=o.id "
                            "where o.grade=33020 and o.id != %s and o.name=%s",
                            org["id"], org["name"])
    merge_users(org_users, org_users1)
    if org["emailDomain"] is not None and org["emailDomain"].strip() != "":
        org_users2 = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                                "join organization o on r.organizationId=o.id "
                                "where o.grade=33020 and o.id != %s and o.emailDomain=%s",
                                org["id"], org["emailDomain"])
        merge_users(org_users, org_users2)
    conn.close()

    return org_users

def merge_users(to_list, from_list):
    for user in from_list:
        exist = False
        for u in to_list:
            if user["id"] == u["id"]:
                exist = True
        if exist is False:
            to_list.append(user)

def process_all():
    flag = False
    conn = db.connect_torndb()
    items = conn.query("select * from email_task where "
                       "(sent is null or sent='N') and "
                       "(sendFailCount is null or sendFailCount<3)")
    conn.close()
    for item in items:
        process(item["id"])
        flag = True

    return flag


def process_user_enterprise_trial_apply(_id):
    emails = [
        "avery@xiniudata.com",
        "charlotte@xiniudata.com",
        "arthur@xiniudata.com",
        "wei.gao@xiniudata.com"
    ]
    conn = db.connect_torndb()
    application = conn.get("select * from user_enterprise_trial_apply where id=%s", _id)
    conn.close()

    data = {
        "application": application,
    }
    # logger.info("%s %s", application['userId'], application["username"], application["orgName"])
    t = Template(filename='template/user_enterprise_trial_apply.html', input_encoding='utf-8',
                 output_encoding='utf-8', encoding_errors='replace')
    content = t.render(data=data)
    # logger.info(content)
    for email in emails:
        send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", email,
                  "【%s】提交机构版使用申请" % application["username"], content)


def run():
    init_kafka();

    while True:
        try:
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)
                    _type = msg["type"]
                    _subType = msg.get("subType")
                    kafkaConsumer.commit()
                    if _type == "email":
                        if _subType == "user_enterprise_trial_apply":
                            process_user_enterprise_trial_apply(msg["id"])
                        else:
                            while True:
                                flag = process_all()
                                if not flag:
                                    break
                except:
                    traceback.print_exc()
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()


def test():
    data ={
        "host":HOST,
        "userId":1,
        "oneTimePwd":"2342"
    }
    t = Template(filename='template/findpwd.html', input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
    content = t.render(data=data)
    logger.info(content)
    #send_mail_by_aliyun("862911876@qq.com", "找回密码", content)
    send_mail("862911876@qq.com", "找回密码", content)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        run()
    else:
        process(sys.argv[1], manual=True)