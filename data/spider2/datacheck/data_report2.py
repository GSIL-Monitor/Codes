# -*- coding: utf-8 -*-
import os, sys
import datetime
import gridfs
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db
import loghelper
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))

#logger
loghelper.init_logger("Data_report2", stream=True)
logger = loghelper.get_logger("Data_report2")



def yitai_check():
    dd = []
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_goshang = mongo.info.gongshang
    sql = "select * from investor where online='Y' and (active is null or active !='N')"
    investors = conn.query(sql)
    dd.append({"item":"上线基金数","count":len(investors)})
    cnt_goshang = 0
    cnt_event = 0
    cnt_event_stock = 0
    cnt_event_nestock = 0
    corporateIds = []
    companyIds = []

    for investor in investors:
        aliases = conn.query("select * from investor_alias where (active is null or active='Y') and "
                             "(verify is null or verify !='N') and investorId=%s", investor["id"])
        for alias in aliases:
            goshang = collection_goshang.find_one({"name":alias["name"]})
            if goshang is not None: cnt_goshang += 1

        funding_investor_rels = conn.query("select distinct fundingId from funding_investor_rel "
                                           "where investorId=%s and (active is null or active='Y')", investor["id"])
        for fir in funding_investor_rels:
            funding = conn.get("select * from funding where id=%s and (active is null or active!='N')"
                               " and fundingDate >='2017-01-01'", fir["fundingId"])

            if funding is not None and funding["corporateId"] is not None:
                # logger.info(funding)
                corporate = conn.get("select * from corporate where id=%s and (active is null or active!='N')",
                                     funding["corporateId"])
                cs = conn.query("select id from company where corporateId=%s and (active is null or active!='N')",
                                funding["corporateId"])
                if len(cs) > 0 and corporate is not None:
                    cnt_event += 1
                    if funding["round"] is not None and funding["round"] in [1105,1106,1110]:
                        cnt_event_stock += 1
                    else:
                        cnt_event_nestock += 1
                    if funding["corporateId"] not in corporateIds:
                        corporateIds.append(funding["corporateId"])

                    for c in cs:
                        # logger.info(c)
                        if c["id"] not in companyIds:
                            companyIds.append(c["id"])
                        # break
    cnt_company = len(companyIds)
    cnt_corporate = len(corporateIds)

    dd.extend([{"item": "2017至今马甲工商数", "count": cnt_goshang},
               {"item": "2017至今融资事件数", "count": cnt_event},
               {"item": "2017至今涉及项目数", "count": cnt_company},
               {"item": "2017至今涉及corporate数", "count": cnt_corporate}])

    mongo.close()
    conn.close()
    return dd

def investor_check():
    de = []
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    sql = "select * from investor where (active is null or active !='N')"
    investors = conn.query(sql)
    # cnt_f = conn.get("select count(*) from funding f left join corporate c on f.corporateId = c.id "
    #                  "where (f.active is null or f.active!='N') and (c.active is null or c.active !='N');")
    cnt_event = 0
    corporateIds = []
    companyIds = []
    fundings = conn.query("select * from funding where (active is null or active !='N')")
    for funding in fundings:
        if funding is not None and funding["corporateId"] is not None:
            # logger.info(funding)
            corporate = conn.get("select * from corporate where id=%s and (active is null or active !='N')",
                                 funding["corporateId"])
            cs = conn.query("select id from company where corporateId=%s and (active is null or active!='N')",
                            funding["corporateId"])
            if len(cs) > 0 and corporate is not None:
                cnt_event += 1
                if funding["corporateId"] not in corporateIds:
                    corporateIds.append(funding["corporateId"])

                for c in cs:
                    # logger.info(c)
                    if c["id"] not in companyIds:
                        companyIds.append(c["id"])
                        # break
    cnt_company = len(companyIds)
    cnt_corporate = len(corporateIds)

    de.extend([{"item": "总基金数", "count": len(investors)},
               {"item": "总融资事件数", "count": cnt_event},
               {"item": "总涉及项目数", "count": cnt_company},
               {"item": "总涉及corporate数", "count": cnt_corporate}])
    conn.close()
    mongo.close()
    return de

