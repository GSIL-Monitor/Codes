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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper

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


def insert(shortname,brief):
    sourceId = util.md5str(unicode(shortname))
    sid = parser_db_util.save_company_yitai(shortname, None,13120,sourceId,brief)
    logger.info("sid:%s->sourceId:%s",sid, sourceId)
    parser_db_util.save_source_company_name(sid, shortname, 12020)
    # for fullName in [name] + fullNames:
    #     parser_db_util.save_source_company_name(sid, fullName, 12010)

    return sid

def aggregate1(sf,company_id, corporate_id, test=False):
    flag = True

    table_names = helper.get_table_names(test)

    conn = db.connect_torndb()
    sfirs = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s", sf["id"])
    # if sf["investment"] == 0 and len(sfirs)==0:
    #     conn.close()
    #     return True

    f = conn.get("select * from " + table_names["funding"] + " where companyId=%s and round=%s and (active is null or active!='N') limit 1",
                 company_id, sf["round"])
    if f is not None:
        logger.info("find here1")
    if f is None and sf["fundingDate"] is not None and sf["round"]<=1020:
        '''
        f = conn.get("select * from " + table_names["funding"] + " where companyId=%s and year(fundingDate)=%s and month(fundingDate)=%s and (active is null or active!='N') limit 1",
                 company_id, sf["fundingDate"].year, sf["fundingDate"].month)
        '''
        f = conn.get("select * from funding where companyId=%s and fundingDate>date_sub(%s,interval 1 month) and fundingDate<date_add(%s,interval 1 month) and (active is null or active!='N') limit 1",
                company_id, sf["fundingDate"], sf["fundingDate"])
        if f is not None:
            logger.info("find here2")
    if f is None:
        logger.info("insert")
        sql = "insert " + table_names["funding"] + "(companyId,preMoney,postMoney,investment,\
                    round,roundDesc,currency,precise,fundingDate,fundingType,\
                    active,createTime,modifyTime,createUser,corporateId) \
                values(%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,'Y',now(),now(),%s,%s)"
        fundingId=conn.insert(sql,
                              company_id,
                              sf["preMoney"],
                              sf["postMoney"],
                              sf["investment"],
                              sf["round"],
                              sf["roundDesc"],
                              sf["currency"],
                              sf["precise"],
                              sf["fundingDate"],
                              8030,
                              -545,
                              corporate_id
                              )

    else:
        fundingId = f["id"]
        # if f["round"] == 1110 and sf["round"] == 1105:
        #     conn.update("update " + table_names["funding"] + " set round=1105 where id=%s",fundingId)

    if f and f["createUser"] is not None:
        pass
    else:
        STR = []
        for sfir in sfirs:

            source_investor = conn.get("select * from source_investor where id=%s", sfir["sourceInvestorId"])
            invname = source_investor["name"]

            investor = conn.get("select i.id, i.name from investor_alias ia join investor i on "
                                "ia.investorId=i.id where ia.name=%s and "
                                "(i.active is null or i.active='Y') and "
                                "(ia.active is null or ia.active='Y') limit 1", invname)
            if investor is None:
                investor_id = None
                investor_id_name = invname

            else:
                logger.info(investor)
                investor_id = investor["id"]
                investor_id_name = investor["name"]

            if investor_id is None:
                if len(STR) > 0:
                    STR.append({"text": "、", "type": "text"})
                STR.append({"text":invname,"type":"text"})
                continue
            else:
                if len(STR) > 0:
                    STR.append({"text": "、", "type": "text"})
                STR.append({"text": investor_id_name,"type":"investor","id":int(investor_id)})


            funding_investor_rel = conn.get("select * from " + table_names["funding_investor_rel"] + " \
                            where investorId=%s and fundingId=%s limit 1",
                            investor_id, fundingId)

            if funding_investor_rel is None:
                sql = "insert " + table_names["funding_investor_rel"] + "(fundingId, investorType, investorId, companyId, currency, investment,\
                        precise,active,createTime,modifyTime,createUser) \
                        values(%s,%s,%s,%s,%s,%s,%s,'Y',now(),now(),%s)"
                conn.insert(sql,
                            fundingId,
                            38001,
                            investor_id,
                            None,
                            None,
                            None,
                            None,
                            -2
                        )

        if len(STR) >= 0:
            investorRaw = "".join([si['text'] for si in STR])
            logger.info("update raw-investors %s",json.dumps(STR, ensure_ascii=False, cls=util.CJsonEncoder))
            if len(STR) > 0:
                conn.update("update funding set investors=%s, investorsRaw=%s where id=%s",
                            json.dumps(STR, ensure_ascii=False, cls=util.CJsonEncoder), investorRaw, fundingId)
            else:
                conn.update("update funding set investors=%s, investorsRaw=%s where id=%s",
                            "", investorRaw, fundingId)
    # update company stage
    if not test:
        funding = conn.get("select * from funding where companyId=%s order by round desc, fundingDate desc limit 1",
                           company_id)
        if funding is not None:
            conn.update("update company set round=%s, roundDesc=%s where id=%s",
                        funding["round"],funding["roundDesc"],company_id)

    conn.close()

    return flag

