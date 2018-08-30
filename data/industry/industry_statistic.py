# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config, db

#logger
loghelper.init_logger("industry_statistic", stream=True)
logger = loghelper.get_logger("industry_statistic")

conn = None
mongo = None


def industry_foundyear_layout(industry_id):
    logger.info("industry_foundyear_layout")
    result = conn.get("select min(cp.establishDate) as start, max(cp.establishDate) as end from industry_company ic "
                      "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                      "join corporate cp on c.corporateId=cp.id and (cp.active is null or cp.active='Y') "
                      "where (ic.active is null or ic.active='Y') and "
                      "cp.locationId < 371 and "
                      "cp.establishDate is not null and ic.industryId=%s", industry_id)
    start = result["start"]
    if start is None:
        return

    start_year = start.year
    this_year = datetime.datetime.now().year

    stat = []
    for year in range(start_year, this_year+1):
        start_date = datetime.datetime(year,1,1)
        end_date = datetime.datetime(year+1,1,1)
        result = conn.get("select count(*) as cnt from industry_company ic "
                      "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                      "join corporate cp on c.corporateId=cp.id and (cp.active is null or cp.active='Y') "
                      "where (ic.active is null or ic.active='Y') and "
                      "cp.locationId < 371 and "
                      "cp.establishDate is not null and ic.industryId=%s "
                      "and cp.establishDate>=%s and cp.establishDate<%s",
                          industry_id, start_date, end_date)
        cnt = result["cnt"]
        stat.append((year, cnt))
        logger.info("from: %s, to: %s, cnt: %s", start_date, end_date, cnt)

    mongo.industry.industry_foundyear_layout.remove({"industryId": industry_id})
    for year, cnt in stat:
        mongo.industry.industry_foundyear_layout.insert({
            "industryId": int(industry_id),
            "year": int(year),
            "count": int(cnt),
            "createTime": datetime.datetime.utcnow()
        })


def industry_funding_trend(industry_id):
    logger.info("industry_funding_trend")
    result = conn.get("select min(f.fundingDate) as start from funding f "
                      "join industry_company ic on f.companyId=ic.companyId and (ic.active is null or ic.active='Y') "
                      "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                      "join corporate cp on c.corporateId=cp.id and (cp.active is null or cp.active='Y') "
                      "where "
                      "(f.active is null or f.active!='N') and f.fundingDate is not null and "
                      "cp.locationId<371 and "
                      "ic.industryId=%s",
                      industry_id)
    start = result["start"]
    if start is None:
        return

    start_year = start.year
    start_month = start.month
    today = datetime.datetime.now()
    this_year = today.year
    this_month = today.month
    logger.info("from: %s-%s, to: %s-%s", start_year, start_month, this_year, this_month)

    stat = []
    for year in range(start_year, this_year+1):
        month1= 1
        month2 = 12
        if year == start_year:
            month1 = start_month
        if year == this_year:
            month2 = this_month
        for month in range(month1, month2+1):
            start_date = datetime.datetime(year, month, 1)
            if month >=12:
                end_date = datetime.datetime(year+1, 1, 1)
            else:
                end_date = datetime.datetime(year, month+1, 1)
            result = conn.get("select count(*) as cnt from industry_company ic "
                              "join funding f on ic.companyId=f.companyId and (ic.active is null or ic.active='Y') "
                              "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                              "join corporate cp on c.corporateId=cp.id and (cp.active is null or cp.active='Y') "
                              "where (f.active is null or f.active!='N') "
                              "and cp.locationId<371 "
                              "and ic.industryId=%s "
                              "and f.fundingDate>=%s and f.fundingDate<%s",
                              industry_id, start_date, end_date)
            cnt = result["cnt"]
            stat.append((year,month, cnt))
            logger.info("from: %s, to: %s, cnt: %s", start_date, end_date, cnt)

    mongo.industry.industry_funding_trend.remove({"industryId": industry_id})
    for year, month, cnt in stat:
        mongo.industry.industry_funding_trend.insert({
            "industryId": int(industry_id),
            "type": "month",
            "year": int(year),
            "month": int(month),
            "count": int(cnt),
            "createTime": datetime.datetime.utcnow()
        })


