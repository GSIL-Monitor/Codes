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
    logger.info("funding yitai start ")
    conn = db.connect_torndb()
    (n1, n2, n3, n4, n5, n6, n7) = (0, 0, 0, 0, 0, 0, 0)
    # cs = conn.query("select * from company where (active is null or active='Y') and id=%s order by id", 248477)
    # cs = conn.query("select * from company where (active is null or active='Y') order by id")
    cs = {}
    namesa = []
    fp = open("yitai2.txt")
    # conn = db.connect_torndb()
    lines = fp.readlines()
    # lines = []
    cnt = 0
    tot = 0
    pb = 0
    for line in lines:
        # logger.info(line)
        names = [name.strip() for name in line.strip().split("+++")]
        tot += 1
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
            # logger.info(line)
            # logger.info("er1")
            continue
            # exit()
        # fullNames = [name_helper.company_name_normalize(unicode(name[2])), name_helper.company_name_normalize(unicode(name[3]))]
        fullNames = []
        for fn in [names[2], names[3]]:
            if fn is not None and fn.strip() != "":
                fullNames.append(name_helper.company_name_normalize(unicode(fn)))
        fullName = name_helper.company_name_normalize(unicode(fullName))

        roundstr = names[4]
        inv = names[5]
        fdate = names[6]
        investors = []
        if names[7] is not None and names[7].strip() != "":
            investors.extend(names[7].split("/"))
        if names[8] is not None and names[8].strip() != "":
            investors.extend(names[8].split("/"))

        if len(investors) == 0:
            continue


        fundingRound, roundStr = itjuzi_helper.getFundingRound(unicode(roundstr))

        if fullName not in namesa: namesa.append(fullName)
        if fundingRound is not None and fundingRound>0:
            if cs.has_key(fullName) is False:
                cs[fullName] = {fundingRound:[investors]}
            else:
                if cs[fullName].has_key(fundingRound) is False:
                    cs[fullName][fundingRound] = [investors]
                else:
                    cs[fullName][fundingRound].append(investors)

    # logger.info(json.dumps(cs, ensure_ascii=False, cls=util.CJsonEncoder))
    logger.info(len(cs))
    logger.info(len(namesa))

    for cc in cs:
        rv, cid = findc(cc)
        sfs = conn.query("select * from source_funding where sourceCompanyId in (select id from source_company "
                         "where (active is null or active='Y') and source=13100 and companyId=%s)", cid)
        co = conn.get("select * from company where (active is null or active!='N') and id=%s", cid)
        if len(sfs) > 0 and co is not None and co["corporateId"] is not None:
            n1 += 1
            if check_ok(cid) is True:
                n2 += 1
                logger.info("company %s|%s could add funding from yitai", cid, cc)
                logger.info(json.dumps(cs[cc], ensure_ascii=False, cls=util.CJsonEncoder))
                logger.info(cs[cc])
    #             n3 += len(sfs)
    #             flag = True
                for sf in sfs:
                    logger.info(sf)
                    if cs[cc].has_key(sf["round"]) is True:
                        logger.info("here")
                        flag = aggregate1(sf, cid, co["corporateId"], cs[cc])

                        if flag is True:
                            n5 += 1
                            logger.info("New funding added for company : %s", cc)
                            set_processed(sfs)
                            # exit()
    #             else:
    #                 logger.info("Something wrong with aggregating funding for company : %s|%s", cc["code"], cc["id"])
    #                 n4 += 1
    #                 #set_processed(sfs)
    #                 exit()
    #             pass
    #
    # logger.info("funding aggregator end.")
    logger.info("%s/%s/%s/%s/%s/%s", n1, n2, n3, n4, n5, n6)

    conn.close()
    logger.info("End.")