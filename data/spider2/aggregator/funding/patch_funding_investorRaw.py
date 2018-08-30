# -*- coding: utf-8 -*-
import datetime
import os, sys
import time,json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import util
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper


#logger
loghelper.init_logger("patch_investor", stream=True)
logger = loghelper.get_logger("patch_investor")



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
                              -544,
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
            investor_id = None
            investor_company_id = None

            if sfir["investorType"] == 38001:
                source_investor = conn.get("select * from source_investor where id=%s", sfir["sourceInvestorId"])
                if source_investor is None:
                    flag = False
                    continue
                investor_id = source_investor["investorId"]
                if investor_id is None:
                    # flag = False
                    if len(STR) > 0:
                        STR.append({"text":"、","type":"text"})
                    STR.append({"text":source_investor["name"],"type":"text"})
                    continue
                else:
                    investor  = conn.get("select * from investor where id=%s", investor_id)
                    if investor is None or investor["active"] == 'N':
                        # flag = False
                        if len(STR) > 0:
                            STR.append({"text": "、", "type": "text"})
                        STR.append({"text":source_investor["name"],"type":"text"})
                        continue
                    else:
                        if len(STR) > 0:
                            STR.append({"text": "、", "type": "text"})
                        STR.append({"text": investor["name"],"type":"investor","id":int(investor_id)})

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
                        precise,active,createTime,modifyTime,createUser) \
                        values(%s,%s,%s,%s,%s,%s,%s,'Y',now(),now(),%s)"
                conn.insert(sql,
                            fundingId,
                            sfir["investorType"],
                            investor_id,
                            investor_company_id,
                            sfir["currency"],
                            sfir["investment"],
                            sfir["precise"],
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

def check_ok(company):
    ss = datetime.datetime.strptime("2017-07-01", "%Y-%m-%d")
    status = False
    conn = db.connect_torndb()
    fundings_all = conn.query("select * from funding where companyId=%s and (active is null or active='Y')",
                              company["id"])

    sfs = conn.query("select id from source_company where (active is null or active='Y') and companyId=%s",
                     company["id"])
    if len(fundings_all) == 0 and (len(sfs) == 1 or (company["modifyUser"] is not None and company["modifyTime"]>=ss)):
        status = True

    conn.close()
    return status


if __name__ == '__main__':
    logger.info("Begin...")
    logger.info("funding investor repatch start ")
    conn = db.connect_torndb()
    (n1, n2, n3, n4, n5, n6, n7) = (0, 0, 0, 0, 0, 0, 0)
    fs = conn.query("select * from funding  where (active is null or active='Y') and investors is not null")
    for f in fs:
        n1 += 1
        # logger.info(f["investors"])
        investors = eval(f["investors"].replace("null","\"abcnull\""))
        for investor in investors:
            if investor["type"] == "text":

                if investor["text"] in ["、",",","，",", ","-"]: continue

                invest = investor["text"].replace("、",",").replace(",",",").replace("，",",").replace(", ",",").replace("-",",")
                invs = invest.split(",")
                for inv in invs:
                    n2 += 1
                    invv = inv.replace("领投","").replace("中国","").replace("跟投","").replace("参投","").replace("和","")
                    if invv.strip() == "":continue
                    # logger.info(f["investors"])
                    # logger.info(invv)
                    investora = conn.get("select i.id, i.name from investor_alias ia join investor i on "
                                         "ia.investorId=i.id where ia.name=%s and "
                                         "(i.active is null or i.active='Y') and "
                                         "(ia.active is null or ia.active='Y') limit 1", invv)
                    if investora is None:
                        continue
                    else:
                        n3 += 1
                        logger.info("%s-%s-%s-%s", invv, investora["id"], f["id"], f["investorsRaw"])

    logger.info("funding aggregator end.")
    logger.info("%s/%s/%s/%s/%s/%s", n1, n2, n3, n4, n5, n6)

    conn.close()
    logger.info("End.")