def funding_check():
    de = []
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    # cnt_event = 0
    # corporateIds = []
    # companyIds = []
    # cnt_event_stock = 0
    # cnt_event_nestock = 0

    for year in ["2015", "2016", "2017"]:
        cnt_event = 0
        corporateIds = []
        companyIds = []
        cnt_event_stock = 0
        cnt_event_nestock = 0
        cnt_d = 0
        cnt_f = 0
        cds = []
        cfs = []
        css = []
        cnes = []
        if year == "2016":
            fundings = conn.query("select * from funding where (active is null or active !='N') and"
                                  " fundingDate >='2016-01-01' and fundingDate<'2017-01-01'")
        elif year == "2015":
            fundings = conn.query("select * from funding where (active is null or active !='N') and"
                                  " fundingDate >='2015-01-01' and fundingDate<'2016-01-01'")
        else:
            fundings = conn.query("select * from funding where (active is null or active !='N') and"
                                  " fundingDate >='2017-01-01' and fundingDate<'2018-01-01'")

        for funding in fundings:
            if funding is not None and funding["corporateId"] is not None:
                # logger.info(funding)
                corporate = conn.get("select * from corporate where id=%s and (active is null or active !='N')",
                                     funding["corporateId"])
                cs = conn.query("select id from company where corporateId=%s and (active is null or active!='N')",
                                funding["corporateId"])

                if len(cs) > 0 and corporate is not None:
                    cnt_event += 1
                    if funding["round"] is not None and funding["round"] in [1105,1106,1110]:
                        cnt_event_stock += 1
                        if funding["corporateId"] not in css:
                            css.append(funding["corporateId"])
                    else:
                        cnt_event_nestock += 1
                        if funding["corporateId"] not in cnes:
                            cnes.append(funding["corporateId"])

                    if funding["corporateId"] not in corporateIds:
                        corporateIds.append(funding["corporateId"])

                    if corporate["locationId"] is not None and corporate["locationId"] > 370:
                        cnt_f += 1
                        if funding["corporateId"] not in cfs:
                            cfs.append(funding["corporateId"])
                    else:
                        cnt_d += 1
                        if funding["corporateId"] not in cds:
                            cds.append(funding["corporateId"])


                    for c in cs:
                        # logger.info(c)
                        if c["id"] not in companyIds:
                            companyIds.append(c["id"])
                            # break
        cnt_company = len(companyIds)
        cnt_corporate = len(corporateIds)

        de.extend([{"item": year + "总融资事件数", "count": cnt_event},
                   {"item": year + "总上市融资事件数", "count": cnt_event_stock},
                   {"item": year + "总非上市融资事件数", "count": cnt_event_nestock},
                   {"item": year + "总上市融资corporate数", "count": len(css)},
                   {"item": year + "总非上市融资corporate数", "count": len(cnes)},
                   {"item": year + "总涉及项目数", "count": cnt_company},
                   {"item": year + "总涉及corporate数", "count": cnt_corporate},
                   {"item": year + "国内融资事件数", "count": cnt_d},
                   {"item": year + "国外融资事件数", "count": cnt_f},
                   {"item": year + "总国内涉及corporate数", "count": len(cds)},
                   {"item": year + "总国外涉及corporate数", "count": len(cfs)},
                   ])

    conn.close()
    mongo.close()
    return de

def fundingP_check():
    de = []
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    # cnt_event = 0
    # corporateIds = []
    # companyIds = []
    # cnt_event_stock = 0
    # cnt_event_nestock = 0

    for year in ["2013", "2014", "2015", "2016", "2017"]:
        cnt_event = 0
        corporateIds = []
        companyIds = []
        cnt_event_stock = 0
        cnt_event_nestock = 0
        cnt_d = 0
        cnt_f = 0
        cds = []
        cfs = []
        css = []
        cnes = []
        if year == "2016":
            fundings = conn.query("select * from funding where (active is null or active !='N') and "
                                  "("
                                  "(publishDate is not null and publishDate>='2016-01-01' and publishDate<'2017-01-01')"
                                  " or "
                                  "(publishDate is null and fundingDate>='2016-01-01' and fundingDate<'2017-01-01')"
                                  ")")
        elif year == "2015":
            fundings = conn.query("select * from funding where (active is null or active !='N') and "
                                  "("
                                  "(publishDate is not null and publishDate>='2015-01-01' and publishDate<'2016-01-01')"
                                  " or "
                                  "(publishDate is null and fundingDate>='2015-01-01' and fundingDate<'2016-01-01')"
                                  ")")
        elif year == "2014":
            fundings = conn.query("select * from funding where (active is null or active !='N') and "
                                  "("
                                  "(publishDate is not null and publishDate>='2014-01-01' and publishDate<'2015-01-01')"
                                  " or "
                                  "(publishDate is null and fundingDate>='2014-01-01' and fundingDate<'2015-01-01')"
                                  ")")

        elif year == "2013":
            fundings = conn.query("select * from funding where (active is null or active !='N') and "
                                  "("
                                  "(publishDate is not null and publishDate>='2013-01-01' and publishDate<'2014-01-01')"
                                  " or "
                                  "(publishDate is null and fundingDate>='2013-01-01' and fundingDate<'2014-01-01')"
                                  ")")

        else:
            fundings = conn.query("select * from funding where (active is null or active !='N') and "
                                  "("
                                  "(publishDate is not null and publishDate>='2017-01-01' and publishDate<'2018-01-01')"
                                  " or "
                                  "(publishDate is null and fundingDate>='2017-01-01' and fundingDate<'2018-01-01')"
                                  ")")

        for funding in fundings:
            if funding is not None and funding["corporateId"] is not None:
                # logger.info(funding)
                corporate = conn.get("select * from corporate where id=%s and (active is null or active !='N')",
                                     funding["corporateId"])
                cs = conn.query("select id from company where corporateId=%s and (active is null or active!='N')",
                                funding["corporateId"])

                if len(cs) > 0 and corporate is not None:
                    cnt_event += 1
                    if funding["round"] is not None and funding["round"] in [1105,1106,1110]:
                        cnt_event_stock += 1
                        if funding["corporateId"] not in css:
                            css.append(funding["corporateId"])
                    else:
                        cnt_event_nestock += 1
                        if funding["corporateId"] not in cnes:
                            cnes.append(funding["corporateId"])

                    if funding["corporateId"] not in corporateIds:
                        corporateIds.append(funding["corporateId"])

                    if corporate["locationId"] is not None and corporate["locationId"] > 370:
                        cnt_f += 1
                        if funding["corporateId"] not in cfs:
                            cfs.append(funding["corporateId"])
                    else:
                        cnt_d += 1
                        if funding["corporateId"] not in cds:
                            cds.append(funding["corporateId"])


                    for c in cs:
                        # logger.info(c)
                        if c["id"] not in companyIds:
                            companyIds.append(c["id"])
                            # break
        cnt_company = len(companyIds)
        cnt_corporate = len(corporateIds)

        de.extend([{"item": year + "披露总融资事件数", "count": cnt_event},
                   {"item": year + "披露总上市融资事件数", "count": cnt_event_stock},
                   {"item": year + "披露总非上市融资事件数", "count": cnt_event_nestock},
                   {"item": year + "披露总上市融资corporate数", "count": len(css)},
                   {"item": year + "披露总非上市融资corporate数", "count": len(cnes)},
                   {"item": year + "披露总涉及项目数", "count": cnt_company},
                   {"item": year + "披露总涉及corporate数", "count": cnt_corporate},
                   {"item": year + "披露国内融资事件数", "count": cnt_d},
                   {"item": year + "披露国外融资事件数", "count": cnt_f},
                   {"item": year + "披露总国内涉及corporate数", "count": len(cds)},
                   {"item": year + "披露总国外涉及corporate数", "count": len(cfs)},
                   ])

    conn.close()
    mongo.close()
    return de

