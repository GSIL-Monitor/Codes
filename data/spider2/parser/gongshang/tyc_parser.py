# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db,util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import parser_db_util

#logger
loghelper.init_logger("parser_tianyancha", stream=True)
logger = loghelper.get_logger("parser_tianyancha")

#mongo
mongo = db.connect_mongo()
collection_goshang = mongo.info.gongshang
collection_goshang_history = mongo.info.gongshang_history

SOURCE = 13090  #天眼查
TYPE = 36008    #工商

investor_type_map = {
    2:"个人投资",
    1:"企业投资",
}


def save_collection_goshang(collection_name, item):

    record = collection_name.find_one({"name": item["name"]})
    if record is None:
        item["createTime"] = datetime.datetime.utcnow()
        item["modifyTime"] = item["createTime"]
        item["diffChecked"] = False
        id = collection_name.insert(item)
    else:
        id = record["_id"]
        item["modifyTime"] = datetime.datetime.utcnow()
        item["diffChecked"] = False
        collection_name.update_one({"_id": id}, {'$set': item})
    return id

def save_collection_goshang_his(collection_name_history, item):
    item["createTime"] = datetime.datetime.utcnow()
    item["modifyTime"] = item["createTime"]
    collection_name_history.insert(item)
    return id


def from1970todate(l):
    if l is None:
        return None
    d = time.localtime(l/1000)
    return datetime.datetime(d.tm_year,d.tm_mon,d.tm_mday)


def process():
    skip = 0
    limit = 1000

    num = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, skip, 1000)
        #items = [parser_db_util.find_process_one(SOURCE, TYPE, 2310299181)]
        #items = [parser_db_util.find_process_one(SOURCE, TYPE, 1257527760)]

        skip += limit
        finish = True
        for c in items:
            #finish = False
            num += 1
            if c.has_key("exist") and c["exist"] is False:
                logger.info(c["key"])
                parser_db_util.update_processed(c["_id"])

            if c["content"] is None:
                logger.info(c["key"])
                parser_db_util.update_processed(c["_id"])
                continue
            if c["content"]["data"] is None:
                logger.info(c["key"])
                parser_db_util.update_processed(c["_id"])
                continue

            base = c["content"]["data"]["baseInfo"]
            if base.get("regStatus") is None:
                logger.info(c["key"])
                parser_db_util.update_processed(c["_id"])
                continue

            logger.info("%s: %s" % (num, c["key"]))

            gongshang = {
                "name": base["name"],
                "regCapital": base.get("regCapital"),
                "industry": base.get("industry"),
                "regInstitute": base.get("regInstitute"),
                "establishTime": from1970todate(base.get("estiblishTime")),
                "base": base.get("base"),
                "regNumber": base.get("regNumber"),
                "regStatus": base.get("regStatus"),
                "fromTime": from1970todate(base.get("fromTime")),
                "toTime": from1970todate(base.get("toTime")),
                "businessScope": base.get("businessScope"),
                "regLocation": base.get("regLocation"),
                "companyOrgType": base.get("companyOrgType"),
                "legalPersonId": base.get("legalPersonId"),
                "legalPersonName":base.get("legalPersonName")

            }
            investors = []
            if c["content"]["data"].has_key("investorList"):
                investorlist = c["content"]["data"]["investorList"]
                #logger.info(len(investorlist))
                for i in investorlist:
                    investor_info = {}
                    investor_info["type"] = investor_type_map.get(i.get("type"),"")
                    investor_info["name"] = i.get("name")

                    investors.append(investor_info)

            members = []
            if c["content"]["data"].has_key("staffList"):
                memberlist = c["content"]["data"]["staffList"]
                for m in memberlist:
                    member_info = {}
                    member_info["name"] = m.get("name")
                    member_info["position"] = ",".join(list(set(m.get("typeJoin"))))

                    members.append(member_info)

            changinfo= []
            if c["content"]["data"].has_key("comChanInfoList"):
                changinfo = c["content"]["data"]["comChanInfoList"]

            invests = []
            if c["content"]["data"].has_key("investList"):
                investlist = c["content"]["data"]["investList"]
                for v in investlist:
                    if not v.has_key("name"):
                        continue
                    data = {
                        "name": v["name"]
                    }
                    invests.append(data)

            gongshang["members"] = members
            gongshang["investors"] = investors
            gongshang["changeInfo"] = changinfo
            gongshang["invests"] = invests

            logger.info(json.dumps(gongshang, ensure_ascii=False, cls=util.CJsonEncoder))

            save_collection_goshang(collection_goshang,gongshang)
            save_collection_goshang_his(collection_goshang_history,gongshang)
            parser_db_util.update_processed(c["_id"])
            logger.info("processed %s", c["key"])


        if len(items) == 0:
            break

if __name__ == '__main__':
    while True:
        process()
        time.sleep(60)