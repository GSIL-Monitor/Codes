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
import pymongo

# logger
loghelper.init_logger("parser_qixin", stream=True)
logger = loghelper.get_logger("parser_qixin")

# mongo
mongo = db.connect_mongo()
collection_goshang = mongo.info.gongshang
collection_goshang_history = mongo.info.gongshang_history
collection_gongshang_name = mongo.info.gongshang_name

SOURCE = 13093  #
TYPE = 36008  # 工商


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
            invests_update = [invest for invest in invests_new]
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
            invests_old_names = [io["name"] for io in investsOld if io["name"] is not None]

            logger.info("%s -> %s", ";".join([i['name'] for i in invests_new]), ";".join(invests_old_names))
            invests_update = []
            for investnew in invests_new:
                investnew_name = investnew.pop('name')
                if investnew_name in invests_old_names:
                    collection_name.update_one({"_id": id, 'invests.name': investnew_name},
                                               {'$set': {"invests.$.info": investnew}})
                else:
                    invests_update.append(investnew_name)
                    collection_name.update_one({"_id": id},
                                               {'$addToSet': {"invests": {'name': investnew_name, 'new': True,
                                                                          'info': investnew}}})

            # invests_old = [io["name"] for io in investsOld if io["name"] is not None]
            # invests_update = [name for name in invests_new if name['name'] not in invests_old]
            logger.info("new add: %s", ";".join([i for i in invests_update]))
            # if len(invests_update) > 0:
            #     for upname in invests_update:
            #         upname.update({"new": True})
            #         collection_name.update_one({"_id": id}, {'$addToSet': {"invests": upname}})

        collection_name.update_one({"_id": id}, {'$set': item})
    return id


def save_collection_goshang_his(collection_name_history, gitem):
    item = {}
    for col in gitem:
        item[col] = gitem[col]

    if item.has_key("invests_new") is True:
        invests_new = item.pop("invests_new")
        item["invests"] = [{"name": name} for name in invests_new]

    newestHistory = list(
        collection_name_history.find({'source': SOURCE, 'name': gitem['name']}).sort("_id", pymongo.DESCENDING))

    if len(newestHistory) > 0:
        newestHistory = newestHistory[0]
        for col in ['createTime', 'modifyTime', 'source', '_id']:
            newestHistory.pop(col)

    if item == newestHistory:
        logger.info('%s, the same history , dunt save', gitem['name'])
    else:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        item["source"] = SOURCE
        collection_name_history.insert(item)
        return id


