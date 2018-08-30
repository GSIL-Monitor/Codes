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

#logger
loghelper.init_logger("investor_ranking", stream=True)
logger = loghelper.get_logger("investor_ranking")

conn = None


def get_today_date():
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    start_date = "%s-%s-%s" % (today.year, today.month, today.day)
    end_date = "%s-%s-%s" % (tomorrow.year, tomorrow.month, tomorrow.day)
    return start_date, end_date


def get_thisweek_date():
    date1 = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    date2 = date1 + datetime.timedelta(days=7)
    start_date = "%s-%s-%s" % (date1.year, date1.month, date1.day)
    end_date = "%s-%s-%s" % (date2.year, date2.month, date2.day)
    return start_date, end_date


def get_thismonth_date():
    date1 = datetime.date.today() - datetime.timedelta(days=datetime.datetime.now().day - 1)
    year = date1.year
    month = date1.month
    if month == 12:
        year += 1
        month =1
    else:
        month += 1
    date2 = datetime.datetime(year, month, 1)
    start_date = "%s-%s-%s" % (date1.year, date1.month, date1.day)
    end_date = "%s-%s-%s" % (date2.year, date2.month, date2.day)
    return start_date, end_date


def get_thisquarter_date():
    date1 = datetime.date.today() - datetime.timedelta(days=datetime.datetime.now().day - 1)
    year = date1.year
    month = date1.month
    quarter = int((month - 1)/3) + 1
    month1 = (quarter -1)*3 + 1
    month2 = month1 + 3
    start_date = "%s-%s-%s" % (year, month1, 1)
    end_date = "%s-%s-%s" % (year, month2, 1)
    return start_date, end_date


def get_thisyear_date():
    today = datetime.datetime.now()
    thisyear = today.year
    nextyear = thisyear + 1
    start_date = "%s-01-01" % thisyear
    end_date = "%s-01-01" % nextyear
    return start_date, end_date


def tongji_all():
    global conn
    conn = db.connect_torndb_proxy()

    start_date, end_date = get_today_date()
    tongji_funding_investment(start_date, end_date)
    tongji_news_count(start_date, end_date)

    start_date, end_date = get_thisweek_date()
    tongji_news_count(start_date, end_date)
    tongji_exit_count(start_date, end_date)
    tongji_nextround_count(start_date, end_date)

    # start_date, end_date = get_thismonth_date()

    start_date, end_date = get_thisquarter_date()
    tongji_funding_count(start_date, end_date)
    tongji_news_count(start_date, end_date)
    tongji_exit_count(start_date, end_date)
    tongji_nextround_count(start_date, end_date)

    start_date, end_date = get_thisyear_date()
    tongji_funding_count(start_date, end_date)
    tongji_news_count(start_date, end_date)
    tongji_exit_count(start_date, end_date)
    tongji_nextround_count(start_date, end_date)

    conn.close()


def tongji_incr():
    global conn
    conn = db.connect_torndb_proxy()

    start_date, end_date = get_today_date()
    tongji_funding_investment(start_date, end_date)
    tongji_news_count(start_date, end_date)

    start_date, end_date = get_thisweek_date()
    tongji_news_count(start_date, end_date)
    tongji_exit_count(start_date, end_date)
    tongji_nextround_count(start_date, end_date)

    start_date, end_date = get_thisyear_date()
    tongji_funding_count(start_date, end_date)
    tongji_news_count(start_date, end_date)
    tongji_exit_count(start_date, end_date)
    tongji_nextround_count(start_date, end_date)

    conn.close()


