# -*- coding: utf-8 -*-
import sys, os, time, datetime
from autocode import Authcode

import requests
import pprint
import json

import M2Crypto
from Crypto.PublicKey import RSA

from urllib import unquote
from urllib import quote

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db,util,url_helper,download


#logger
loghelper.init_logger("liangzi_crawler", stream=True)
logger = loghelper.get_logger("liangzi_crawler")

SOURCE = 13091
TYPE = 36008

def liangziCrawler(name,infos=[]):
    result = {}
    if len(infos) == 0:
        infos = ['getRegistInfo', 'getShareHolderInfo', 'getMainManagerInfo',
                 'getRegisterChangeInfo', 'getInvestmentAbroadInfo']
    pub_key = M2Crypto.RSA.load_pub_key('public_526cfb78fc944cffafccfc30991bda53.key.pem')
    uid = '526cfb78fc944cffafccfc30991bda53'
    for info in infos:
        des_key = Authcode.random(32)
        des_key_encrypted = pub_key.public_encrypt(des_key, M2Crypto.RSA.pkcs1_padding).encode("base64")
        params = {
            'uid': uid,
            'service': info,
            'params': {
                'entName': name,
            },
            'user': {
                "id": 139,
                "name": '烯牛数据'
            }
        }
        data = json.dumps(params)
        data_encrypted = Authcode.quantum_encode(data, des_key)
        map1 = {'key': des_key_encrypted,
                'value': data_encrypted,
                }

        _data = json.dumps(map1)
        try:
            res = requests.post('http://api.liangzisj.com/service',
                            {
                                "uid": uid,
                                "data": _data
                            },
                            timeout=20)

            data = json.loads(unquote(res.text))
            des_key = pub_key.public_decrypt(data["key"].decode("base64"), M2Crypto.RSA.pkcs1_padding)
            ra =  unquote(Authcode.quantum_decode(data['value'], des_key))
            logger.info(ra)
            jra = json.loads(ra)
            if jra.has_key("RESULTDATA") is True:
                result[info] =  jra["RESULTDATA"]
        except:
            pass
    return result

def save(company_name, content):
    if content.has_key("getRegistInfo") is True:
        if isinstance(content["getRegistInfo"], dict) is True and content["getRegistInfo"].has_key("ERRORCODE"):
            logger.info("WRONG: %s, %s", content["getRegistInfo"]["ERRORCODE"], content["getRegistInfo"]["ERRORVALUE"])
        else:
            collection_content = {
                "date":datetime.datetime.now(),
                "source":SOURCE,
                "type":36008,
                "url":None,
                "content":content,
                "key": company_name
            }

            mongo = db.connect_mongo()
            if mongo.raw.projectdata.find_one({"source":SOURCE, "type":TYPE, "key":company_name}) is not None:
                mongo.raw.projectdata.delete_one({"source":SOURCE, "type":TYPE, "key":company_name})
            mongo.raw.projectdata.insert_one(collection_content)
            mongo.close()


def start_run():
    while True:
        logger.info("liangzi crawler start...")
        conn = db.connect_torndb()
        # company_aliases = conn.query("select * from corporate_alias where type=12010 and "
        #                              "(gongshangCheckTime is null or gongshangCheckTime < date_sub(now(),interval 20 day)) "
        #                              "order by id desc limit %s", concurrency * 5)

        company_aliases = conn.query("select * from corporate_alias where gongshangCheckTime is null")

        for company in company_aliases:
            if company["name"] is None or company["name"].strip() == "":
                pass
            else:
                logger.info("crawler: %s", company["name"])
                r =liangziCrawler(company["name"],[])
                save(company["name"], r)
            sql = "update corporate_alias set gongshangCheckTime=now() where id=%s"
            conn.update(sql, company["id"])

        conn.close()

        # mongo = db.connect_mongo()
        # collection_name = mongo.info.gongshang_name
        # cnames = list(collection_name.find({
        #     "type": 1,
        #     "$or": [
        #         {"lastCheckTime": None},
        #         {"lastCheckTime": {"$lt": datetime.datetime.now() - datetime.timedelta(days=7)}}
        #     ]
        # }).limit(200))
        #
        # for cname in cnames:
        #     if cname["name"] is None or cname["name"].strip() == "":
        #         continue
        #     logger.info("crawler type 1: %s", cname["name"])
        #     r = liangziCrawler(cname["name"], [])
        #     save(cname["name"], r)
        #     collection_name.update_one({"_id": cname["_id"]},{'$set': {"lastCheckTime": datetime.datetime.now()}})
        # mongo.close()

        logger.info("liangzi crawler end...")

        time.sleep(1*60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        infos = []
        r = liangziCrawler(param, infos)
        for ri  in r:
            logger.info("%s", ri)
            logger.info(r[ri])
        # save(param, r)
    else:
        # pass
        start_run()