def add_gongshang_name(name):
    if collection_gongshang_name.find_one({'name': name}) is None:
        logger.info("insert gongshang_name:%s", name)
        collection_gongshang_name.insert({"name": name, "type": 5, "lastCheckTime": None})


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
        # items = [parser_db_util.find_process_one_key(SOURCE, TYPE, u'行吟信息科技（上海）有限公司')]
        # items = [parser_db_util.find_process_one_key(SOURCE, TYPE, u'深圳市加推科技有限公司')]

        # skip += limit
        for c in items:
            num += 1

            logger.info("%s: %s" % (num, c["key"]))
            gongshang = {'name': c["key"]}

            if c['content'].has_key('IC_info') and len(c['content']['IC_info']) > 0:
                base = c['content']['IC_info']

                def get_date(key):
                    if base.get(key) is not None and base.get(key) != "-":
                        try:
                            result = datetime.datetime.strptime(base.get(key), '%Y-%m-%d')
                        except:
                            result = None
                    else:
                        result = None

                    return result

                toTime = get_date('term_end')
                fromTime = get_date('term_start')

                try:
                    address = base.get("addresses")[0]['address']
                except:
                    address = None

                baseInfo = {
                    "name": base["name"],
                    "regCapital": base.get("regist_capital"),
                    # "industry": base.get("industry"),
                    # "regInstitute": base.get("regInstitute"),
                    "establishTime": get_date('start_date'),
                    # "base": base.get("base"),
                    "regNumber": base.get("reg_no"),
                    "regStatus": base.get("status"),
                    "fromTime": fromTime,
                    "toTime": toTime,
                    "businessScope": base.get("scope"),
                    "regLocation": address,
                    "companyOrgType": base.get("kind"),
                    # "legalPersonId": base.get("legalPersonId"),
                    "legalPersonName": base.get("legal_person")
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
            else:
                record = collection_goshang.find_one({"name": c["key"]})
                if record is None:
                    logger.info("No gongshang data before for this missing registinfo company: %s", c["key"])
                    parser_db_util.update_processed(c["_id"])
                    continue

            if c['content'].has_key('partners') and len(c['content']['partners']) > 0:
                investors = []
                investorlist = c["content"]["partners"]
                # logger.info(len(investorlist))
                real_capitals_total, should_capitals_total = 0, 0
                for i in investorlist:
                    real_capitals = i.get('real_capitals')
                    should_capitals = i.get('should_capitals')
                    if real_capitals:
                        amount = real_capitals[0].get('amount', -666)
                        if amount != -666 and amount != '-' and amount.strip() not in [u'万人民币', u'万美元']:
                            if amount.find(u'万') < 0: continue
                            amount = amount.split(u'万')[0]
                            real_capitals_total += float(amount)
                        else:
                            logger.info('%s has no capital amount, stop calculating rate.', c['key'])
                            real_capitals_total = -999999999

                    if should_capitals:
                        amount = should_capitals[0].get('amount', -666)
                        if amount != -666 and amount != '-' and amount.strip() not in [u'万人民币', u'万美元']:
                            if amount.find(u'万') < 0: continue
                            amount = amount.split(u'万')[0]

                            should_capitals_total += float(amount)
                        else:
                            logger.info('%s has no capital amount, stop calculating rate.', c['key'])
                            should_capitals_total = -999999999
                            break

                for i in investorlist:
                    investor_info = {}
                    investor_info["type"] = i.get("kind")
                    investor_info["name"] = i.get("name").replace("(", "（").replace(")", "）")
                    real_capitals = i.get("real_capitals")
                    for capital in real_capitals:
                        if capital.has_key('amount') and capital['amount'].strip() not in [u'万人民币', u'万美元']:
                            if capital['amount'].find(u'万') < 0: continue
                            amount = capital['amount'].split(u'万')[0]
                            if amount != '-':
                                amount = float(amount)
                                rate = '%s%%' % (int(
                                    round(amount / real_capitals_total, 2) * 100)) if real_capitals_total > 0 else '-'
                            else:
                                rate = '-'
                            capital['rate'] = rate
                    investor_info["real_capitals"] = real_capitals

                    should_capitals = i.get("should_capitals")
                    for capital in should_capitals:
                        if capital.has_key('amount') and capital['amount'].strip() not in [u'万人民币', u'万美元']:
                            if capital['amount'].find(u'万') < 0: continue
                            amount = capital['amount'].split(u'万')[0]
                            if amount != '-':
                                amount = float(amount)
                                rate = '%s%%' % (int(round(amount / should_capitals_total,
                                                           2) * 100)) if should_capitals_total > 0 else '-'
                            else:
                                rate = '-'
                            capital['rate'] = rate
                    investor_info["should_capitals"] = should_capitals

                    investors.append(investor_info)
                    if investor_info["name"] is not None and investor_info["name"] != '' and (
                            investor_info["type"].find('企业') >= 0 or investor_info["type"].find('公司') >= 0):
                        add_gongshang_name(investor_info["name"])

                gongshang["investors"] = investors

            members = []
            if c["content"].has_key("managers") and len(c['content']['managers']) > 0:
                memberlist = c["content"]["managers"]
                for m in memberlist:
                    member_info = {}
                    member_info["name"] = m.get("name")
                    member_info["position"] = m.get("position")
                    # member_info["position"] = ",".join(list(set(m.get("POSITION"))))

                    members.append(member_info)
                gongshang["members"] = members

            changinfo = []
            if c["content"].has_key("change_records") and len(c['content']['change_records']) > 0:
                changinfoList = c["content"]["change_records"]
                for change in changinfoList:
                    change_info = {}
                    change_info["changeTime"] = change.get("date")
                    change_info["contentBefore"] = change.get("before")
                    change_info["contentAfter"] = change.get("after")
                    change_info["changeItem"] = change.get("item")

                    changinfo.append(change_info)
                gongshang["changeInfo"] = changinfo
            else:
                gongshang["changeInfo"] = []

            invests_new = []
            if c["content"].has_key("invests") and len(c['content']['invests']) > 0:
                investlist = c["content"]["invests"]
                for invest in investlist:
                    if invest.has_key("name") and invest["name"] is not None:
                        invest['name'] = invest['name'].replace("(", "（").replace(")", "）")
                        invests_new.append(invest)
                        add_gongshang_name(invest["name"])

                gongshang["invests_new"] = invests_new

            if c["content"].has_key("contact") and len(c['content']['contact']) > 0:
                gongshang['contact'] = c['content']['contact']

            if len(gongshang) == 1:
                logger.info('no content:%s', c["key"])
            else:
                try:
                    logger.info(json.dumps(gongshang, ensure_ascii=False, cls=util.CJsonEncoder))
                except:
                    pass

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
