# -*- coding: utf-8 -*-
import os, sys,json,time
import datetime
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../corporate'))
import loghelper, db, config, util,url_helper,name_helper,download
import find_company

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/company/itjuzi'))
import parser_db_util
import itjuzi_helper


# kafka
kafkaProducer = None
download_crawler = download.DownloadCrawler(use_proxy=False)


def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)

def send_message(company_id, action):
    if kafkaProducer is None:
        init_kafka()

    #action: create, delete
    msg = {"type":"company", "id":company_id , "action":action}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)

def send_message_task(company_id, action, source):
    if kafkaProducer is None:
        init_kafka()

    # action: create, delete
    msg = {"source": action, "id": company_id, "detail": source}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("task_company", json.dumps(msg))
            flag = True
        except Exception, e:
            logger.exception(e)
            time.sleep(60)


#logger
loghelper.init_logger("sh_import", stream=True)
logger = loghelper.get_logger("sh_import")


def insert(shortname, name,brief,fullNames):
    name = name.replace("（开业）","")
    sourceId = util.md5str(name)
    sid = parser_db_util.save_company_yitai(shortname, name,13100,sourceId,brief)
    # logger.info("sid:%s->sourceId:%s",sid, sourceId)
    parser_db_util.save_source_company_name(sid, shortname, 12020)
    for fullName in [name] + fullNames:
        parser_db_util.save_source_company_name(sid, fullName, 12010)

    return sid

def insert_funding(sid,roundstr,inv,fundingDate,investor):
    try:
        inv = "".join(inv.split())
        if inv in ["超千万人民币","千万人民币", "近千万人民币","过千万人民币","上千万人民币","1千万人民币"]:
            inv = "1000万人民币"
        elif inv in ["超亿人民币", "近亿人民币","过亿人民币","上亿人民币", "亿人民币", "一亿人民币","亿人民币及以上人民币"]:
            inv = "1亿人民币"
        elif inv in ["超千万美元","千万美元", "近千万美元","过千万美元","上千万美元","1千万美元"]:
            inv = "1000万美元"
        elif inv in ["百万美元", "近百万美元","过百万美元","上百万美元", "1百万美元"]:
            inv = "100万美元"
        elif inv in ["百万人民币", "近百万人民币","过百万人民币","上百万人民币","1百万人民币"]:
            inv = "100万人民币"

        if roundstr == "re-A轮":
            roundstr = "Pre-A"
        elif roundstr == "re-IPO":
            roundstr = "Pre-IPO"
        fundingRound, roundStr = itjuzi_helper.getFundingRound(unicode(roundstr))
        currency, investment, precise = itjuzi_helper.getMoney(unicode(inv))

        source_funding = {
            "sourceCompanyId": sid,
            "preMoney": None,
            "postMoney": None,
            "investment": investment,
            "precise": precise,
            "round": fundingRound,
            "roundDesc": roundStr,
            "currency": currency,
            "fundingDate": fundingDate,
            "newsUrl": None
        }
        source_investors = []
        source_investor = {
            "name": investor,
            "website": None,
            "description": None,
            "logo_url": None,
            "stage": None,
            "field": None,
            "type": 10020,
            "source": 13100,
            "sourceId": util.md5str(investor)
        }
        source_investors.append(source_investor)

        parser_db_util.save_funding_standard(source_funding, download_crawler, source_investors)
        # logger.info("%s/%s-------%s/%s/%s/%s", roundstr, inv, fundingRound, investment,precise,currency)
    except:
        logger.info("%s/%s/%s/%s", roundstr, inv, fdate, investor)
        # exit()
    pass


def findc(aname):
    rvalue = 0
    conn = db.connect_torndb()
    aname = aname.replace("（开业）","")
    sourceId = util.md5str(aname)
    sc = conn.get("select * from source_company where source=13100 and sourceId=%s", sourceId)
    if sc is None:
        logger.info("wrong")
        exit()
    companyId = sc["companyId"]
    company =  conn.get("select * from company where id=%s", companyId)
    scs = conn.query("select * from source_company where companyId=%s", companyId)
    # if len(scs) == 1 and scs[0]["source"] == 13096 and company is not None:
    if company is not None and company["active"] in ["A","P","N"]:
        # conn.update("update company set brief=%s,locationId=2 where id=%s", brief, companyId)
        # conn.update("update corporate set brief=%s,locationId=2 where id=%s", brief, company["corporateId"])

        # if company["active"] == "A":
            rvalue = 1
            # conn.update("update company set brief=%s,locationId=2 where id=%s", brief,companyId)
            # conn.update("update corporate set brief=%s,locationId=2 where id=%s", brief, company["corporateId"])


    conn.close()
    return rvalue,companyId



if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    fp = open("yitai2.txt")
    fp2 = open("company_sh.txt", "w")
    # conn = db.connect_torndb()
    lines = fp.readlines()
    # lines = []
    cnt = 0
    tot = 0
    pb = 0
    for line in lines:
        # logger.info(line)
        names = [name.strip() for name in line.strip().split("+++")]
        tot +=1
        if len(names) != 10:
            logger.info(line)
            logger.info("er1")
            exit()
        # tot += 1
        shortname = names[1]
        fullName = names[2]
        if fullName is None or fullName.strip() == "":
            fullName = names[3]
        if fullName is None or fullName.strip() == "":
            logger.info(line)
            # logger.info("er1")
            continue
            # exit()
        # fullNames = [name_helper.company_name_normalize(unicode(name[2])), name_helper.company_name_normalize(unicode(name[3]))]
        fullNames = []
        for fn in [names[2],names[3]]:
            if fn is not None and fn.strip() != "":
                fullNames.append(name_helper.company_name_normalize(unicode(fn)))
        fullName = name_helper.company_name_normalize(unicode(fullName))

        roundstr = names[4]
        inv = names[5]
        fdate = names[6]
        investor = names[7]
        if investor is not None:
            investor = investor.split("/")[0]
        if investor is None or investor.strip() == "":
            if names[8] is not None:
                investor = names[8].split("/")[0]

        if investor is None:
            logger.info(line)
            logger.info("er2")
            exit()
            continue

        try:
            fundingDate =datetime.datetime.strptime(fdate, "%Y-%m-%d")
        except:
            logger.info(line)
            logger.info("er3")
            continue
        # logger.info("%s/%s/%s/%s",roundstr,inv,fdate,investor)
        # # if len(brief) < 100:
        # #     logger.info(brief)
        # # if len(brief) == 0:
        # #     brief = None
        # #     logger.info("none")
        # # if website is not None and website.strip() != "":
        # #     logger.info(website)
        #
        # logger.info("name:%s, fullName:%s", shortname, fullName)
        # company_ids = find_company.find_companies_by_full_name_corporate(fullNames)
        # #
        # if len(company_ids) != 0:
        #     logger.info("found : %s, %s", fullName, company_ids)
        #     cnt += 1
        # sid = insert(shortname,fullName,None,fullNames)
        # insert_funding(sid, roundstr,inv,fundingDate,investor)
        # # cnt += 1
        # exit()
        rv,cid = findc(fullName)
        if rv == 1:
            cnt+=1
            c = conn.get("select * from company where id=%s", cid)
            link = 'http://www.xiniudata.com/validator/#/company/%s/overview' % c["code"]
            send_message_task(cid, "company_newcover", 13100)
            line = "%s+++%s+++%s+++%s\n" % (c["code"], c["name"], link, c["active"])
            fp2.write(line)

        # if pb>50:
        #     break
        # # break
    conn.close()
    logger.info("%s/%s",cnt, tot)
    logger.info("End.")