def industry_investor_layout(industry_id):
    logger.info("industry_investor_layout")

    stat = []
    results = conn.query("select r.investorId as investorId, count(*) as cnt from industry_company ic "
                        "join funding f on ic.companyId=f.companyId and (f.active is null or f.active!='N') "
                        "join funding_investor_rel r on f.id=r.fundingId and (r.active is null or r.active!='N')"
                        "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                        "join corporate cp on c.corporateId=cp.id and (cp.active is null or cp.active='Y') "
                        "where (ic.active is null or ic.active='Y') "
                         "and cp.locationId<371 "
                         "and ic.industryId=%s "
                        "group by r.investorId",
                        industry_id
                        )
    for result in results:
        investor_id = result["investorId"]
        cnt = result["cnt"]
        investor = conn.get("select * from investor where id=%s", investor_id)
        result = conn.get("select max(f.fundingDate) as fundingDate from industry_company ic "
                        "join funding f on ic.companyId=f.companyId and (f.active is null or f.active!='N') "
                        "join funding_investor_rel r on f.id=r.fundingId and (r.active is null or r.active!='N') "
                        "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                        "join corporate cp on c.corporateId=cp.id and (cp.active is null or cp.active='Y') "
                        "where "
                        "(ic.active is null or ic.active='Y') "
                          "and cp.locationId<371 "
                        "and ic.industryId=%s and r.investorId=%s",
                        industry_id, investor_id
                        )
        last_funding_date = result["fundingDate"]
        stat.append((investor_id, investor["name"], cnt, last_funding_date))
        logger.info("%s -> %s -> %s", investor["name"], cnt, last_funding_date)

    mongo.industry.industry_investor_layout.remove({"industryId": industry_id})
    for investor_id, investor_name, cnt, last_funding_date in stat:
        mongo.industry.industry_investor_layout.insert({
            "industryId": int(industry_id),
            "investorId": int(investor_id),
            "investorName": investor_name,
            "count": int(cnt),
            "lastFundingDate": last_funding_date,
            "createTime": datetime.datetime.utcnow()
        })


def industry_location_layout(industry_id):
    logger.info("industry_location_layout")

    stat = []
    results = conn.query("select cp.locationId as locationId, count(*) as cnt from industry_company ic "
                      "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                      "join corporate cp on c.corporateId=cp.id and (cp.active is null or cp.active='Y') "
                      "where (ic.active is null or ic.active='Y') and ic.industryId=%s "
                      "and cp.locationId is not null and cp.locationId<371 "
                      "group by cp.locationId",
                      industry_id)
    for result in results:
        location_id = result["locationId"]
        cnt = result["cnt"]
        location = conn.get("select * from location where locationId=%s", location_id)
        location_name = location["locationName"]
        if location_id != 0: # 未知地区
            stat.append((location_id, location_name, cnt))
        logger.info("%s: %s -> %s", location_id, location_name, cnt)

    mongo.industry.industry_location_layout.remove({"industryId": industry_id})
    for location_id, location_name, cnt in stat:
        mongo.industry.industry_location_layout.insert({
            "industryId": int(industry_id),
            "locationId": int(location_id),
            "locationName": location_name,
            "count": int(cnt),
            "createTime": datetime.datetime.utcnow()
        })


def industry_rank(industry_id):
    logger.info("industry_rank")
    today = datetime.datetime.now()
    start = datetime.datetime(today.year, today.month, today.day)
    start = start - datetime.timedelta(days=7)
    result = conn.get("select count(*) cnt from industry_news "
                      "where (active is null or active='Y') and "
                      "industryId=%s and "
                      "newsTime>=%s",
                      industry_id, start)
    cnt = result["cnt"]
    conn.update("update industry set rank=%s where id=%s",
                cnt, industry_id)


