# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import traceback
import requests
import json
from lxml import etree
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from aliyun_monitor import AliyunMonitor
import email_send
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
import uuid

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("sms_send", stream=True)
logger = loghelper.get_logger("sms_send")

REGION = "cn-beijing"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"
ACCESS_KEY_ID = "LTAIYT13z6IqNsrr"
ACCESS_KEY_SECRET = "nwlUs3HiDU62lZyagTPFECt3mKRmzL"
acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
region_provider.modify_point(PRODUCT_NAME,REGION,DOMAIN)

# kafka
kafkaConsumer = None

def init_kafka():
    global kafkaConsumer, kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("send_verify_code", group_id="sms_send",
                bootstrap_servers=[url],
                auto_offset_reset='smallest')


SN = "SDK-OPA-010-00007"
PWD = ")-04c)-4"


def send_verify_code(mobile, content):
    flag = False
    if mobile.startswith("110"):
        return True

    try:
        url = "http://sms.combmobile.com/sdk/gxmt"
        pwd = util.md5str(SN+PWD).upper()

        payload = {
            "sn": SN,
            "pwd": pwd,
            "mobile": mobile,
            "content": content.encode("gb2312"),
            "ext": "",
            "stime": "",
            "rrid": ""
        }

        r = requests.post(url, data=payload)
        #logger.info(r.text)
        root = etree.fromstring(r.text.encode("utf8"))
        if root.tag == '{http://tempuri.org/}string':
            return_code = root.text
            return_code_int = int(return_code)
            if return_code_int > 0:
                flag = True
                logger.info("sent ok. return code: %s", return_code)
            else:
                logger.info("sent fail. return code: %s", return_code)
    except:
        traceback.print_exc()
    return flag


# 阿里云
def send_verify_code_by_aliyun(templdate_code, mobile, code):
    if not mobile.startswith("1"):
        return "E"

    # 每日发送数量控制在1W
    conn = db.connect_torndb()
    result = conn.get("select count(*) cnt from sms where createTime>date_sub(now(),interval 24 HOUR) "
                      "and (sent!='E' or sent is null)")
    # TODO 增加IP限制

    conn.close()

    if result["cnt"] > 1000:
        email_send.sendcloud_send_mail("烯牛数据","烯牛数据","noreply@xiniudata.com", "arthur@xiniudata.com", "警告! 阿里短信发送数量超限", "阿里短信发送数量超限")
        return "P"

    # payload = {
    #     'Version': '2016-09-27',
    #     'Action': 'SingleSendSms',
    #     'SignName': '烯牛数据',
    #     'TemplateCode': templdate_code,
    #     'RecNum': mobile,
    #     'ParamString': '{"code":"%s", "product":"%s"}' % (code , '烯牛数据')
    # }
    #
    # if templdate_code != "SMS_25130421":
    #     payload["ParamString"] = '{"code":"%s"}' % code
    #
    # aliyun = AliyunMonitor()
    # post_data = aliyun.make_post_data(payload)
    #
    # request = requests.post("http://sms.aliyuncs.com", post_data)
    # logger.info(request.text)
    # if request.status_code == 200:
    #     return True
    # else:
    #     logger.info("status code: %s ,reason: %s", request.status_code, request.reason)
    #     return False
    try:
        result = new_send_verify_code_by_aliyun_20171225(templdate_code, mobile, code)
    except Exception, e:
        logger.info(e)
        traceback.print_stack()
        return False
    data = json.loads(result)
    logger.info("result: %s", data["Code"])
    if data["Code"] == "OK":
        return True

    return False


# 阿里云新接口
def new_send_verify_code_by_aliyun_20171225(template_code, phone_number, code):
    # logger.info("%s, %s, %s", template_code, phone_number,code)
    business_id = uuid.uuid1()
    smsRequest = SendSmsRequest.SendSmsRequest()
    smsRequest.set_TemplateCode(template_code)
    smsRequest.set_TemplateParam('{"code":"%s", "product":"%s"}' % (code , '烯牛数据'))
    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)
    # 短信签名
    smsRequest.set_SignName('烯牛数据');
    smsRequest.set_PhoneNumbers(phone_number)
    # 发送请求
    smsResponse = acs_client.do_action_with_exception(smsRequest)
    return smsResponse