def tongji_funding_count(start_date, end_date):
    logger.info(u"融资事件数量统计 %s -> %s", start_date, end_date)
    TYPE = 81001

    results = conn.query(
        "select distinct(r.investorId) investorId from "
        "funding_investor_rel r "
        "join funding f on r.fundingId=f.id "
        "join company cp on f.companyId=cp.id "
        "join investor i on r.investorId=i.id "
        "where "
        "(r.active is null or r.active='Y') and "
        "(f.active is null or f.active='Y') and "
        "(cp.active is null or cp.active='Y') and "
        "(i.active is null or i.active='Y') and "
        "i.online='Y' and i.locationId>0 and i.locationId<371 and "
        "("
        "(f.publishDate is null and f.fundingDate>=%s and f.fundingDate<%s) "
        "or "
        "(f.publishDate is not null and f.publishDate>=%s and f.publishDate<%s)"
        ") ",
        start_date, end_date, start_date, end_date
        )
    investor_ids = [result["investorId"] for result in results]
    # logger.info("%s", ",".join([str(id) for id in investor_ids]))

    # calc cnt
    investors_tongji = {}
    for investor_id in investor_ids:
        result = conn.get(
            "select count(*) cnt from "
            "(select * from funding_investor_rel where investorId=%s and (active is null or active='Y')) r "
            "join funding f on r.fundingId=f.id "
            "join company cp on f.companyId=cp.id "
            "where "
            "(f.active is null or f.active='Y') and "
            "(cp.active is null or cp.active='Y') and "
            "("
            "(f.publishDate is null and f.fundingDate>=%s and f.fundingDate<%s) "
            "or "
            "(f.publishDate is not null and f.publishDate>=%s and f.publishDate<%s)"
            ") ",
            investor_id, start_date, end_date, start_date, end_date
            )
        investors_tongji[investor_id] = result["cnt"]

    if len(investors_tongji) > 0:
        save_tongji(TYPE, start_date, end_date, investors_tongji)
        calc_rank_and_defeat(TYPE, start_date, end_date)


def tongji_funding_investment(start_date, end_date):
    logger.info(u"融资事件总金额统计 %s -> %s", start_date, end_date)
    TYPE = 81002

    fundings = conn.query(
        "select f.* from "
        "funding f "
        "join company cp on f.companyId=cp.id "
        "where "
        "(f.active is null or f.active='Y') and "
        "(cp.active is null or cp.active='Y') and "
        "("
        "(f.publishDate is null and f.fundingDate>=%s and f.fundingDate<%s) "
        "or "
        "(f.publishDate is not null and f.publishDate>=%s and f.publishDate<%s) "
        "or "
        "(f.publishDate<f.fundingDate and f.fundingDate>=%s and f.fundingDate<%s)"
        ") ",
        start_date, end_date, start_date, end_date, start_date, end_date
        )


    # calc
    exchange_rates = {}
    items = conn.query("select * from exchange_rate")
    for item in items:
        exchange_rates[item["currency"]] = item["rate"]

    investors_tongji = {}
    for funding in fundings:
        currency = funding["currency"]
        investment = funding["investment"]
        precise = funding["precise"]
        if investment is None or investment < 10000:
            investment = 0
        if precise == 'N' and investment > 0:
            investment = 5*10**(len(str(investment))-1)
        exchange_rate = exchange_rates.get(currency)
        if exchange_rate is None:
            investment = 0
        else:
            investment = int(investment * exchange_rate)

        investment = int(investment / 10000)
        investors = conn.query("select * from funding_investor_rel r join investor i on r.investorId=i.id "
                               "where "
                               "(r.active is null or r.active='Y') and "
                               "(i.active is null or i.active='Y') and "
                               "i.online='Y' and i.locationId>0 and i.locationId<371 and "
                               "fundingId=%s",
                               funding["id"])
        for investor in investors:
            investor_id = investor["investorId"]
            logger.info(investor["name"])
            key = str(investor_id) + "|" + str(funding["id"])
            investors_tongji[key] = investment

    if len(investors_tongji) > 0:
        save_tongji2(TYPE, start_date, end_date, investors_tongji)
        calc_rank_and_defeat(TYPE, start_date, end_date)


