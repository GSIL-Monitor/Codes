# -*- coding: utf-8 -*-
import os, sys, re, json, time
import datetime
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import amac_util
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util, url_helper,email_helper
import db

import find_investor_alias

#logger
loghelper.init_logger("amac_find_new", stream=True)
logger = loghelper.get_logger("amac_find_new")

# investor_alias amacType amacId
# investor_alias_candidate amacType amacId

DATE = None

def extract_fund(investorId):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    collection_gongshang = mongo.info.gongshang

    allinvestors = []
    portfolios = find_investor_alias.get_investor_porfolio(investorId)
    corIds = [i['corporateId'] for i in portfolios]
    if len(corIds) == 0:
        mongo.close()
        conn.close()
        return

    fullNames = find_investor_alias.get_companyFullNames(corIds)
    gongshangs = list(collection_gongshang.find({'name': {'$in': fullNames}}, {'investors': 1, 'name': 1}))
    for g in gongshangs:
        if g.has_key('investors'):
            for i in g['investors']:
                if i['name'] is None or i["name"].strip() in ["", "-", "—"]:
                    logger.info('investorName is None %s', g['name'])
                    continue
                if i["name"].strip() not in allinvestors:
                    allinvestors.append(i["name"].strip())

    logger.info("investors Names all: %s", ";".join(allinvestors))

    if len(allinvestors) == 0:
        mongo.close()
        conn.close()
        return

    aliases = conn.query("select * from investor_alias where (active is null or active='Y') and "
                         "(verify is null or verify !='N') and investorId=%s", investorId)

    anames = [alias["name"] for alias in aliases if alias["name"] is not None and alias["type"] == 12010]

    for aname in anames:
        if aname.find("合伙") == -1 and aname.find("资产") == -1 and aname.find("基金") == -1:
            continue
        if aname in allinvestors:
            logger.info("find a fund name: %s for investor: %s", aname, investorId)
            memo = aname + "是该机构所投企业的股东"
            amac_util.add_name_investor_fund(aname, investorId, memo)

    mongo.close()
    conn.close()

def extract_data(investorId):
    tline = ""
    n = 0
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_gongshang = mongo.info.gongshang

    oaliases = conn.query("select * from investor_alias where (active is null or active='Y') and "
                         "(verify is null or verify !='N') and investorId=%s", investorId)

    oanames = [alias["name"] for alias in oaliases if alias["name"] is not None and alias["type"] == 12010]
    anames = []

    investorfs = conn.query("select * from investor_fund where (active is null or active='Y') and "
                            "(verify is null or verify !='N') and investorId=%s;", investorId)
    for investorf in investorfs:
        amacf = "是" if investorf["amacFundId"] is not None else "否"
        of = "是" if investorf["fullName"] in oanames else "否"
        item = collection_gongshang.find_one({'name': investorf["fullName"]})
        if item is not None and item.has_key("invests") and len(item["invests"]) > 0:
            numiv = len(item["invests"])
        else:
            numiv = "0"
        line = "%s+++%s+++%s+++%s+++%s\n" % (investorf["fullName"], investorf["memo"], amacf, of,numiv)
        tline += line
        if investorf["fullName"] not in anames: anames.append(investorf["fullName"])

    investorgs = conn.query("select * from investor_gp where (active is null or active='Y') and "
                            "(verify is null or verify !='N') and investorId=%s;", investorId)
    for investorg in investorgs:
        amacf = "是" if investorg["amacManagerId"] is not None else "否"
        of = "是" if investorg["fullName"] in oanames else "否"
        item = collection_gongshang.find_one({'name': investorg["fullName"]})
        if item is not None and item.has_key("invests") and len(item["invests"]) > 0:
            numiv = len(item["invests"])
        else:
            numiv = "0"
        line = "%s+++%s+++%s+++%s+++%s\n" % (investorg["fullName"], investorg["memo"], amacf, of,numiv)
        tline += line
        if investorg["fullName"] not in anames: anames.append(investorg["fullName"])

    tline += "\n\n"

    for oal in oaliases:
        if oal["name"] is None: continue
        if oal["name"] in anames: continue
        if oal["type"] != 12010: continue
        if amac_util.find_amac_manager(oal["name"]) is not None or amac_util.find_amac_fund(oal["name"]) is not None:
            amacf = "是"
        else:
            amacf = "否"
        createUser = oal["createUser"] if oal["createUser"] is not None else " "
        item = collection_gongshang.find_one({'name': oal["name"]})
        if item is not None and item.has_key("legalPersonName") and item["legalPersonName"].strip() not in ["", "-", "—"]:
            lp = item["legalPersonName"]
        else:
            lp = " "

        if item is not None and item.has_key("invests") and len(item["invests"]) > 0:
            numiv = len(item["invests"])
            ivnames = [inv["name"] for inv in item["invests"]]
            ivnamesstr = ";".join(ivnames)
            ivnamesnn = [inv["name"] for inv in item["invests"] if inv["name"] in anames]
            ivnamesnnstr = ";".join(ivnamesnn) if len(ivnamesnn) >0 else "无"
        else:
            numiv = "0"
            ivnamesstr = "无"
            ivnamesnnstr = "无"

        line = "%s+++%s+++%s+++%s+++%s+++%s+++%s\n" % (oal["name"], createUser, amacf, lp,
                                                       numiv, ivnamesstr, ivnamesnnstr)
        tline += line
        mongo.close()

    logger.info("%s - %s - %s", investorId, len(oanames), len(investorfs)+len(investorgs))

    fp2 = open("me.txt", "w")
    fp2.write(tline)
    content = '''<div>Dears,    <br /><br />

                附件是目前系统中存在重复的公司，请在后台搜索
                </div>
                '''
    fp2.close()
    path = os.path.join(sys.path[0], "me.txt")
    logger.info(path)
    email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "bamy@xiniudata.com",
                                ';'.join([i + '@xiniudata.com' for i in ["bamy"]]),
                                "重复机构检索--人工审查", content, path)
    fp2.close()
    conn.close()

