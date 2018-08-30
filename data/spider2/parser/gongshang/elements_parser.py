# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import parser_db_util

# logger
loghelper.init_logger("parser_elements", stream=True)
logger = loghelper.get_logger("parser_elements")

# mongo
mongo = db.connect_mongo()
collection_goshang = mongo.info.gongshang
collection_goshang_history = mongo.info.gongshang_history

SOURCE = 13092  #
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
        if item.has_key("invests_new") is True:
            invests_new = item.pop("invests_new")
            investsOld = record.get("invests", [])
            invests_old = [io["name"] for io in investsOld if io["name"] is not None]
            invests_update = [name for name in invests_new if name not in invests_old]
            logger.info("%s -> %s", ";".join(invests_new), ";".join(invests_old))
            logger.info("new add: %s", ";".join(invests_update))
            if len(invests_update) > 0:
                for upname in invests_update:
                    collection_name.update_one({"_id": id}, {'$addToSet': {"invests": {"name": upname, "new": True}}})

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
        # items = [parser_db_util.find_process_one_key(SOURCE, TYPE, u'哎哎信息科技（上海）有限公司')]
        # items = [parser_db_util.find_process_one_key(SOURCE, TYPE, u'北京真格天投股权投资中心（有限合伙）')]

        # skip += limit
        for c in items:
            num += 1

            logger.info("%s: %s" % (num, c["key"]))
            gongshang = {'name': c["key"]}

            if c['content'].has_key('A1'):
                base = pq(html.fromstring(c['content']['A1'].decode("utf-8")))
                item = base('BASIC ITEM')

                if len(item) > 0:
                    base = base(item)

                    def getItem(key):
                        if base(key).text() != '':
                            return base(key).text()
                        else:
                            return None

                    baseInfo = {
                        "name": getItem('ENTNAME'),
                        "regCapital": getItem('REGCAP'),
                        "industry": getItem('INDUSTRYPHY'),
                        "regInstitute": getItem('REGORG'),
                        "establishTime": datetime.datetime.strptime(getItem('ESDATE'), '%Y-%m-%d') if getItem(
                            'ESDATE') is not None else None,
                        "base": getItem('REGORGPROVINCE'),
                        "regNumber": getItem('REGNO'),
                        "regStatus": getItem('ENTSTATUS'),
                        "fromTime": datetime.datetime.strptime(getItem('OPFROM'), '%Y-%m-%d') if getItem(
                            'OPFROM') is not None else None,
                        "toTime": datetime.datetime.strptime(getItem('OPTO'), '%Y-%m-%d') if getItem(
                            'OPTO') is not None else None,
                        "businessScope": getItem('CBUITEM'),
                        "regLocation": getItem('OPLOC'),
                        "companyOrgType": getItem('ENTTYPE'),
                        # "legalPersonId": getItem('REGORGPROVINCE'),
                        "legalPersonName": getItem('FRNAME')
                    }

                    # gongshang.update(baseInfo)
                    record = collection_goshang.find_one({"name": c["key"]})
                    for key in baseInfo:
                        if record is None:
                            gongshang[key] = baseInfo[key]
                        else:
                            if baseInfo[key] is None and record.has_key(key):
                                logger.info("%s is None, don't update" % key)
                            else:
                                gongshang[key] = baseInfo[key]

            if c['content'].has_key('B1'):
                investors = []
                htmlRaw = pq(html.fromstring(c['content']['B1'].decode("utf-8")))
                item = htmlRaw('SHAREHOLDER ITEM')

                if len(item) > 0:
                    for investor in item:
                        i = htmlRaw(investor)
                        investor_info = {}
                        # investor_info["type"] = i('')
                        investor_info["name"] = i("SHANAME").text()

                        investors.append(investor_info)

                    gongshang["investors"] = investors

            members = []
            if c["content"].has_key("B3") > 0:
                htmlRaw = pq(html.fromstring(c['content']['B3'].decode("utf-8")))
                item = htmlRaw('PERSON ITEM')

                if len(item) > 0:
                    for member in item:
                        def getItem(key):
                            if m(key).text() != '':
                                return m(key).text()
                            else:
                                return None

                        m = htmlRaw(member)
                        member_info = {}
                        member_info["name"] = getItem("PERNAME")
                        member_info["position"] = getItem("POSITION")
                        # member_info["position"] = ",".join(list(set(m.get("POSITION"))))

                        members.append(member_info)
                    gongshang["members"] = members

            changinfo = []
            if c["content"].has_key("A2") > 0:
                htmlRaw = pq(html.fromstring(c['content']['A2'].decode("utf-8")))
                item = htmlRaw('ALTER ITEM')

                if len(item) > 0:
                    for change in item:
                        def getItem(key):
                            if change(key).text() != '':
                                return change(key).text()
                            else:
                                return None

                        change = htmlRaw(change)
                        change_info = {}
                        change_info["changeTime"] = getItem("ALTDATE")
                        change_info["contentBefore"] = getItem("ALTBE")
                        change_info["contentAfter"] = getItem("ALTAF")
                        change_info["changeItem"] = getItem("ALTITEM")

                        changinfo.append(change_info)
                    gongshang["changeInfo"] = changinfo

            invests_new = []
            if c["content"].has_key("B7"):
                htmlRaw = pq(html.fromstring(c['content']['B7'].decode("utf-8")))
                item = htmlRaw('ENTINV ITEM')

                if len(item) > 0:
                    for i in item:
                        invest = htmlRaw(i)
                        if invest("ENTNAME") and invest("ENTNAME").text() != '':
                            invests_new.append(invest("ENTNAME").text())

                    gongshang["invests_new"] = invests_new

            parser_db_util.update_processed(c["_id"])
            if len(gongshang) == 1:
                logger.info('no content:%s', c["key"])
            else:
                logger.info(json.dumps(gongshang, ensure_ascii=False, cls=util.CJsonEncoder))

                save_collection_goshang(collection_goshang, gongshang)
                save_collection_goshang_his(collection_goshang_history, gongshang)
            logger.info("processed %s", c["key"])

        if len(items) == 0:
            break


if __name__ == '__main__':
    while True:
        process()
        logger.info('end')
        time.sleep(60)
