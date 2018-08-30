# -*- coding: utf-8 -*-
import datetime
import os, sys
import time,json
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import util
import name_helper
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/company/itjuzi'))
import parser_db_util
import itjuzi_helper

# corporateId not companyId
# funding createUser =-557
# if have 2 or more corporates do not do anything
#

#logger
loghelper.init_logger("patch_card", stream=True)
logger = loghelper.get_logger("patch_card")


def remove_13030_funding():
    conn = db.connect_torndb()
    fs = conn.query("select * from source_funding where sourceCompanyId in (select id from source_company where source=13030)")
    for f in fs:
        conn.execute("delete from source_frawunding_investor_rel where sourceFundingId=%s", f["id"])
        conn.execute("delete from source_funding where id=%s",f["id"])
    conn.close()

def check_investor(investorId, str_id):
    cflag = False
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_dealLog = mongo.raw.qmp_tz_parser
    item = collection_dealLog.find_one({"_id": ObjectId(str_id)})
    investors = item["tzr"]
    STR = []
    InvestorIds = []
    for invs in investors.replace(",","，").replace("、","，").split("，"):
        invraw0 = invs
        invraw = invs.strip().replace("领投", "").replace("跟投", "").replace("参投", "").replace("等", "").replace(r'\n',"").replace("\"", "")
        if invraw.find("(") >= 0 or invraw.find("（") >= 0:
            # logger.info("here")
            invraw = invraw.replace("(", "（").split("（")[0]
        investor_id = None
        investor_id_name = None

        investor = conn.get("select i.id, i.name from investor_alias ia join investor i on "
                            "ia.investorId=i.id where ia.name=%s and "
                            "(i.active is null or i.active='Y') and "
                            "(ia.active is null or ia.active='Y') limit 1", invraw)
        if investor is None:
            pass
        else:
            # logger.info(investor)
            investor_id = investor["id"]
            investor_id_name = investor["name"]
            InvestorIds.append(int(investor_id))


        if investor_id is None:
            if len(STR) > 0:
                STR.append({"text": "、", "type": "text"})
            STR.append({"text":invraw0,"type":"text"})
        else:
            if len(STR) > 0:
                STR.append({"text": "、", "type": "text"})
            STR.append({"text": invraw0,"type":"investor","id":int(investor_id)})

    if len(STR) >= 0:
        investorRaw = "".join([si['text'] for si in STR])
        logger.info(json.dumps(STR, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(investorRaw)

    if int(investorId) in InvestorIds:
        cflag = True
    else:
        xinvestor = conn.get("select * from investor where id=%s", investorId)
        logger.info("*******  %s not found investor: %s|%s", investors, investorId, xinvestor["name"])

    conn.close()
    mongo.close()
    return cflag


def getMoney(moneyStr):
    investment = 0
    currency = 3020
    precise = 'Y'

    investmentStr = ""

    if investment == 0:
        result = util.re_get_result(u'(数.*?)万人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            precise = 'N'
        else:
            result = util.re_get_result(u'(数.*?)万美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                precise = 'N'

        if investmentStr != "":
            if investmentStr == u"数":
                investment = 1*10000
            elif investmentStr == u"数十":
                investment = 10*10000
            elif investmentStr == u"数百":
                investment = 100*10000
            elif investmentStr == u"数千":
                investment = 1000*10000

    if investment == 0:
        result = util.re_get_result(u'(数.*?)亿人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            precise = 'N'
        else:
            result = util.re_get_result(u'(数.*?)亿美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                precise = 'N'

        if investmentStr != "":
            if investmentStr == u"数":
                investment = 1*10000*10000
            elif investmentStr == u"数十":
                investment = 10*10000*10000
            elif investmentStr == u"数百":
                investment = 100*10000*10000
            elif investmentStr == u"数千":
                investment = 1000*10000*10000

    if investment == 0:
        result = util.re_get_result(u'(\d*\.?\d*?)万人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            investment = int(float(investmentStr) * 10000)
        else:
            result = util.re_get_result(u'(\d*\.?\d*?)万美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                investment = int(float(investmentStr) * 10000)

    if investment == 0:
        result = util.re_get_result(u'(\d*\.?\d*?)亿人民币',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            investment = int(float(investmentStr) * 100000000)
        else:
            result = util.re_get_result(u'(\d*\.?\d*?)亿美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                investment = int(float(investmentStr) * 100000000)

    if investment == 0:
        result = util.re_get_result(u'亿元及以上美元',moneyStr)
        if result != None:
            currency = 3020
            investment = 100000000
            precise = 'N'
        else:
            result = util.re_get_result(u'亿元及以上人民币',moneyStr)
            if result != None:
                currency = 3010
                investment = 100000000
                precise = 'N'

    return currency, investment, precise


def parseFinance(item):
    logger.info("parseFinance")
    if item is None:
        return None

    # logger.info("%s,%s,%s,%s" % (item.get("lunci"),item.get("money"),item["tzdate"],item.get("tzr")))

    roundStr = item.get("lunci")
    fundingRound = 0
    if roundStr.startswith("尚未获投"):
        fundingRound = 1000
        roundStr = "尚未获投"
    elif roundStr.startswith("种子"):
        fundingRound = 1010
        roundStr = "天使轮"
    elif roundStr.startswith("天使"):
        fundingRound = 1011
        roundStr = "天使轮"
    elif roundStr.startswith("Pre-A"):
        fundingRound = 1020
        roundStr = "Pre-A轮"
    elif roundStr.startswith("A+"):
        fundingRound = 1031
        roundStr = "A+轮"
    elif roundStr.startswith("A"):
        fundingRound = 1030
        roundStr = "A轮"
    elif roundStr.startswith("Pre-B"):
        fundingRound = 1039
        roundStr = "Pre-B轮"
    elif roundStr.startswith("B+"):
        fundingRound = 1041
        roundStr = "B+轮"
    elif roundStr.startswith("B"):
        fundingRound = 1040
        roundStr = "B轮"
    elif roundStr.startswith("C+"):
        fundingRound = 1051
        roundStr = "C轮"
    elif roundStr.startswith("C"):
        fundingRound = 1050
        roundStr = "C轮"
    elif roundStr.startswith("D"):
        fundingRound = 1060
        roundStr = "D轮"
    elif roundStr.startswith("E"):
        fundingRound = 1070
        roundStr = "E轮"
    elif roundStr.startswith("F"):
        fundingRound = 1080
        roundStr = "F轮"
    elif roundStr.startswith("Pre-IPO"):
        fundingRound = 1080
        roundStr = "Pre-IPO"
    elif roundStr.startswith("新三板"):
        fundingRound = 1105
        roundStr = "新三板"
    elif roundStr.startswith("定向增发"):
        fundingRound = 1106
        roundStr = "新三板定增"
    elif (roundStr.startswith("IPO") or roundStr.startswith("已上市")) and roundStr.find("IPO上市后") == -1:
        fundingRound = 1110
        roundStr = "上市"
    elif roundStr.startswith("已被收购") or roundStr.startswith("并购"):
        fundingRound = 1120
        roundStr = "并购"
    elif roundStr.startswith("战略投资") or roundStr.startswith("战略融资") or roundStr.startswith("IPO上市后"):
        fundingRound = 1130
        roundStr = "战略投资"
    elif roundStr.startswith("私有化"):
        fundingRound = 1140
        roundStr = "私有化"
    elif roundStr.startswith("债权融资"):
        fundingRound = 1150
        roundStr = "债权融资"
    elif roundStr.startswith("股权转让"):
        fundingRound = 1160
        roundStr = "股权转让"


    try:
        fundingDate = datetime.datetime.strptime(item["tzdate"], "%Y.%m.%d")
    except:
        fundingDate = None
    (currency, investment, precise) = getMoney(item.get("money"))
    source_funding = {
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

    # logger.info(json.dumps(source_funding, ensure_ascii=False, cls=util.CJsonEncoder))
    logger.info("org:  %s,%s,%s,%s" % (item.get("lunci"), item.get("money"), item["tzdate"], item.get("tzr")))
    logger.info("parser: %s, %s, %s, %s", round, investment, fundingDate, item.get("tzr"))


    return source_funding

def aggregate2(str_id, company_id, corporate_id, sinvestorId, test=False):
    if check_investor(int(sinvestorId), str_id) is False:
        logger.info("nnnno investor")
        return
    table_names = helper.get_table_names(test)

    mongo = db.connect_mongo()
    conn = db.connect_torndb()
    collection_dealLog = mongo.raw.qmp_tz_parser
    item = collection_dealLog.find_one({"_id": ObjectId(str_id)})

    sf = parseFinance(item)

    f = conn.get("select * from " + table_names["funding"] + " where corporateId=%s and round=%s and (active is null or active!='N') limit 1",
                 corporate_id, sf["round"])
    if f is not None:
        logger.info("corporate has this round already")

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
                              -557,
                              corporate_id
                              )

    else:
        fundingId = f["id"]

    if f:
        pass
    else:
        investors = item["tzr"]
        STR = []
        InvestorIds = []
        if check_investor(int(sinvestorId), str_id) is False:
            pass
        else:
            for invs in investors.replace(",","，").replace("、","，").split("，"):
                invraw0 = invs
                invraw = invs.strip().replace("领投", "").replace("跟投", "").replace("参投", "").replace("等", "").replace(r'\n',"").replace("\"", "")
                if invraw.find("(") >= 0 or invraw.find("（") >= 0:
                    # logger.info("here")
                    invraw = invraw.replace("(","（").split("（")[0]
                investor_id = None
                investor_id_name = None

                investor = conn.get("select i.id, i.name from investor_alias ia join investor i on "
                                    "ia.investorId=i.id where ia.name=%s and "
                                    "(i.active is null or i.active='Y') and "
                                    "(ia.active is null or ia.active='Y') limit 1", invraw)
                if investor is None:
                    pass
                else:
                    # logger.info(investor)
                    investor_id = investor["id"]
                    investor_id_name = investor["name"]
                    InvestorIds.append(int(investor_id))

                if investor_id is None:
                    if len(STR) > 0:
                        STR.append({"text": "、", "type": "text"})
                    STR.append({"text": invraw0, "type": "text"})
                else:
                    if len(STR) > 0:
                        STR.append({"text": "、", "type": "text"})
                    STR.append({"text": invraw0, "type": "investor", "id": int(investor_id)})
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


            if len(STR) > 0:
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
            funding = conn.get("select * from funding where corporateId=%s order by round desc, fundingDate desc limit 1",
                               corporate_id)
            if funding is not None:
                conn.update("update company set round=%s, roundDesc=%s where id=%s",
                            funding["round"],funding["roundDesc"],company_id)

    conn.close()

def check_investorname():
    fp = open("card.txt")
    fp2 = open("company_sh.txt", "w")
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_dealLog = mongo.raw.qmp_tz_parser
    # item = collection_dealLog.find_one({"_id": ObjectId(str_id)})
    # investors = item["tzr"]
    investorNames = []
    InvestorIds = []
    lines = fp.readlines()
    for line in lines:
        STR = []
        for invs in line.strip().replace(",","，").replace("、","，").split("，"):
            invraw0 = invs
            invraw = invs.strip().replace("领投","").replace("跟投","").replace("参投","").replace("等","").replace(r'\n',"").replace("\"","")
            logger.info(invraw)
            if invraw.find("(") >= 0 or invraw.find("（") >= 0:
                logger.info("here")
                invraw = invraw.replace("(","（").split("（")[0]
            investor_id = None
            investor_id_name = None

            investor = conn.get("select i.id, i.name from investor_alias ia join investor i on "
                                "ia.investorId=i.id where ia.name=%s and "
                                "(i.active is null or i.active='Y') and "
                                "(ia.active is null or ia.active='Y') limit 1", invraw)
            if investor is None:
                logger.info("*******do not find: %s", invraw)
                if invraw not in investorNames:
                    investorNames.append(invraw)
                pass
            else:
                # logger.info(investor)
                investor_id = investor["id"]
                investor_id_name = investor["name"]
                InvestorIds.append(int(investor_id))


            if investor_id is None:
                if len(STR) > 0:
                    STR.append({"text": "、", "type": "text"})
                STR.append({"text":invraw0,"type":"text"})
            else:
                if len(STR) > 0:
                    STR.append({"text": "、", "type": "text"})
                STR.append({"text": invraw0,"type":"investor","id":int(investor_id)})

        if len(STR) >= 0:
            investorRaw = "".join([si['text'] for si in STR])
            logger.info(json.dumps(STR, ensure_ascii=False, cls=util.CJsonEncoder))
            logger.info(investorRaw)
        # break
        # if int(investorId) in InvestorIds:
        #     pass
        # else:
        #     xinvestor = conn.get("select * from investor where id=%s", investorId)
        #     logger.info("*******  %s not found investor: %s|%s", investors, investorId, xinvestor["name"])
    logger.info("total : %s", len(investorNames))
    logger.info(json.dumps(investorNames, ensure_ascii=False, cls=util.CJsonEncoder))
    for n in investorNames:
        fp2.write(n)
        fp2.write("\n")
    conn.close()
    mongo.close()
    fp.close()
    fp2.close()



if __name__ == '__main__':
    logger.info("Begin...")
    logger.info("funding card start ")
    # check_investor(114, "5b45a8f7deb47174c8a818e0")
    check_investorname()
    logger.info("End.")