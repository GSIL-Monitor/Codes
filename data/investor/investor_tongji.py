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
loghelper.init_logger("investor_tongji", stream=True)
logger = loghelper.get_logger("investor_tongji")

conn = None


def tongji_all():
    global conn
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    conn = db.connect_torndb_proxy()
    invs = conn.query("select * from investor where (active is null or active='Y')")
    for inv in invs:
        investor_id = inv["id"]
        tongji_investor_total_funding_cnt(investor_id)
        tongji_investor_tag_funding_cnt(investor_id, 175747)    # blockchain
        tongji_investor_year_funding_cnt(investor_id, yesterday.year)
    conn.close()


def tongji_incr():
    global conn
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    conn = db.connect_torndb_proxy()
    invs = conn.query("select distinct investorId from funding_investor_rel r "
                      "join funding f on r.fundingId=f.id "
                      "where (f.active is null or f.active='Y') and "
                      "(r.active is null or r.active='Y') and "
                      "("
                      "f.createTime>date_sub(now(),interval 1 day) or "
                      "f.modifyTime>date_sub(now(),interval 1 day)"
                      ")")
    for inv in invs:
        investor_id = inv["investorId"]
        tongji_investor_total_funding_cnt(investor_id)
        tongji_investor_tag_funding_cnt(investor_id, 175747)    # blockchain
        tongji_investor_year_funding_cnt(investor_id, yesterday.year)
    conn.close()


def tongji_investor_total_funding_cnt(investor_id):
    logger.info("investorId: %s", investor_id)
    result = conn.get("select count(*) cnt from funding_investor_rel r "
                      "join funding f on r.fundingId=f.id "
                      "join company cp on f.companyId=cp.id "
                      "where "
                      "(r.active is null or r.active='Y') and "
                      "(f.active is null or f.active='Y') and "
                      "(cp.active is null or cp.active='Y') and "
                      "r.investorId=%s",
                      investor_id
                      )
    cnt = result["cnt"]
    tongji = conn.get("select * from investor_tongji where "
                      "investorId=%s and tagId is null and fromDate is null and toDate is null", investor_id)
    if tongji is None:
        conn.insert("insert investor_tongji(investorId,cnt,createTime,modifyTime) values(%s,%s,now(),now())",
                    investor_id,cnt)
    else:
        conn.update("update investor_tongji set cnt=%s, modifyTime=now() where id=%s", cnt, tongji["id"])


def tongji_investor_tag_funding_cnt(investor_id, tag_id):
    logger.info("investorId: %s, tagId: %s", investor_id, tag_id)
    result = conn.get("select count(*) cnt from funding_investor_rel r "
                      "join funding f on r.fundingId=f.id "
                      "join company cp on f.companyId=cp.id "
                      "join company_tag_rel tr on cp.id=tr.companyId "
                      "where "
                      "(r.active is null or r.active='Y') and "
                      "(f.active is null or f.active='Y') and "
                      "(cp.active is null or cp.active='Y') and "
                      "(tr.active is null or tr.active='Y') and "
                      "r.investorId=%s and tr.tagId=%s",
                      investor_id, tag_id
                      )
    cnt = result["cnt"]
    tongji = conn.get("select * from investor_tongji where "
                      "investorId=%s and tagId=%s and fromDate is null and toDate is null", investor_id, tag_id)
    if tongji is None:
        conn.insert("insert investor_tongji(investorId,tagId,cnt,createTime,modifyTime) values(%s,%s,%s,now(),now())",
                    investor_id, tag_id, cnt)
    else:
        conn.update("update investor_tongji set cnt=%s, modifyTime=now() where id=%s", cnt, tongji["id"])


def tongji_investor_year_funding_cnt(investor_id, year):
    logger.info("investorId: %s, year: %s", investor_id, year)
    start_date = "%s-01-01" % year
    end_date = "%s-01-01" % (year+1)

    result = conn.get("select count(*) cnt from funding_investor_rel r "
                      "join funding f on r.fundingId=f.id "
                      "join company cp on f.companyId=cp.id "
                      "where "
                      "(r.active is null or r.active='Y') and "
                      "(f.active is null or f.active='Y') and "
                      "(cp.active is null or cp.active='Y') and "
                      "r.investorId=%s and "
                      # "("
                      #          "(publishDate is not null and publishDate>=%s and publishDate<%s)"
                      #          " or "
                      #          "(publishDate is null and fundingDate>=%s and fundingDate<=%s)"
                      # ")"
                      "fundingDate>=%s and fundingDate<=%s",
                      investor_id, start_date, end_date
                      )
    cnt = result["cnt"]
    tongji = conn.get("select * from investor_tongji where "
                      "investorId=%s and tagId is null and fromDate=%s and toDate=%s", investor_id, start_date, end_date)
    if tongji is None:
        conn.insert("insert investor_tongji(investorId,fromDate,toDate,cnt,createTime,modifyTime) values(%s,%s,%s,%s,now(),now())",
                    investor_id, start_date, end_date, cnt)
    else:
        conn.update("update investor_tongji set cnt=%s, modifyTime=now() where id=%s", cnt, tongji["id"])


if __name__ == "__main__":
    INTERVAL = 10
    cnt = 0
    while True:
        if cnt >= 24*60/INTERVAL:
            cnt = 0
            tongji_all()
        else:
            tongji_incr()
            cnt += 1
        time.sleep(INTERVAL * 60)