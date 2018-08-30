# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo
from distutils.version import LooseVersion
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, config, url_helper, util, db

#logger
loghelper.init_logger("android", stream=True)
logger = loghelper.get_logger("android")

#mongo
mongo = db.connect_mongo()
collection = mongo.market.android

def save_baidu_index(collection_index, item):
    record = collection_index.find_one({"key_int":item["key_int"]})
    if record:
        return

    record = collection_index.find_one({"docids.docid":item["key_int"]})
    if record:
        return

    item["createTime"] = datetime.datetime.now()
    item["modifyTime"] = item["createTime"]
    try:
        collection_index.insert(item)
    except Exception,e:
        logger.info(e)

def save_baidu_search(collection_search, item):
    record = collection_search.find_one({"key_int":item["key_int"]})
    if record:
        logger.info("%s exist!", item["key_int"])
        return

    record = collection_search.find_one({"apkname":item["apkname"]})
    if record:
        logger.info("%s exist!", item["apkname"])
        if item["version"] is not None and item["version"].strip() != "":
            if record["version"] is None or record["version"].strip() == "" or LooseVersion(item["version"]) >= LooseVersion(record["version"]):
                item["createTime"] = record["createTime"]
                item["modifyTime"] = datetime.datetime.now()
                collection_search.update_one({"_id":record["_id"]},{'$set':item})
    else:
        logger.info("%s insert!", item["apkname"])
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        collection_search.insert(item)


def save(collection_market, appmarket, item):
    item["website"] = url_helper.url_normalize(item["website"])
    flag, domain = url_helper.get_domain(item["website"])
    if flag:
        item["website_domain"] = domain
    else:
        item["website_domain"] = None

    temp = "http://" + ".".join(item["apkname"].split(".")[::-1])
    flag, domain = url_helper.get_domain(temp)
    item["apkname_domain"] = domain

    record = collection_market.find_one({"appmarket":appmarket, "apkname":item["apkname"]}, projection={'histories': False})
    if record:
        _id = record.pop("_id")
        record.pop("key")
        record.pop("key_int")
        #logger.info(json.dumps(record, ensure_ascii=False, cls=util.CJsonEncoder))
        if item["version"] is not None and item["version"].strip() != "":
            if record["version"] is not None and record["version"].strip() != "" and LooseVersion(item["version"]) > LooseVersion(record["version"]):
                item["createTime"] = record["createTime"]
                item["modifyTime"] = datetime.datetime.now()
                if item["updateDate"] is None:
                    item["updateDate"] = datetime.datetime.now()
                collection_market.update_one({"_id":_id},{'$set':item, '$addToSet':{"histories":record}})
            elif record["version"] is None or record["version"].strip() == "" or LooseVersion(item["version"]) == LooseVersion(record["version"]):
                item["modifyTime"] = datetime.datetime.now()
                collection_market.update_one({"_id":_id},{'$set':item})
    else:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        if item["updateDate"] is None:
            item["updateDate"] = datetime.datetime.now()
        try:
            collection_market.insert(item)
        except Exception,e:
            logger.info(e)


def replace(app, item):
    names = ["brief",
             "website",
             "website_domain",
             "commentbyeditor",
             "tags",
             "updates",
             "author",
             "version"]
    flag = False
    for name in names:
        if (app.has_key(name) == False or app[name] is None or app[name].strip() == "") and (item.has_key(name) and item[name] is not None and item[name].strip() != ""):
            app[name] = item[name]
            flag = True

    if (app.has_key("screenshots") == False or len(app["screenshots"]) == 0) and (item.has_key("screenshots") and len(item["screenshots"]) > 0):
        flag = True

    return flag

def merge(item):
    if item.has_key("_id"):
        item.pop("_id")
    #if item.has_key("link"):
    #    item.pop("link")
    if item.has_key("key"):
        item.pop("key")
    if item.has_key("key_int"):
        item.pop("key_int")
    if item.has_key("appmarket"):
        item.pop("appmarket")
    if item.has_key("baidu_docids"):
        item.pop("baidu_docids")
    if item.has_key("download"):
        item.pop("download")

    if item.has_key("screenshots") and len(item["screenshots"]) > 0:
        sshots = item["screenshots"]
        if sshots[0].find("bdimg") >= 0:
            # baidu image not work
            item["screenshots"] = []

    app = collection.find_one({"apkname":item["apkname"]}, projection={'histories': False})
    if app is None:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        try:
            collection.insert(item)
        except Exception,e:
            logger.info(e)
    else:
        _id = app.pop("_id")
        logger.info("old version: %s", app["version"])
        logger.info("new version: %s", item["version"])
        if item["version"] is not None and item["version"] != "":
            if app["version"] is not None and app["version"] != "" and LooseVersion(item["version"]) > LooseVersion(app["version"]):
                item["createTime"] = app["createTime"]
                item["modifyTime"] = datetime.datetime.now()
                collection.update_one({"_id":_id},{'$set':item, '$addToSet':{"histories":app}})
            elif app["version"] is None or app["version"] == "" or LooseVersion(item["version"]) == LooseVersion(app["version"]):
                if replace(app, item):
                    # app["modifyTime"] = item["modifyTime"]
                    logger.info("merge update")
                    logger.info(json.dumps(app, ensure_ascii=False, cls=util.CJsonEncoder))
                    collection.update_one({"_id":_id},{'$set':app})


if __name__ == '__main__':
    if LooseVersion("5.22.0") > LooseVersion("5.l0.2"):
        print ("here")