def tongji_funding_investment2(start_date, end_date):
    # 这个统计按投资机构累计了金额，暂不需要
    logger.info(u"融资事件总金额统计 %s -> %s", start_date, end_date)
    TYPE = 81002

    fundings = conn.query(
        "select f.* from "
        "funding f "
        "join company cp on f.companyId=cp.id "
        "where "
        "(f.active is null or f.active='Y') and "
        "(cp.active is null or cp.active='Y') and "
        "("
        "(f.publishDate is null and f.fundingDate>=%s and f.fundingDate<%s) "
        "or "
        "(f.publishDate is not null and f.publishDate>=%s and f.publishDate<%s) "
        "or "
        "(f.publishDate<f.fundingDate and f.fundingDate>=%s and f.fundingDate<%s)"
        ") ",
        start_date, end_date, start_date, end_date, start_date, end_date
        )


    # calc
    exchange_rates = {}
    items = conn.query("select * from exchange_rate")
    for item in items:
        exchange_rates[item["currency"]] = item["rate"]

    investors_tongji = {}
    for funding in fundings:
        currency = funding["currency"]
        investment = funding["investment"]
        precise = funding["precise"]
        if investment is None or investment < 10000:
            investment = 0
        if precise == 'N' and investment > 0:
            investment = 5*10**(len(str(investment))-1)
        exchange_rate = exchange_rates.get(currency)
        if exchange_rate is None:
            investment = 0
        else:
            investment = int(investment * exchange_rate)

        investment = int(investment / 10000)
        investors = conn.query("select * from funding_investor_rel r join investor i on r.investorId=i.id "
                               "where "
                               "(r.active is null or r.active='Y') and "
                               "(i.active is null or i.active='Y') and "
                               "i.online='Y' and i.locationId>0 and i.locationId<371 and "
                               "fundingId=%s",
                               funding["id"])
        for investor in investors:
            investor_id = investor["investorId"]
            logger.info(investor["name"])
            if investors_tongji.has_key(investor_id):
                investors_tongji[investor_id] += investment
            else:
                investors_tongji[investor_id] = investment

    if len(investors_tongji) > 0:
        save_tongji(TYPE, start_date, end_date, investors_tongji)
        calc_rank_and_defeat(TYPE, start_date, end_date)


def tongji_news_count(start_date, end_date):
    logger.info(u"新闻数量统计 %s -> %s", start_date, end_date)
    TYPE = 81003

    start = datetime.datetime.strptime(start_date, "%Y-%m-%d") - datetime.timedelta(hours=8)
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.timedelta(hours=8)
    # logger.info("%s -> %s", start, end)
    mongo = db.connect_mongo()
    items = list(mongo.article.news.find({"investorIds":{"$elemMatch":{"$ne":None}},
                                          "date":{"$gte": start,"$lt": end}},
                                         {"investorIds": True,"date":True}))
    mongo.close()

    investors_tongji = {}
    for item in items:
        # logger.info(item)
        investor_ids = item["investorIds"]
        for investor_id in investor_ids:
            investor = conn.get("select * from investor where id=%s", investor_id)
            if investor is None:
                continue
            if investor["active"] == 'N':
                continue
            if investor["online"] != 'Y':
                continue
            if investor["locationId"] == 0 or investor["locationId"]>=371:
                continue
            if investors_tongji.has_key(investor_id):
                investors_tongji[investor_id] += 1
            else:
                investors_tongji[investor_id] = 1

    if len(investors_tongji) > 0:
        save_tongji(TYPE, start_date, end_date, investors_tongji)
        calc_rank_and_defeat(TYPE, start_date, end_date)


exit_rounds_str = "1110, 1120"

def tongji_exit_count(start_date, end_date):
    logger.info(u"退出事件数量统计 %s -> %s", start_date, end_date)
    # IPO, 收购
    TYPE = 81004

    fundings = conn.query(
        "select f.* from "
        "funding f "
        "join company cp on f.companyId=cp.id "
        "where "
        "(f.active is null or f.active='Y') and "
        "(cp.active is null or cp.active='Y') and "
        "("
        "(f.publishDate is null and f.fundingDate>=%s and f.fundingDate<%s) "
        "or "
        "(f.publishDate is not null and f.publishDate>=%s and f.publishDate<%s)"
        "or "
        "(f.publishDate<f.fundingDate and f.fundingDate>=%s and f.fundingDate<%s)"
        ") and "
        "f.round in (" + exit_rounds_str + ")",
        start_date, end_date, start_date, end_date, start_date, end_date
        )

    investors_tongji = {}
    for funding in fundings:
        previous_investor_ids = get_previous_investors(funding)
        # logger.info("fundingId: %s, previous investors: %s", funding["id"], ",".join([str(id) for id in previous_investor_ids]))
        for investor_id in previous_investor_ids:
            if investors_tongji.has_key(investor_id):
                investors_tongji[investor_id] += 1
            else:
                investors_tongji[investor_id] = 1

    if len(investors_tongji) > 0:
        save_tongji(TYPE, start_date, end_date, investors_tongji)
        calc_rank_and_defeat(TYPE, start_date, end_date)


