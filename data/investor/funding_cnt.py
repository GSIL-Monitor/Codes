# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import util
import config
import db
import loghelper

# logger
loghelper.init_logger("funding_cnt", stream=True)
logger = loghelper.get_logger("funding_cnt")

DATE = None


def run():
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    invs = conn.query("select * from investor where (active is null or active='Y')")
    # cnt_event = 0
    result = []
    for inv in invs:
        # check investor_shortname
        if inv["name"] is not None and inv["name"].strip() != "":
            ialias = conn.get("select * from investor_alias where investorId=%s and name=%s and "
                              "(active is null or active != 'N') limit 1", inv["id"], inv["name"])
            if ialias is None:
                insql = "insert investor_alias(investorId,name,type,createTime,modifyTime,createUser) " \
                        "values(%s,%s,%s,now(),now(),139)"
                conn.insert(insql, inv["id"], inv["name"], 12020)
                logger.info("**********add name for %s %s", inv["name"], inv["id"])

        allialias = conn.query("select * from investor_alias where investorId=%s and "
                               "(active is null or active != 'N')", inv["id"])

        sources = conn.query('''select si.sourceId from investor_source_rel r  join source_investor si
                                on si.id=r.sourceInvestorId
                                where r.investorId=%s and 
                               (r.active is null or r.active != 'N')''', inv["id"])

        map = {
            'investorName': inv['name'],
            'investorId': inv['id'],
            '是否上线': inv['online'],
            'active': inv['active'],
            '短名': '，'.join([i['name'] for i in allialias if i['type'] == 12020]),
            '全名': '，'.join([i['name'] for i in allialias if i['type'] == 12010]),
            'link': '，'.join(['https://rong.36kr.com/org/%s'%i['sourceId'] for i in sources]),
            'modifyTime': datetime.datetime.now()
        }
        for year in [2018, 2017, 2016, 2015, 2014]:
            map[str(year)] = cal_fundnum(inv, year)

        result.append(map)

    # import pandas as pd
    # df = pd.DataFrame(result)
    # df.to_excel('funding_cnt.xlsx', index=0)


    collection = mongo.investor.fundingcnt
    for i in result:
        if collection.find_one({'investorId': i['investorId']}) is None:
            collection.insert_one(i)
        else:
            collection.update_one({'investorId': i['investorId']}, {'$set': i})

    conn.close()
    mongo.close()


def cal_fundnum(inv, year):
    conn = db.connect_torndb()
    cnt_event = 0

    funding_investor_rels = conn.query("select distinct fundingId from funding_investor_rel "
                                       "where investorId=%s and (active is null or active='Y')", inv["id"])
    companyIds = []
    for fir in funding_investor_rels:
        funding = conn.get("select * from funding where id=%s and (active is null or active='Y')"
                           " and "
                           "("
                           "(publishDate is not null and publishDate>='%s-01-01'  and publishDate<'%s-01-01')"
                           " or "
                           "(publishDate is null and fundingDate>='%s-01-01'  and fundingDate <'%s-01-01')"
                           ")", fir["fundingId"], year, year + 1, year, year + 1)

        if funding is not None and funding["corporateId"] is not None:
            # logger.info(funding)
            corporate = conn.get("select * from corporate where id=%s and (active is null or active='Y')",
                                 funding["corporateId"])
            cs = conn.query("select id from company where corporateId=%s and (active is null or active='Y')",
                            funding["corporateId"])
            # cs = conn.query("select id from company where corporateId=%s and (active is null or active='Y')",
            #                 funding["corporateId"])
            if len(cs) > 0 and corporate is not None:
                cnt_event += 1
                # for c in cs:
                #     # logger.info(c)
                #     if c["id"] not in companyIds:
                #         companyIds.append(c["id"])
                #         # break
    # logger.info(companyIds)
    # logger.info("found %s companies by investor: %s", len(companyIds), inv["id"])
    conn.close()
    return cnt_event

    # if len(companyIds) > 0:
    #     conn.update("update investor set fundingCntFrom2017=%s where id=%s", cnt_event, inv["id"])


if __name__ == "__main__":
    global DATE
    while True:
        dt = datetime.datetime.now()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE:
            logger.info('start %s', datestr)
            run()
            logger.info('end')

            DATE = datestr
        time.sleep(60 * 60 * 23)
