# -*- coding: utf-8 -*-
import os, sys
import time, datetime

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import util
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper

#logger
loghelper.init_logger("funding_aggregator", stream=True)
logger = loghelper.get_logger("funding_aggregator")


def aggregate(source_funding):
    #flag = True
    sf = source_funding
    logger.info("source_funding_id: %s" % sf["id"])
    #logger.info(sf)

    # TODO
    # 如果funding日期比公司成立日期晚一年, 跳过

    conn = db.connect_torndb()
    source_company = conn.get("select * from source_company where id=%s", sf["sourceCompanyId"])
    #logger.info(source_company)
    conn.close()

    if source_company is None:
        return False

    if source_company["companyId"] is None:
        return False

    if source_company["source"] == 13022:
        return False

    company_id = source_company["companyId"]
    logger.info("company_id: %s", company_id)

    return aggregate2(sf, source_company, company_id)

def getCurrencyName(currency):
    if currency == 3010:
        return u"美元"
    if currency == 3020:
        return u"人民币"
    if currency == 3030:
        return u"新加坡元"
    return ""

def getRoundName(round):
    if round==1010:
        return u"种子轮"
    if round==1011:
        return u"天使轮"
    if round==1020:
        return u"Pre-A轮"
    if round==1030:
        return u"A轮"
    if round==1031:
        return u"A+轮"
    if round==1039:
        return u"Pre-B轮"
    if round==1040:
        return u"B轮"
    if round==1041:
        return u"B+轮"
    if round==1050:
        return u"C轮"
    if round==1060:
        return u"D轮"
    if round==1070:
        return u"E轮"
    if round==1080:
        return u"F轮"
    if round==1090:
        return u"Late Stage"
    if round==1100:
        return u"Pre-IPO轮"
    if round==1105:
        return u"新三板"
    if round==1110:
        return u"IPO"
    if round==1120:
        return u"Acquired"
    if round==1130:
        return u"战略投资"
    return u"未知"

def get_money_str(amount, precise):
    if amount > 10000 * 10000:
        str = u"%s亿" % ((int)(amount/10000/10000))
        if amount % (10000*10000) > 0:
            str += u"%s万" % (int)((amount % (10000*10000))/10000)
    elif amount > 10000:
        str = u"%s万" % (int)(amount/10000)
    else:
        str = "%s" % amount

    if precise == "N":
        str += u"(估)"
    return str


def aggregate2(sf,source_company,company_id, test=False):
    if test:
        return True

    if sf["fundingDate"] is None:
        return True

    f = conn.get("select * from funding where companyId=%s and round=%s and (active is null or active!='N') limit 1",
                 company_id, sf["round"])

    if f is None and sf["fundingDate"] is not None and sf["round"]<=1020:
        f = conn.get("select * from funding where companyId=%s and fundingDate>date_sub(%s,interval 1 month) and fundingDate<date_add(%s,interval 1 month) and (active is null or active!='N') limit 1",
                company_id, sf["fundingDate"], sf["fundingDate"])

    if f:
        return True

    investor_names = []
    sfirs = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s", sf["id"])
    for sfir in sfirs:
        if sfir["investorType"] == 38001:
            source_investor = conn.get("select * from source_investor where id=%s", sfir["sourceInvestorId"])
            if source_investor:
                investor_name = source_investor["name"]
                investor_names.append(investor_name)
        else:
            source_company = conn.get("select * from source_company where id=%s", sfir["sourceCompanyId"])
            if source_company:
                investor_name = source_company["name"]
                investor_names.append(investor_name)

    company = conn.get("select * from company where id=%s", company_id)
    name = "%s %s获得%s%s%s融资" % (sf["fundingDate"].strftime("%Y-%m-%d"),
                                company["name"],
                                get_money_str(sf["investment"], sf["precise"]),
                                getCurrencyName(sf["currency"]),
                                getRoundName(sf["round"]))
    brief = u"融资日期: %s " % sf["fundingDate"].strftime("%Y-%m-%d")
    if len(investor_names) > 0:
        brief += "投资人: " + ", ".join(investor_names)

    data = {
        "name": name,
        "processStatus": 0,
        "items": [{
            "sort": 1,
            "currency":getCurrencyName(sf["currency"]),
            "amount":get_money_str(sf["investment"], sf["precise"]),
            "brief": brief,
            "round":getRoundName(sf["round"])
        }],
        "company": [int(company_id)],
        "news_date": sf["createTime"],
        "news_id": [],
        "createTime": datetime.datetime.now() - datetime.timedelta(hours=8)
    }
    # investment =0 and older funding set as -2
    if sf["investment"] is not None and sf["investment"]==0 and \
        sf["fundingDate"] is not None and (datetime.datetime.now()-sf["fundingDate"]).days>90:
        logger.info("source funding %s|%s ->%s will be set as -2", sf["id"], sf["fundingDate"],name)
        data["processStatus"] = -2

    #print data
    mongo = db.connect_mongo()
    mongo.raw.funding.insert(data)
    mongo.close()
    return True

