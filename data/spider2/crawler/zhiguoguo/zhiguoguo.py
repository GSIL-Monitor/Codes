# -*- coding: utf-8 -*-
import sys, os, time, datetime

import requests
import pprint
import json
import urllib


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download



# logger
loghelper.init_logger("zguoguo_crawler", stream=True)
logger = loghelper.get_logger("zguoguo_crawler")

SOURCE = 13095
# TYPE = 36011
# TYPE = 36012

token = None

def gettoken():
    APPKEY = "9ebf51b8e23b419c371e5ebf58d49c71"
    SECKEY = "c63970b3666de504d406f92875d31a4e"

    urlToken = "http://211.154.163.148:51000/DataPlatformService/GetToken?appkey=%s&seckey=%s&type=JSON" % (
    APPKEY, SECKEY)

    logger.info("url: %s", urlToken)
    r = requests.get(urlToken)

    # print r.text
    while True:
        if r.status_code == 200:
            try:
                logger.info(r.text)
                content = json.loads(r.text)
                if content.has_key("result"):
                    token = content["result"]["token"]
                    break
            except Exception, e:
                logger.info(e)
                logger.info(r.text)
                try:
                    content = json.loads(r.text)
                    logger.info(content["message"])
                except:
                    pass
                logger.info("token failed")
                time.sleep(60*1)
    return token


def zhguoguoCrawler(companyName):
    global token
    result = []
    while True:
        success = False
        if token is None:
            token = gettoken()

        if token is None:
            logger.info("token failed")
            exit()

        company = companyName
        # company = '柳州欧维姆机械股份'
        cc = urllib.quote(company.encode("utf-8"))

        key = 0
        while True:

            urlIcon = "http://211.154.163.148:51000/DataPlatformService/GetTradeMark?token=%s&pageSize=10&currentPage=%s&keyWord=%s" \
                      % (token, key, cc)
            # print urlIcon
            logger.info("url: %s",urlIcon)
            r1 = requests.get(urlIcon)

            try:
                re = json.loads(r1.text)
                logger.info(json.dumps(json.loads(r1.text), ensure_ascii=False, cls=util.CJsonEncoder))
                if re.has_key("status") and re["status"] in  [200,201]:
                    if len(re["result"]) > 0:
                        result.extend(re["result"])

                    if re["page"]["totalPage"] > key + 1 and re["status"] == 200:
                        key += 1
                    else:
                        success = True
                        break
                else:
                    if re.has_key("status") and re["status"] in [101,102]:
                        token = None
                        break
                    elif re.has_key("status") and re["status"] in [108]:
                        time.sleep(60 * 60 * 1)
                        token = None
                        break
                    else:
                        logger.info(r1.text)
                        logger.info("query1 failed")
                        exit(0)
            except:
                logger.info(r1.text)
                logger.info("query failed")
                exit()


        if success is True:
            break
    return result

def zhguoguoCrawler2(companyName):
    global token
    result = []
    while True:
        success = False
        if token is None:
            token = gettoken()

        if token is None:
            logger.info("token failed")
            exit()

        company = companyName
        # company = '柳州欧维姆机械股份'
        cc = urllib.quote(company.encode("utf-8"))

        key = 0
        while True:

            urlCopy = "http://211.154.163.148:51000/DataPlatformService/GetCopyRight?token=%s&pageSize=10&currentPage=%s&keyWord=%s" \
                      % (token, key, cc)
            # print urlIcon
            logger.info("url: %s", urlCopy)
            r1 = requests.get(urlCopy)

            try:
                re = json.loads(r1.text)
                logger.info(json.dumps(json.loads(r1.text), ensure_ascii=False, cls=util.CJsonEncoder))
                if re.has_key("status") and re["status"] in  [200,201]:
                    if len(re["result"]) > 0:
                        result.extend(re["result"])

                    if re["page"]["totalPage"] > key + 1 and re["status"] == 200:
                        key += 1
                    else:
                        success = True
                        break
                else:
                    if re.has_key("status") and re["status"] in [101,102]:
                        time.sleep(1 * 10)
                        token = None
                        break
                    elif re.has_key("status") and re["status"] in [108]:
                        time.sleep(60 * 60 * 1)
                        token = None
                        break
                    else:
                        logger.info(r1.text)
                        logger.info("query1 failed")
                        exit(0)
            except:
                logger.info(r1.text)
                logger.info("query failed")
                exit()


        if success is True:
            break
    return result



def save(company_name, content, TYPE):
    collection_content = {
        "date": datetime.datetime.now(),
        "source": SOURCE,
        "type": TYPE,
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
        logger.info("zhiguoguo crawler start...")

        mongo = db.connect_mongo()
        collection_name = mongo.info.gongshang_name
        cnames = list(collection_name.find({
            "type": 3,
            "$or": [
                {"zglastCheckTime": None},
                {"zglastCheckTime": {"$lt": datetime.datetime.now() - datetime.timedelta(days=300)}}
            ]
        }).limit(20))

        for cname in cnames:
            if cname["name"] is None or cname["name"].strip() == "":
                continue
            logger.info("crawler type 3: %s", cname["name"])
            r = zhguoguoCrawler(cname["name"])
            if len(r) > 0:
                save(cname["name"], r, 36011)
            r1 = zhguoguoCrawler2(cname["name"])
            if len(r1) > 0:
                save(cname["name"], r1, 36012)
            collection_name.update_one({"_id": cname["_id"]}, {'$set': {"zglastCheckTime": datetime.datetime.now()}})
            time.sleep(1*10)
        mongo.close()

        logger.info("zhiguoguo crawler end...")

        time.sleep(1 * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        infos = []
        r = zhguoguoCrawler2(param)
        for ri in r:
            logger.info("%s", ri)
            # logger.info(r[ri])
        # save(param, r)
    else:
        start_run()
        # companyName = u'北京真格天投股权投资中心（有限合伙）'
        # r = elementsCrawler(companyName)
        # save(companyName, r)
        # compare()