if __name__ == "__main__":
    extract_data(109)
    extract_data(149)
    exit()
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        # if datestr != DATE:
        #     # init
        #     # time.sleep(30*60)
        #     DATE = datestr

        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        # clists = conn.query("select * from investor where active is null or active !='N'")
        # clists = conn.query("select * from investor where id in (109,149)")
        #
        #
        # for investor in clists:
        #     logger.info("********extract fund :%s, %s", investor["name"], investor["id"])
        #     investor["investorId"] = int(investor["id"])
        #     extract_fund(investor["investorId"])

        for processStatus in [0,1,2]:
            investorfs = conn.query(
                "select * from investor_fund where (active is null or active='Y') and "
                "processStatus=%s", processStatus)

            for inf in investorfs:
                if inf["processStatus"] == 0:
                    logger.info("fund %s: %s is 0 go to check", str(inf["investorId"]),inf["fullName"])
                    amac_util.fund_process_0(inf["id"])
                if inf["processStatus"] == 1:
                    logger.info("fund %s: %s is 1 go to check", inf["investorId"],inf["fullName"])
                    amac_util.fund_process_1(inf["id"])
                if inf["processStatus"] == 2:
                    logger.info("fund %s: %s is 2 go to check", inf["investorId"],inf["fullName"])
                    amac_util.fund_process_2(inf["id"])

            investorgs = conn.query(
                "select * from investor_gp where (active is null or active='Y') and "
                "processStatus=%s", processStatus)

            for ing in investorgs:
                if ing["processStatus"] == 0:
                    logger.info("gp %s: %s is 0 go to check", ing["investorId"], ing["fullName"])
                    amac_util.generalp_process_0(ing["id"])
                if ing["processStatus"] == 1:
                    logger.info("gp %s: %s is 1 go to check", ing["investorId"], ing["fullName"])
                    amac_util.generalp_process_1(ing["id"])
                if ing["processStatus"] == 2:
                    logger.info("gp %s: %s is 2 go to check", ing["investorId"], ing["fullName"])
                    amac_util.generalp_process_2(ing["id"])

        # amac_util.find_investor_alias_by_fund(114)

        mongo.close()
        conn.close()

        logger.info('end')



        time.sleep(60)
