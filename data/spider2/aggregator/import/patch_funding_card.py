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
import name_helper
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/company/itjuzi'))
import parser_db_util
import itjuzi_helper

#logger
loghelper.init_logger("patch_36kr", stream=True)
logger = loghelper.get_logger("patch_36kr")


def remove_13030_funding():
    conn = db.connect_torndb()
    fs = conn.query("select * from source_funding where sourceCompanyId in (select id from source_company where source=13030)")
    for f in fs:
        conn.execute("delete from source_funding_investor_rel where sourceFundingId=%s", f["id"])
        conn.execute("delete from source_funding where id=%s",f["id"])
    conn.close()

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


def set_processed(source_fundings):
    conn = db.connect_torndb()
    for s_f in source_fundings:
        conn.update("update source_funding set processStatus=2 where id=%s", s_f["id"])
    conn.close()

def aggregate1(sf,company_id, corporate_id, sfi, test=False):
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
        if sfi.has_key(sf["round"]) is True:
            for invs in sfi[sf["round"]]:
                invraw = invs[0]
                investor_id = None
                investor_id_name = None
                for invname in invs:

                    investor = conn.get("select i.id, i.name from investor_alias ia join investor i on "
                                        "ia.investorId=i.id where ia.name=%s and "
                                        "(i.active is null or i.active='Y') and "
                                        "(ia.active is null or ia.active='Y') limit 1", invname)
                    if investor is None:
                        continue
                    else:
                        logger.info(investor)
                        investor_id = investor["id"]
                        investor_id_name = investor["name"]
                        break

                if investor_id is None:
                    if len(STR) > 0:
                        STR.append({"text": "、", "type": "text"})
                    STR.append({"text":invraw,"type":"text"})
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

def check_ok(companyId):
    ss = datetime.datetime.strptime("2017-07-01", "%Y-%m-%d")
    status = False
    conn = db.connect_torndb()
    company = conn.get("select * from company where (active is null or active!='N') and id=%s",companyId)
    if company is not None and company["corporateId"] is not None:
        fundings_all = conn.query("select * from funding where corporateId=%s and (active is null or active='Y')",
                                  company["corporateId"])

        # sfs = conn.query("select id from source_company where (active is null or active='Y') and companyId=%s",
        #                  companyId)
        # if len(fundings_all) == 0 and (len(sfs) == 1 or (company["modifyUser"] is not None and company["modifyTime"]>=ss)):
        if len(fundings_all) == 0:
            status = True

    conn.close()
    return status


if __name__ == '__main__':
    logger.info("Begin...")
    logger.info("funding card start ")
    fp2 = open("company_sh.txt", "w")
    conn = db.connect_torndb()
    sinvestors = conn.query("select * from source_investor where source=13120 and id=37659")
    (n1, n2, n3) = (0, 0, 0)
    for si in sinvestors:
        n3 += 1
        name = si["name"]
        name = name.replace("（", "、").replace("领投","").replace("跟投","").replace("合投","").split("、")[0]
        logger.info("name: %s00000", name)
        sfs = conn.query("select * from source_funding_investor_rel where sourceInvestorId=%s", si["id"])
        investor = conn.get("select i.id, i.name from investor_alias ia join investor i on "
                            "ia.investorId=i.id where ia.name=%s and "
                            "(i.active is null or i.active='Y') and "
                            "(ia.active is null or ia.active='Y') limit 1", name)
        if investor is None:
            ivid = "未找到"
            n1 += 1
        else:
            ivid = investor["id"]
            n2 += 1

        line = "%s+++%s+++%s\n" % (si["name"], len(sfs), ivid)
        logger.info(line)
        fp2.write(line)

    # logger.info("funding aggregator end.")
    logger.info("%s/%s/%s/", n1, n2, n3)

    conn.close()
    logger.info("End.")