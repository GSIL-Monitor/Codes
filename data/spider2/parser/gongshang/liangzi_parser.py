# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import parser_db_util

# logger
loghelper.init_logger("parser_liangzi", stream=True)
logger = loghelper.get_logger("parser_liangzi")

# mongo
mongo = db.connect_mongo()
collection_goshang = mongo.info.gongshang
collection_goshang_history = mongo.info.gongshang_history

SOURCE = 13091  #
TYPE = 36008  # 工商

investor_type_map = {
    2: "个人投资",
    1: "企业投资",
}


def save_collection_goshang(collection_name, gitem):
    item = {}
    for col in gitem:
        item[col] = gitem[col]

    record = collection_name.find_one({"name": item["name"]})
    if record is None:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        item["diffChecked"] = False

        if item.has_key("invests_new") is True:
            invests_new = item.pop("invests_new")
            invests_update = [{"name": name} for name in invests_new]
            item["invests"] = invests_update

        id = collection_name.insert(item)
        logger.info('inserting:%s', item["name"])
    else:
        id = record["_id"]
        item["modifyTime"] = datetime.datetime.now()
        item["diffChecked"] = False

        # checking and add new invest
        # item.pop("invests_new")
        # if item.has_key("invests_new") is True:
        #     invests_new = item.pop("invests_new")
        #     investsOld = record.get("invests", [])
        #     invests_old = [io["name"] for io in investsOld if io["name"] is not None]
        #     invests_update = [name for name in invests_new if name not in invests_old]
        #     logger.info("%s -> %s", ";".join(invests_new), ";".join(invests_old))
        #     logger.info("new add: %s", ";".join(invests_update))
        #     if len(invests_update) > 0:
        #         for upname in invests_update:
        #             collection_name.update_one({"_id": id}, {'$addToSet': {"invests": {"name": upname, "new": True}}})

        collection_name.update_one({"_id": id}, {'$set': item})
    return id


def save_collection_goshang_his(collection_name_history, gitem):
    item = {}
    for col in gitem:
        item[col] = gitem[col]

    item["createTime"] = datetime.datetime.now()
    item["modifyTime"] = item["createTime"]
    item["source"] = 13091
    if item.has_key("invests_new") is True:
        invests_new = item.pop("invests_new")
        item["invests"] = [{"name": name} for name in invests_new]
    collection_name_history.insert(item)
    return id


def from1970todate(l):
    if l is None:
        return None
    d = time.localtime(l / 1000)
    return datetime.datetime(d.tm_year, d.tm_mon, d.tm_mday)


def process():
    skip = 0
    limit = 1000

    num = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, 0, limit)
        # items = [parser_db_util.find_process_one(SOURCE, TYPE, 2310299181)]

        # skip += limit
        for c in items:
            num += 1

            logger.info("%s: %s" % (num, c["key"]))
            gongshang = {'name': c["key"]}

            if c['content'].has_key('getRegistInfo') and len(c['content']['getRegistInfo']) > 0 and isinstance(
                    c['content']['getRegistInfo'], list):
                base = c['content']['getRegistInfo'][0]
                if base.get("OPTO") is not None:
                    try:
                        toTime = datetime.datetime.strptime(base.get("OPTO"), '%Y-%m-%d')
                    except:
                        toTime = base.get("OPTO")
                else:
                    toTime = None

                if base.get("OPFROM") is not None:
                    try:
                        fromTime = datetime.datetime.strptime(base.get("OPFROM"), '%Y-%m-%d')
                    except:
                        fromTime = base.get("OPFROM")
                else:
                    fromTime = None

                baseInfo = {
                    "name": base["ENTNAME"],
                    "regCapital": base.get("REGCAP"),
                    # "industry": base.get("industry"),
                    # "regInstitute": base.get("regInstitute"),
                    "establishTime": datetime.datetime.strptime(base.get("ESDATE"), '%Y-%m-%d') if base.get("ESDATE") else None ,
                    # "base": base.get("base"),
                    "regNumber": base.get("REGNO"),
                    "regStatus": base.get("ENTSTATUS"),
                    "fromTime": fromTime,
                    "toTime": toTime,
                    "businessScope": base.get("OPSCOPE"),
                    "regLocation": base.get("DOM"),
                    "companyOrgType": base.get("ENTTYPE"),
                    # "legalPersonId": base.get("legalPersonId"),
                    "legalPersonName": base.get("FRNAME")
                }
                gongshang.update(baseInfo)
            else:
                record = collection_goshang.find_one({"name": c["key"]})
                if record is None:
                    logger.info("No gongshang data before for this missing registinfo company: %s", c["key"])
                    parser_db_util.update_processed(c["_id"])
                    continue


            if c['content'].has_key('getShareHolderInfo') and len(
                    c['content']['getShareHolderInfo']) > 0 and isinstance(c['content']['getShareHolderInfo'], list):
                investors = []
                investorlist = c["content"]["getShareHolderInfo"]
                # logger.info(len(investorlist))
                for i in investorlist:
                    investor_info = {}
                    investor_info["type"] = i.get("INVTYPE")
                    investor_info["name"] = i.get("SHANAME")

                    investors.append(investor_info)
                gongshang["investors"] = investors

            members = []
            if c["content"].has_key("getMainManagerInfo") and len(
                    c['content']['getMainManagerInfo']) > 0 and isinstance(c['content']['getMainManagerInfo'], list):
                memberlist = c["content"]["getMainManagerInfo"]
                for m in memberlist:
                    member_info = {}
                    member_info["name"] = m.get("NAME")
                    member_info["position"] = m.get("POSITION")
                    # member_info["position"] = ",".join(list(set(m.get("POSITION"))))

                    members.append(member_info)
                gongshang["members"] = members

            changinfo = []
            if c["content"].has_key("getRegisterChangeInfo") and len(
                    c['content']['getRegisterChangeInfo']) > 0 and isinstance(c['content']['getRegisterChangeInfo'],
                                                                              list):
                changinfoList = c["content"]["getRegisterChangeInfo"]
                for change in changinfoList:
                    change_info = {}
                    change_info["changeTime"] = change.get("ALTDATE")
                    change_info["contentBefore"] = change.get("ALTBE")
                    change_info["contentAfter"] = change.get("ALTAF")
                    change_info["changeItem"] = change.get("ALTITEM")

                    changinfo.append(change_info)
                gongshang["changeInfo"] = changinfo

            # invests_new = []
            # if c["content"].has_key("getInvestmentAbroadInfo") and len(
            #         c['content']['getInvestmentAbroadInfo']) > 0 and isinstance(c['content']['getInvestmentAbroadInfo'],
            #                                                                     list):
            #     investlist = c["content"]["getInvestmentAbroadInfo"]
            #     for invest in investlist:
            #         if invest.has_key("ENTNAME") and invest["ENTNAME"] is not None:
            #             invests_new.append(invest["ENTNAME"])
            #
            #     gongshang["invests_new"] = invests_new

            if len(gongshang) == 1:
                logger.info('no content:%s', c["key"])
            else:
                logger.info(json.dumps(gongshang, ensure_ascii=False, cls=util.CJsonEncoder))

                save_collection_goshang(collection_goshang, gongshang)
                save_collection_goshang_his(collection_goshang_history, gongshang)
            parser_db_util.update_processed(c["_id"])
            logger.info("processed %s", c["key"])

        if len(items) == 0:
            break


if __name__ == '__main__':
    while True:
        process()
        logger.info('end')
        time.sleep(60)