def db_check():
    dbb = []
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    sql1 = "select count(*) from company c left join corporate co on c.corporateId = co.id " \
           " where (c.active is null or c.active !='N') and (co.active is null or co.active !='N')"
    count = conn.get(sql1)
    dbb.append({"item": "产品线数", "count": count["count(*)"]})
    sql2 = "select count(*) from investor where (active is null or active !='N')"
    count = conn.get(sql2)
    dbb.append({"item": "创投机构数", "count": count["count(*)"]})
    collection_news = mongo.article.news
    cnt = collection_news.find({}).count() - collection_news.find({"type": 61000}).count()
    dbb.append({"item": "总新闻数", "count": cnt})

    dt = datetime.date.today()
    prev_1week_first = dt - datetime.timedelta(dt.weekday()) + datetime.timedelta(weeks=-1)
    prev_1week_end = prev_1week_first + datetime.timedelta(days=5)
    logger.info("%s - %s", prev_1week_first, prev_1week_end)

    p1f = datetime.datetime(prev_1week_first.year, prev_1week_first.month, prev_1week_first.day)
    p1e = datetime.datetime(prev_1week_end.year, prev_1week_end.month, prev_1week_end.day)

    sql3 = "select count(*) from company where createTime>=%s and createTime<=%s"
    count = conn.get(sql3, prev_1week_first, prev_1week_end)
    dbb.append({"item": "每天新增产品线数（包含未发布或者不发布）", "count": count["count(*)"]/5})

    cnt = collection_news.find({"type": {"$ne":61000},"createTime": {"$gt":p1f,"$lt":p1e}}).count()
    dbb.append({"item": "每天新增新闻数", "count": cnt/5})

    cnt = collection_news.find({"category": 60101, "createTime": {"$gt": p1f, "$lt": p1e}}).count()
    dbb.append({"item": "每天新增融资新闻数", "count": cnt / 5})

    # collection_itunes = mongo.market.itunes
    # collection_android = mongo.market.android
    # cnt = collection_itunes.find({}).count()
    # dbb.append({"item": "每天新增融资新闻数", "count": cnt / 5})
    # cnt = collection_android.find({}).count()
    # dbb.append({"item": "每天新增融资新闻数", "count": cnt / 5})


    # dbb.append({"item": "每天新增融资新闻数", "count": cnt})
    # prev_12week_first = dt - datetime.timedelta(dt.weekday()) + datetime.timedelta(weeks=-12)
    # prev_12week_end = prev_12week_first + datetime.timedelta(days=83)

    conn.close()
    mongo.close()
    return dbb




if __name__ == '__main__':
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    logger.info(today)
    stat0 = db_check()
    for item in stat0:
        logger.info("%s - %s", item["item"], item["count"])
    stat1 = yitai_check()
    for item in stat1:
        logger.info("%s - %s", item["item"], item["count"])
    stat2 = investor_check()
    for item in stat2:
        logger.info("%s - %s", item["item"], item["count"])
    # stat3 = funding_check()
    # for item in stat3:
    #     logger.info("%s - %s", item["item"], item["count"])
    # stat4 = fundingP_check()
    # for item in stat4:
    #     logger.info("%s - %s", item["item"], item["count"])