def compare_select(source_funding, compare_fundings):
    flag = False

    # if len(update_deleteIds)>0: logger.info("Update deleteids: %s",update_deleteIds)
    for cfund in compare_fundings:

        if source_funding["fundingDate"] is not None and source_funding["investment"] is not None:
            column = "fundingDate"
            column2 = "investment"
            if cfund[column] is not None and \
                    (cfund[column]-source_funding[column]).days > -20 and \
                    (cfund[column]-source_funding[column]).days< 20 and \
                    cfund[column2] is not None and cfund[column2] == source_funding[column2]:
                flag = True
                logger.info("Company %s has Funding Date Same for %s/%s/%s/%s and %s/%s/%s/%s", cfund["companyId"],
                            source_funding["id"],source_funding["fundingDate"],
                            source_funding["investment"],source_funding["round"],
                            cfund["id"],cfund["fundingDate"],cfund["investment"],cfund["round"])

        elif source_funding["fundingDate"] is not None:
            column = "fundingDate"
            if cfund[column] is not None and \
                    (cfund[column] - source_funding[column]).days > -20 and \
                    (cfund[column] - source_funding[column]).days < 20 :
                flag = True
                logger.info("Company %s has Funding Date Same for %s/%s/%s/%s and %s/%s/%s/%s", cfund["companyId"],
                            source_funding["id"], source_funding["fundingDate"],
                            source_funding["investment"], source_funding["round"],
                            cfund["id"], cfund["fundingDate"], cfund["investment"], cfund["round"])
        elif source_funding["investment"] is not None:
            column2 = "investment"
            if cfund[column2] is not None and cfund[column2]> 0 and cfund[column2] == source_funding[column2]:
                flag = True
                logger.info("Company %s has Funding Date Same for %s/%s/%s/%s and %s/%s/%s/%s", cfund["companyId"],
                            source_funding["id"], source_funding["fundingDate"],
                            source_funding["investment"], source_funding["round"],
                            cfund["id"], cfund["fundingDate"], cfund["investment"], cfund["round"])


        if flag is True:
            break

    return flag


if __name__ == '__main__':
    logger.info("Begin...")
    (num0,num1,num2,num3,num4,num5,num6) = (0, 0, 0, 0, 0, 0, 0)
    conn = db.connect_torndb()
    sourceCompanies =  conn.query("select * from source_company where source=13121")
    for sc in sourceCompanies:
        num0 += 1

        sourceFundings = conn.query("select * from source_funding where sourceCompanyId=%s", sc["id"])
        if len(sourceFundings) == 0: continue

        num1 += 1

        companyId =  sc["companyId"]
        scs = conn.query("select * from source_company where companyId=%s and (active is null or active!='N')", companyId)

        company = conn.get("select * from company where id=%s", companyId)
        fundings = conn.query("select * from funding where corporateId=%s", company["corporateId"])


        if len(scs) == 1 and scs[0]["source"] == 13121:
            num2 += 1
            checkflag = True
            for sfunding in sourceFundings:
                if compare_select(sfunding, fundings) is False:
                    checkflag = False
                    break

            if checkflag is True:
                logger.info("funding added before for company: %s|%s", company["name"], company["code"])
                continue
            logger.info("company: %s|%s", company["name"], company["code"])
            # num2 += 1
            for sf in sourceFundings:
                iflag = aggregate1(sf, company["id"], company["corporateId"])
            # exit()
        else:

            if len(fundings) == 0:
                num3 += 1
                checkflag = True
                for sfunding in sourceFundings:
                    if compare_select(sfunding, fundings) is False:
                        checkflag = False
                        break

                if checkflag is True:
                    logger.info("funding added before for company: %s|%s", company["name"], company["code"])
                    continue
                logger.info("company: %s|%s", company["name"], company["code"])
                for sf in sourceFundings:
                    iflag = aggregate1(sf, company["id"], company["corporateId"])
                # exit()
            else:
                cuser = []
                # for f in fundings:
                #     if
                checkflag = True
                for sfunding in sourceFundings:
                    if compare_select(sfunding, fundings) is False:
                        checkflag = False
                        break

                if checkflag is True:
                    num4 += 1
                else:
                    num5 += 1



    conn.close()
    logger.info("num:%s   %s/%s/%s/%s/%s/%s", num0, num1, num2, num3, num4, num5, num6)
    logger.info("End.")