def tongji_nextround_count(start_date, end_date):
    logger.info(u"下轮融资数量统计 %s -> %s", start_date, end_date)
    TYPE = 81005

    fundings = conn.query(
        "select f.* from "
        "funding f "
        "join company cp on f.companyId=cp.id "
        "where "
        "(f.active is null or f.active='Y') and "
        "(cp.active is null or cp.active='Y') and "
        "("
        "(f.publishDate is null and f.fundingDate>=%s and f.fundingDate<%s) "
        "or "
        "(f.publishDate is not null and f.publishDate>=%s and f.publishDate<%s)"
        "or "
        "(f.publishDate<f.fundingDate and f.fundingDate>=%s and f.fundingDate<%s)"
        ") and "
        "f.round not in (" + exit_rounds_str + ")",
        start_date, end_date, start_date, end_date, start_date, end_date
        )

    investors_tongji = {}
    for funding in fundings:
        previous_investor_ids = get_previous_investors(funding)
        # logger.info("fundingId: %s, previous investors: %s", funding["id"], ",".join([str(id) for id in previous_investor_ids]))
        for investor_id in previous_investor_ids:
            if investors_tongji.has_key(investor_id):
                investors_tongji[investor_id] += 1
            else:
                investors_tongji[investor_id] = 1

    if len(investors_tongji) > 0:
        save_tongji(TYPE, start_date, end_date, investors_tongji)
        calc_rank_and_defeat(TYPE, start_date, end_date)


def save_tongji(TYPE, start_date, end_date, investors_tongji):
    # delete
    investor_ids = [investorId for investorId, cnt in investors_tongji.items()]
    conn.execute("delete from investor_ranking where type=%s and fromDate=%s and toDate=%s and "
                 "investorId not in (" + ",".join([str(id) for id in investor_ids]) + ")",
                 TYPE, start_date, end_date)

    # save
    for investor_id, cnt in investors_tongji.items():
        item = conn.get("select * from investor_ranking where type=%s and fromDate=%s and toDate=%s and "
                        "investorId=%s", TYPE, start_date, end_date, investor_id)
        if item is None:
            conn.insert("insert investor_ranking(investorId,type,fromDate,toDate,cnt,createTime,modifyTime) "
                        "values(%s,%s,%s,%s,%s,now(),now())",
                        investor_id, TYPE, start_date, end_date, cnt)
        else:
            conn.update("update investor_ranking set cnt=%s, modifyTime=now() where id=%s",
                        cnt, item["id"])


def save_tongji2(TYPE, start_date, end_date, investors_tongji):
    investor_funding_ids = []
    keys = [investorId for investorId, cnt in investors_tongji.items()]
    for key in keys:
        strs = key.split("|")
        investor_id = int(strs[0])
        funding_id = int (strs[1])
        investor_funding_ids.append((investor_id, funding_id))

    # delete
    conn.execute("delete from investor_ranking where type=%s and fromDate=%s and toDate=%s and "
                 "investorId not in (" + ",".join([str(investor_id) for investor_id, funding_id in investor_funding_ids]) + ")",
                 TYPE, start_date, end_date)
    conn.execute("delete from investor_ranking where type=%s and fromDate=%s and toDate=%s and "
                 "fundingId not in (" + ",".join(
        [str(funding_id) for investor_id, funding_id in investor_funding_ids]) + ")",
                 TYPE, start_date, end_date)

    # save
    for key, cnt in investors_tongji.items():
        strs = key.split("|")
        investor_id = int(strs[0])
        funding_id = int(strs[1])

        item = conn.get("select * from investor_ranking where type=%s and fromDate=%s and toDate=%s and "
                        "investorId=%s and fundingId=%s", TYPE, start_date, end_date, investor_id, funding_id)
        if item is None:
            conn.insert("insert investor_ranking(investorId,fundingId,type,fromDate,toDate,cnt,createTime,modifyTime) "
                        "values(%s,%s,%s,%s,%s,%s,now(),now())",
                        investor_id, funding_id, TYPE, start_date, end_date, cnt)
        else:
            conn.update("update investor_ranking set cnt=%s, modifyTime=now() where id=%s",
                        cnt, item["id"])