def industry_news_trend(industry_id):
    logger.info("industry_news_trend")
    mongo.industry.industry_news_trend.remove({"industryId": industry_id, "type": "day"})
    today = datetime.datetime.now()
    for diff in range(0,31):
        d = today - datetime.timedelta(days=diff)
        start = datetime.datetime(d.year, d.month, d.day)
        end = start + datetime.timedelta(days=1)
        result = conn.get("select count(*) cnt from industry_news "
                          "where (active is null or active='Y') and "
                          "industryId=%s and "
                          "newsTime>=%s and newsTime<%s",
                          industry_id, start, end)
        cnt = result["cnt"]
        logger.info("start: %s, end: %s, cnt: %s", start, end, cnt)
        mongo.industry.industry_news_trend.insert({
                "industryId": int(industry_id),
                "type": "day",
                "date": start,
                "count": int(cnt),
                "createTime": datetime.datetime.utcnow()
            })



def industry_news_trend_month(industry_id):
    logger.info("industry_news_trend_month")
    mongo.industry.industry_news_trend.remove({"industryId": industry_id, "type": "month"})
    today = datetime.datetime.now()
    this_month = datetime.datetime(today.year,today.month,1)
    for diff in range(0, 12):
        start = datetime.datetime(this_month.year, this_month.month, 1)
        _end = start + datetime.timedelta(days=31)
        end = datetime.datetime(_end.year, _end.month, 1)
        _start = start + datetime.timedelta(days=-1)
        this_month = datetime.datetime(_start.year,_start.month,1)
        result = conn.get("select count(*) cnt from industry_news "
                          "where (active is null or active='Y') and "
                          "industryId=%s and "
                          "newsTime>=%s and newsTime<%s",
                          industry_id, start, end)
        cnt = result["cnt"]
        logger.info("start: %s, end: %s, cnt: %s", start, end, cnt)
        mongo.industry.industry_news_trend.insert({
            "industryId": int(industry_id),
            "type": "month",
            "date": start,
            "count": int(cnt),
            "createTime": datetime.datetime.utcnow()
        })


def industry_round_layout(industry_id):
    logger.info("industry_round_layout")
    # 种子轮
    seed = industry_round_count(industry_id, 1010)
    # 天使轮
    angel = industry_round_count(industry_id, 1011)
    # Pre-A
    preA = industry_round_count(industry_id, 1020)
    # A
    A = industry_round_count(industry_id, 1030,1031,1032,1033)
    # B
    B = industry_round_count(industry_id, 1039,1040,1041,1042,1043)
    # C
    C = industry_round_count(industry_id, 1049,1050,1051,1052)
    # D
    D = industry_round_count(industry_id, 1059,1060,1061,1062,1070,1071,1072,1080,1081,1082,1090)
    # pre-IPO
    preIPO = industry_round_count(industry_id, 1100)
    # 新三板
    xsb = industry_round_count(industry_id, 1105,1106)
    # IPO
    ipo = industry_round_count(industry_id, 1110)
    # 并购
    acquired = industry_round_count(industry_id, 1120)
    # 战略投资
    strategy = industry_round_count(industry_id, 1130)
    # 私有化
    private = industry_round_count(industry_id, 1140)
    # 债权融资
    debt = industry_round_count(industry_id, 1150)
    # 股权转让
    share = industry_round_count(industry_id, 1160)
    logger.info(u"seed: %s, angel: %s, preA: %s, A: %s, B:%s, C:%s, D:%s, preIPO:%s, 新三板:%s, IPO: %s,并购: %s, 战略投资: %s, "
                u"私有化: %s, 债权融资: %s, 股权转让: %s",
                seed, angel, preA, A, B, C, D, preIPO, xsb, ipo, acquired, strategy, private, debt, share)

    mongo.industry.industry_round_layout.remove({"industryId": industry_id})
    insert_industry_round_layout(industry_id, u"种子轮", seed, 1)
    insert_industry_round_layout(industry_id, u"天使轮", angel, 2)
    insert_industry_round_layout(industry_id, u"Pre-A轮", preA, 3)
    insert_industry_round_layout(industry_id, u"A轮", A, 4)
    insert_industry_round_layout(industry_id, u"B轮", B, 5)
    insert_industry_round_layout(industry_id, u"C轮", C, 6)
    insert_industry_round_layout(industry_id, u"D轮及以后", D, 7)
    insert_industry_round_layout(industry_id, u"pre-IPO", preIPO, 8)
    insert_industry_round_layout(industry_id, u"新三板", xsb, 9)
    insert_industry_round_layout(industry_id, u"IPO", ipo, 10)
    insert_industry_round_layout(industry_id, u"并购", acquired, 11)
    insert_industry_round_layout(industry_id, u"战略投资", strategy, 12)
    insert_industry_round_layout(industry_id, u"私有化", private, 13)
    insert_industry_round_layout(industry_id, u"债权融资", debt, 14)
    insert_industry_round_layout(industry_id, u"股权转让", share, 15)


