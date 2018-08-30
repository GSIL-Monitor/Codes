#coding=utf-8

import json

from umessage.pushclient import PushClient
from umessage.iospush import *
from umessage.androidpush import *

from umessage.errorcodes import UMPushError, APIServerErrorCode

#注意andorid和ios是不同的appkey和appMasterSecret。 在不同需求下换成各自的appkey。
iOSappKey = '59117c86aed1797f5d0001c6'
iOSappMasterSecret = 'lqxgyijzh9xujxmrc1ewbyud7tsw9oli'

#烯牛数据·个人版
iOSappKey_personal = '5b0e9eaaf29d984fdf000075'
iOSappMasterSecret_personal = 'puktayih1qtyzcjisqukr4vwe7yv1sdf'

#ios
def sendIOSUnicast(message, badge, device_token, messageType="topic", test=False, data={}):
    unicast = IOSUnicast(iOSappKey, iOSappMasterSecret)
    unicast.setDeviceToken(device_token)
    unicast.setAlert(message)
    unicast.setBadge(badge)
    unicast.setCustomizedField("messageType", messageType)
    for key, value in data.items():
        unicast.setCustomizedField(key, value)
    if test:
        unicast.setTestMode()
    else:
        unicast.setProductionMode()
    pushClient = PushClient()
    ret = pushClient.send(unicast)
    unicast.statuCode = ret.status_code
    printResult(ret)


def sendContentAvailableIOSUnicast(device_token, messageType="topic", test=False):
    unicast = IOSUnicast(iOSappKey, iOSappMasterSecret)
    unicast.setDeviceToken(device_token)
    unicast.setContentAvailable(1)
    unicast.setCustomizedField("messageType", messageType)
    if test:
        unicast.setTestMode()
    else:
        unicast.setProductionMode()
    pushClient = PushClient()
    ret = pushClient.send(unicast)
    unicast.statuCode = ret.status_code
    printResult(ret)

def sendIOSBroadcast(app, message, badge, messageType="hot_news", test=False, data={}):
    appKey = iOSappKey
    appMasterSecret = iOSappMasterSecret
    if app == "personal":
        appKey = iOSappKey_personal
        appMasterSecret = iOSappMasterSecret_personal
    broadcast = IOSBroadcast(appKey, appMasterSecret)
    broadcast.setAlert(message)
    broadcast.setBadge(badge)
    broadcast.setCustomizedField("messageType", messageType)
    for key, value in data.items():
        broadcast.setCustomizedField(key, value)
    if test:
        broadcast.setTestMode()
    else:
        broadcast.setProductionMode()
    pushClient = PushClient()
    ret = pushClient.send(broadcast)
    printResult(ret)


def printResult(ret):
    print "http status code: %s" % ret.status_code

    if ret.text != "":
        ret_json = json.loads(ret.text)
        if ret_json["ret"] == IOSNotification.CONSTR_STATUS_SUCCESS:
            if 'msg_id' in ret_json['data']:
                print "msgId: %s" % ret_json['data']['msg_id']
            if 'task_id' in ret_json['data']:
                print "task_id: %s" % ret_json['data']['task_id']
        elif ret_json["ret"] == IOSNotification.CONSTR_STATUS_FAIL:
            errorcode = int(ret_json["data"]["error_code"])
            print "error Code: %s, detail: %s" % (errorcode, APIServerErrorCode.errorMessage(errorcode));


if __name__ == '__main__':
    # device_token = "46c0dd215874cc2b045af11643c910cde479fc34fd3c4249ee5596d12b6e7134"
    # sendIOSUnicast(u"这是一个测试消息", 11, device_token, messageType="topic", test=False)
    # sendContentAvailableIOSUnicast(device_token, "company", test=True)
    data = {"newsId": "5b0e3e08deb471013c80759e"}
    sendIOSBroadcast("personal", "Uber新增“紧急”按钮，可在应用内直接报警", 0, messageType="hot_news", test=True, data=data)
