# coding=utf-8

import sys, os
import base64
import hmac
from hashlib import sha1
import urllib
import time
import uuid
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import config

(ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, HOST) = config.get_aliyun_smtp_config()

class AliyunMonitor:
    def __init__(self):
        self.access_id = ALIYUN_ACCESS_KEY_ID
        self.access_secret = ALIYUN_ACCESS_KEY_SECRET

    # 签名
    def sign(self, accessKeySecret, parameters):
        sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
        canonicalizedQueryString = ''

        for (k, v) in sortedParameters:
            canonicalizedQueryString += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)

        stringToSign = 'POST&%2F&' + self.percent_encode(canonicalizedQueryString[1:])

        h = hmac.new(accessKeySecret + "&", stringToSign, sha1)
        signature = base64.encodestring(h.digest()).strip()
        return signature

    def percent_encode(self, encodeStr):
        encodeStr = str(encodeStr)
        # 下面这行挺坑的，使用上面文章中的方法会在某些情况下报错，后面详细说明
        res = urllib.quote(encodeStr.decode('utf-8').encode('utf-8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    def make_post_data(self, params):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        parameters = {
            'Format': 'JSON',
            'Version': '2015-11-23',
            'AccessKeyId': self.access_id,
            'SignatureVersion': '1.0',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': str(uuid.uuid1()),
            'Timestamp': timestamp,
        }
        for key in params.keys():
            parameters[key] = params[key]

        signature = self.sign(self.access_secret, parameters)
        parameters['Signature'] = signature

        # return parameters
        # url = self.url + "/?" + urllib.urlencode(parameters)
        return parameters