def insert_industry_round_layout(industry_id, round, cnt, sort):
    if cnt != 0:
        mongo.industry.industry_round_layout.insert({
            "industryId": int(industry_id),
            "round": round,
            "count": int(cnt),
            "sort": int(sort),
            "createTime": datetime.datetime.utcnow()
        })


def industry_round_count(industry_id, *rounds):
    rounds_str = ",".join([str(i) for i in rounds])
    result = conn.get("select count(*) cnt from funding f "
                      "join industry_company ic on f.companyId=ic.companyId and (ic.active is null or ic.active='Y') "
                      "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                      "join corporate cp on c.corporateId=cp.id and (cp.active is null or cp.active='Y') "
                      "where "
                      "(f.active is null or f.active!='N') and f.fundingDate is not null and "
                      "cp.locationId<371 and "
                      "ic.industryId=%s and f.round in (" + rounds_str + ")",
                      industry_id)
    return result["cnt"]


def industry_update_company_count(industry_id):
    result = conn.get("select count(*) cnt from industry_company ic "
                      "join company c on ic.companyId=c.id and (c.active is null or c.active='Y') "
                      "where (ic.active is null or ic.active='Y') and ic.industryId=%s",
                      industry_id)
    conn.update("update industry set companyCount=%s where id=%s", result["cnt"], industry_id)


def industry_chain_update_company_count(industry_chain_id):
    result = conn.get("select count(distinct cp.id) cnt from industry_chain c "
                      "join industry_chain_category cate on cate.industryChainId=c.id "
                      "join industry_chain_category_industry_rel rel on rel.industryChainCategoryId=cate.id "
                      "join industry i on rel.industryId=i.id "
                      "join industry_company ic on i.id=ic.industryId "
                      "join company cp on cp.id=ic.companyId "
                      "where (i.active is null or i.active='Y') and "
                      "(rel.active is null or rel.active='Y') and "
                      "(c.active is null or c.active='Y') and "
                      "(ic.active is null or ic.active='Y') and "
                      "(cp.active is null or cp.active='Y') and "
                      "c.id=%s", industry_chain_id)
    conn.update("update industry_chain set companyCount=%s where id=%s", result["cnt"], industry_chain_id)


def main():
    global conn
    global mongo
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()

    industries = conn.query("select * from industry where (active is null or active !='N')")
    for industry in industries:
        logger.info("------------------ %s ----------------", industry["name"])
        industry_id = industry["id"]
        industry_foundyear_layout(industry_id)
        industry_funding_trend(industry_id)
        industry_investor_layout(industry_id)
        industry_location_layout(industry_id)
        industry_news_trend(industry_id)
        industry_news_trend_month(industry_id)
        industry_round_layout(industry_id)
        industry_update_company_count(industry_id)
        industry_rank(industry_id)

    chains = conn.query("select * from industry_chain where (active is null or active !='N')")
    for chain in chains:
        industry_chain_id = chain["id"]
        industry_chain_update_company_count(industry_chain_id)

    conn.close()
    mongo.close()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60*60)