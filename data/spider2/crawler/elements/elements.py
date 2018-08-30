# -*- coding: utf-8 -*-
import sys, os, time, datetime

import requests
import pprint
import json

from urllib import unquote
from urllib import quote

from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download

import hmac
import hashlib

# logger
loghelper.init_logger("elements_crawler", stream=True)
logger = loghelper.get_logger("elements_crawler")

SOURCE = 13092
TYPE = 36008
userid = 'HZ91i1a'
userkey = 'nbgHUmTH'


def compare():
    content = elementsCrawler(u'北京真格天投股权投资中心（有限合伙）', infos=['B7'])
    d = pq(html.fromstring(content.decode("utf-8")))
    items = d('ENTINV ITEM')
    for i in items:
        print d(i)('ENTNAME').text()


def getEntid(companyName):
    param = {
        "userid": 'HZ91i1a',
        "type": 3,
        "key": companyName
    }

    param = sorted(param.items(), key=lambda d: d[0])
    paramStr = ''
    for i in param:
        paramStr += i[0] + str(i[1])

    token = hmac.new(userkey, paramStr + userid, hashlib.sha1).hexdigest()

    res = requests.post('http://open.elecredit.com/getentid/', data=param, headers={'Authorization': token})

    print res.text
    data = json.loads(unquote(res.text))

    if data['code'] == '200' and data['sucess'] == 1:
        return data['data']
    else:
        print data
        exit()


def elementsCrawler(companyName, infos=[]):
    entid = getEntid(companyName)

    if len(infos) == 0:
        infos = ['A1', 'A2', 'B1', 'B3', 'B7']
    result = {}
    for info in infos:
        param = {
            "userid": 'HZ91i1a',
            "entid": entid,
            "version": info
        }

        param = sorted(param.items(), key=lambda d: d[0])
        paramStr = ''
        for i in param:
            paramStr += i[0] + str(i[1])

        token = hmac.new(userkey, paramStr + userid, hashlib.sha1).hexdigest()

        res = requests.post('http://open.elecredit.com/elsaic/', data=param, headers={'Authorization': token})
        print 'info:%s' % info
        print  res.text
        result[info] = res.text
    return result


def save(company_name, content):
    collection_content = {
        "date": datetime.datetime.now(),
        "source": SOURCE,
        "type": 36008,
        "url": None,
        "content": content,
        "key": company_name
    }

    mongo = db.connect_mongo()
    if mongo.raw.projectdata.find_one({"source": SOURCE, "type": TYPE, "key": company_name}) is not None:
        mongo.raw.projectdata.delete_one({"source": SOURCE, "type": TYPE, "key": company_name})
    mongo.raw.projectdata.insert_one(collection_content)
    mongo.close()


def start_run():
    while True:
        logger.info("elements crawler start...")

        mongo = db.connect_mongo()
        collection_name = mongo.info.gongshang_name
        cnames = list(collection_name.find({
            "type": 3,
            "$or": [
                {"lastCheckTime": None},
                {"lastCheckTime": {"$lt": datetime.datetime.now() - datetime.timedelta(days=30)}}
            ]
        }).sort('_id', -1).limit(1000))

        for cname in cnames:
            if cname["name"] is None or cname["name"].strip() == "":
                continue
            logger.info("crawler type 3: %s", cname["name"])
            r = elementsCrawler(cname["name"], [])
            save(cname["name"], r)
            collection_name.update_one({"_id": cname["_id"]}, {'$set': {"lastCheckTime": datetime.datetime.now()}})
        mongo.close()

        logger.info("elements crawler end...")

        time.sleep(1 * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        infos = []
        r = elementsCrawler(param, infos)
        for ri in r:
            logger.info("%s", ri)
            logger.info(r[ri])
        save(param, r)
    else:
        start_run()
        # companyName = u'北京真格天投股权投资中心（有限合伙）'
        # r = elementsCrawler(companyName)
        # save(companyName, r)
        # compare()