def get_previous_investors(funding):
    funding_investor_rels = conn.query("select * from funding_investor_rel "
                                       "where "
                                       "(active is null or active='Y') and "
                                       "fundingId=%s",
                                       funding["id"])
    current_investor_ids = [r["investorId"] for r in funding_investor_rels]

    # 以往投资方
    company_id = funding["companyId"]
    funding_date = funding["fundingDate"]
    previous_investors = conn.query("select distinct(r.investorId) investorId from "
                                    "funding_investor_rel r "
                                    "join funding f on r.fundingId=f.id "
                                    "join investor i on r.investorId=i.id "
                                    "where "
                                    "(r.active is null or r.active='Y') and "
                                    "(i.active is null or i.active='Y') and "
                                    "i.online='Y' and i.locationId>0 and i.locationId<371 and "
                                    "f.companyId=%s and "
                                    "f.fundingDate<%s",
                                    company_id, funding_date
                                    )
    previous_investor_ids = []
    if len(previous_investors) > 0:
        for p in previous_investors:
            investor_id = p["investorId"]
            if investor_id not in current_investor_ids:
                previous_investor_ids.append(investor_id)
    return previous_investor_ids


def calc_rank_and_defeat(TYPE, start_date, end_date):
    # calc rank
    rank = 0
    same_rank = 0
    current_cnt = 10000000
    items = conn.query("select * from investor_ranking where type=%s and fromDate=%s and toDate=%s "
                       "order by cnt desc, id",
                       TYPE, start_date, end_date)
    for item in items:
        cnt = item["cnt"]
        if cnt < current_cnt:
            rank += same_rank + 1
            same_rank = 0
            current_cnt = cnt
        else:
            same_rank += 1
        logger.info("cnt: %s, rank: %s", cnt, rank)
        conn.update("update investor_ranking set rank=%s where id=%s", rank, item["id"])

    # calc defeat
    item = conn.get("select count(*) cnt from investor_ranking where type=%s and fromDate=%s and toDate=%s",
                       TYPE, start_date, end_date)
    investor_cnt = item["cnt"]
    items = conn.query("select * from investor_ranking where type=%s and fromDate=%s and toDate=%s "
                       "order by cnt desc, id",
                       TYPE, start_date, end_date)
    for item in items:
        cnt = item["cnt"]
        result = conn.get("select count(*) cnt from investor_ranking "
                          "where type=%s and fromDate=%s and toDate=%s and cnt<%s",
                          TYPE, start_date, end_date, cnt)
        defeat_cnt = result["cnt"]
        if investor_cnt <= 1:
            defeat = 1
        else:
            defeat = defeat_cnt / (investor_cnt - 1.0)
        logger.info("rank: %s, cnt: %s, defeat: %f", item["rank"], cnt, defeat)
        conn.update("update investor_ranking set defeat=%s where id=%s", defeat, item["id"])


def patch():
    global conn
    conn = db.connect_torndb_proxy()
    # today = datetime.date.today()
    # for i in range(1, 30):
    #     yesterday = today - datetime.timedelta(days=1)
    #     start_date = "%s-%s-%s" % (yesterday.year, yesterday.month, yesterday.day)
    #     end_date = "%s-%s-%s" % (today.year, today.month, today.day)
    #     # logger.info("%s - > %s", start_date, end_date)
    #     tongji_funding_investment(start_date, end_date)
    #     today = yesterday
    start_date = '2018-01-01'
    end_date = '2018-07-01'
    tongji_exit_count(start_date, end_date)
    tongji_nextround_count(start_date, end_date)
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "patch":
            patch()
            exit()

    INTERVAL = 10
    LAST_TONGJI_ALL_TIME = None
    while True:
        now = datetime.datetime.now()
        if now.hour >= 1 and now.hour < 3 and (LAST_TONGJI_ALL_TIME is None or (now - LAST_TONGJI_ALL_TIME).seconds > 10*3600):
            tongji_all()
        else:
            tongji_incr()
        time.sleep(INTERVAL * 60)