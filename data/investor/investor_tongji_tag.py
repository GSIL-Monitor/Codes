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
loghelper.init_logger("investor_tongji_tag", stream=True)
logger = loghelper.get_logger("investor_tongji_tag")

conn = None

def get_thisyear_date():
    today = datetime.datetime.now()
    thisyear = today.year
    nextyear = thisyear + 1
    start_date = "%s-01-01" % thisyear
    end_date = "%s-01-01" % nextyear
    return start_date, end_date


def tongji_investor_tag(investor_id):
    logger.info("start investorId :%s", investor_id)
    from_date, to_date = get_thisyear_date()

    results = conn.query("select t.id tagId, count(*) cnt from "
                         "funding_investor_rel r use index (investorId) "
                         "join funding f on r.fundingid=f.id and r.investorId=%s and (r.active is null or r.active='Y') "
                      "join company cp on f.companyId=cp.id "
                      "join company_tag_rel tr on tr.companyId=cp.id "
                         "join tag t on tr.tagId=  t.id "
                      "where "
                      "(f.active is null or f.active='Y') and "
                      "(cp.active is null or cp.active='Y') and "
                         "(tr.active is null or tr.active='Y') and "
                         "(t.active is null or t.active='Y') and "
                         "t.type=11012 and "
                      "("
                      "(f.publishDate is null and f.fundingDate>=%s and f.fundingDate<%s) "
                      "or "
                      "(f.publishDate is not null and f.publishDate>=%s and f.publishDate<%s)"
                      ") "
                      "group by t.id "
                      "order by cnt",
                      investor_id, from_date, to_date, from_date, to_date
                      )

    conn.execute("delete from investor_tongji_tag where investorid=%s and fromDate=%s and toDate=%s",
                 investor_id, from_date, to_date)
    for result in results:
        tagId = result["tagId"]
        cnt = result["cnt"]
        logger.info("investorId: %s, tagId: %s, cnt: %s", investor_id, tagId, cnt)
        conn.insert("insert investor_tongji_tag(investorId,tagId,fromDate,toDate,cnt,createTime,modifyTime) values"
                    "(%s,%s,%s,%s,%s,now(),now())",
                    investor_id, tagId, from_date, to_date, cnt)
    logger.info("end investorId :%s", investor_id)


def tongji_incr():
    global conn
    conn = db.connect_torndb_proxy()
    invs = conn.query("select distinct investorId from funding_investor_rel r "
                      "join funding f on r.fundingId=f.id "
                      "join company cp on f.companyId=cp.id "
                      "where (f.active is null or f.active='Y') and "
                      "(r.active is null or r.active='Y') and "
                      "(cp.active is null or cp.active='Y') and "
                      "("
                      "f.createTime>date_sub(now(),interval 1 hour) or "
                      "f.modifyTime>date_sub(now(),interval 1 hour)"
                      ")")
    for inv in invs:
        investor_id = inv["investorId"]
        tongji_investor_tag(investor_id)
    conn.close()


def tongji_all():
    global conn
    conn = db.connect_torndb_proxy()
    invs = conn.query("select * from investor where (active is null or active='Y')")
    for inv in invs:
        investor_id = inv["id"]
        tongji_investor_tag(investor_id)
    conn.close()


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