def aggregate1(sf,source_company,company_id, test=False):
    return False

    flag = True

    table_names = helper.get_table_names(test)

    conn = db.connect_torndb()
    sfirs = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s", sf["id"])
    if sf["investment"] == 0 and len(sfirs)==0:
        conn.close()
        return True

    f = conn.get("select * from " + table_names["funding"] + " where companyId=%s and round=%s and (active is null or active!='N') limit 1",
                 company_id, sf["round"])

    if f is None and sf["fundingDate"] is not None and sf["round"]<=1020:
        '''
        f = conn.get("select * from " + table_names["funding"] + " where companyId=%s and year(fundingDate)=%s and month(fundingDate)=%s and (active is null or active!='N') limit 1",
                 company_id, sf["fundingDate"].year, sf["fundingDate"].month)
        '''
        f = conn.get("select * from funding where companyId=%s and fundingDate>date_sub(%s,interval 1 month) and fundingDate<date_add(%s,interval 1 month) and (active is null or active!='N') limit 1",
                company_id, sf["fundingDate"], sf["fundingDate"])

    if f is None:
        sql = "insert " + table_names["funding"] + "(companyId,preMoney,postMoney,investment,\
                    round,roundDesc,currency,precise,fundingDate,fundingType,\
                    active,createTime,modifyTime) \
                values(%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,'Y',now(),now())"
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
                              8030
                              )
    else:
        fundingId = f["id"]
        if f["round"] == 1110 and sf["round"] == 1105:
            conn.update("update " + table_names["funding"] + " set round=1105 where id=%s",fundingId)

    if f and f["createUser"] is None:
        for sfir in sfirs:
            investor_id = None
            investor_company_id = None

            if sfir["investorType"] == 38001:
                source_investor = conn.get("select * from source_investor where id=%s", sfir["sourceInvestorId"])
                if source_investor is None:
                    flag = False
                    continue
                investor_id = source_investor["investorId"]
                if investor_id is None:
                    flag = False
                    continue
                investor  = conn.get("select * from investor where id=%s", investor_id)
                if investor is None or investor["active"] == 'N':
                    flag = False
                    continue
            else:
                source_company = conn.get("select * from source_company where id=%s", sfir["sourceCompanyId"])
                if source_company is None or source_company["companyId"] is None:
                    flag = False
                    continue
                investor_company_id = source_company["companyId"]

            if sfir["investorType"] == 38001:
                funding_investor_rel = conn.get("select * from " + table_names["funding_investor_rel"] + " \
                                where investorId=%s and fundingId=%s limit 1",
                                investor_id, fundingId)
            else:
                funding_investor_rel = conn.get("select * from " + table_names["funding_investor_rel"] + " \
                                where companyId=%s and fundingId=%s limit 1",
                                investor_company_id, fundingId)

            if funding_investor_rel is None:
                sql = "insert " + table_names["funding_investor_rel"] + "(fundingId, investorType, investorId, companyId, currency, investment,\
                        precise,active,createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s,%s,%s,'Y',now(),now())"
                conn.insert(sql,
                            fundingId,
                            sfir["investorType"],
                            investor_id,
                            investor_company_id,
                            sfir["currency"],
                            sfir["investment"],
                            sfir["precise"]
                        )

    # update company stage
    if not test:
        funding = conn.get("select * from funding where companyId=%s order by round desc, fundingDate desc limit 1",
                           company_id)
        if funding is not None:
            conn.update("update company set round=%s, roundDesc=%s where id=%s",
                        funding["round"],funding["roundDesc"],company_id)

    conn.close()

    return flag


if __name__ == '__main__':
    while True:
        logger.info("funding aggregator start")
        conn = db.connect_torndb()
        source_fundings = conn.query("select * from source_funding where processStatus=0 order by id")
        conn.close()

        for source_funding in source_fundings:
            flag = aggregate(source_funding)
            if flag:
                conn = db.connect_torndb()
                conn.update("update source_funding set processStatus=2 where id=%s", source_funding["id"])
                conn.close()
                pass

        logger.info("funding aggregator end.")
        time.sleep(30*60)