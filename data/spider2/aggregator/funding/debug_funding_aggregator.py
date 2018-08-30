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

    company_id = source_company["companyId"]
    logger.info("company_id: %s", company_id)

    return aggregate1(sf, source_company, company_id)


def aggregate1(sf,source_company,company_id, test=False):
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

    logger.info("fundingId: %s", fundingId)

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
    #2671 investor聚合错误的处理
    logger.info("funding aggregator start")
    conn = db.connect_torndb()
    source_fundings = conn.query("select * from source_funding where processStatus=-1 order by id")
    conn.close()

    for source_funding in source_fundings:
        flag = aggregate(source_funding)
        if flag:
            conn = db.connect_torndb()
            conn.update("update source_funding set processStatus=2 where id=%s", source_funding["id"])
            conn.close()
            pass

    logger.info("funding aggregator end.")