def check(_id, phone):
    logger.info("check: %s", phone)
    if phone is None or phone.strip() == "":
        return False
    conn = db.connect_torndb()
    # 一分钟内是否发过
    item = conn.get("select * from sms where phone=%s and createTime>date_sub(now(),interval 1 MINUTE) and id<%s limit 1", phone, _id)
    if item is not None:
        logger.info(item)
        conn.close()
        return False

    # 一小时内的次数不能超过10次
    result = conn.get("select count(*) cnt from sms where phone=%s and createTime>date_sub(now(),interval 60 MINUTE)", phone)
    if result["cnt"] >= 11:
        logger.info(result)
        conn.close()
        return False

    conn.close()
    return True


def process(_id):
    conn = db.connect_torndb()
    item = conn.get("select * from sms where id=%s", _id)
    if item is None:
        conn.close()
        return

    phone = item["phone"]
    if check(_id, phone) is False:
        conn.update("update sms set sent='E',sendTime=now() where id=%s", item["id"])
        conn.close()
        return

    flag = True
    if item["type"] == 62010:
        #注册时手机号码验证
        if item["createTime"] + datetime.timedelta(minutes=1) < datetime.datetime.now():
            conn.update("update sms set sent='T',sendTime=now() where id=%s",item["id"])
            conn.close()
            return
        # content = u"【烯牛数据】验证码：%s (10分钟内有效) 立即开启新的工作方式！" % item["code"]
        # flag = send_verify_code(item["phone"], content)
        flag = send_verify_code_by_aliyun("SMS_67286279", item["phone"], item["code"])

    elif item["type"] == 62020:
        #忘记密码
        if item["createTime"] + datetime.timedelta(minutes=1) < datetime.datetime.now():
            conn.update("update sms set sent='T',sendTime=now() where id=%s",item["id"])
            conn.close()
            return
        # content = u"【烯牛数据】修改密码验证码：%s 该验证码10分钟内有效，不要告诉别人哦！" % item["code"]
        # flag = send_verify_code(item["phone"], content)
        flag = send_verify_code_by_aliyun("SMS_67101390", item["phone"], item["code"])
    elif item["type"] == 62030:
        #修改手机号码验证
        if item["createTime"] + datetime.timedelta(minutes=1) < datetime.datetime.now():
            conn.update("update sms set sent='T',sendTime=now() where id=%s",item["id"])
            conn.close()
            return
        # content = u"【烯牛数据】验证码：%s (10分钟内有效)" % item["code"]
        # flag = send_verify_code(item["phone"], content)
        flag = send_verify_code_by_aliyun("SMS_67286282", item["phone"], item["code"])
    elif item["type"] == 62040:
        #手机端注册登录验证码
        flag = send_verify_code_by_aliyun("SMS_25130421", item["phone"], item["code"])

    if flag is True:
        conn.update("update sms set sent='Y',sendTime=now() where id=%s",item["id"])
    elif flag is False:
        if item["sendFailCount"] is None:
            sendFailCount = 0
        else:
            sendFailCount = item["sendFailCount"] + 1
        conn.update("update sms set sent='N',sendTime=now(), sendFailCount=%s where id=%s",sendFailCount,item["id"])
    elif flag == 'P':
        conn.update("update sms set sent='P',sendTime=now() where id=%s", item["id"])
    else:
        conn.update("update sms set sent='E',sendTime=now() where id=%s", item["id"])
    conn.close()


def process_all():
    flag = False
    conn = db.connect_torndb()
    items = conn.query("select * from sms where "
                       "(sent is null or sent='N') and "
                       "(sendFailCount is null or sendFailCount<3) and "
                       "createTime>date_sub(now(),interval 60 SECOND)")
    conn.close()
    for item in items:
        process(item["id"])
        flag = True

    return flag


def run():
    init_kafka()

    while True:
        try:
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)
                    _type = msg["type"]
                    kafkaConsumer.commit()
                    if _type == "sms":
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


if __name__ == "__main__":
    # print send_verify_code_by_aliyun_20171225("SMS_67286279", "13818287827", "4089")
    if len(sys.argv) <= 1:
        run()
    else:
        process(sys.argv[1])
