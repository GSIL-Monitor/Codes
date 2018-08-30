# -*- coding: utf8 -*-
# Create your tests here.
from autocode import Authcode

import requests
import pprint
import json

import M2Crypto
from Crypto.PublicKey import RSA

from urllib import unquote
from urllib import quote

pub_key = M2Crypto.RSA.load_pub_key('public_526cfb78fc944cffafccfc30991bda53.key.pem')
print pub_key
des_key=Authcode.random(32)

des_key_encrypted = pub_key.public_encrypt(des_key,M2Crypto.RSA.pkcs1_padding).encode("base64")
print "add"
print des_key_encrypted
print "add"
uid = '526cfb78fc944cffafccfc30991bda53'
params = {  
    'uid': uid,
    'service': 'getRegisterChangeInfo',
    'params': {
        'entName': '上海汇翼信息科技有限公司',
    },
    'user': {
        "id": 139,
        "name": '烯牛数据'
    }
}
data = json.dumps(params)
data_encrypted = Authcode.quantum_encode(data, des_key)
map1 ={'key': des_key_encrypted,
        'value': data_encrypted,
              }

_data = json.dumps(map1)
res = requests.post('http://api.liangzisj.com/service',
{
    "uid":uid,
    "data":_data
})
data = json.loads(unquote(res.text))

print('返回的数据: ')

des_key= pub_key.public_decrypt(data["key"].decode("base64"),M2Crypto.RSA.pkcs1_padding)
print unquote(Authcode.quantum_decode(data['value'], des_key))
