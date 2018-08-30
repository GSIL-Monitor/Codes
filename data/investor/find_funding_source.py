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
loghelper.init_logger("find_funding", stream=True)
logger = loghelper.get_logger("find_funding")


DATE = None

def save(type, companyId, companyName, investorId, sourceInvestorId, source, sourceIds, investmentflag, prior2017):
    conn = db.connect_torndb()
    insert_sql = "insert audit_investor_company(name,companyId,investorId,xiniuInvestor,itjuziInvestor,kr36Investor,gongshangInvestor" \
                 ",createTime,operateStatus) values(%s,%s,%s,%s,%s,%s,%s,now(),'N')"
    insert_sql_sub = "insert audit_investor_company_source(auditInvestorCompanyId,source,sourceId) values(%s,%s,%s)"

    (xiniuInvestor, itjuziInvestor, kr36Investor, gongshangInvestor) = ("N", "N", "N", "N")

    #type1 xiniu has company funding, cross check itjuzi/36kr to see if they have funding or not
    if type == 1:
        xiniuInvestor = 'Y'
        if source == 13022 and investmentflag is True: kr36Investor = 'Y'
        if source == 13030 and investmentflag is True: itjuziInvestor = 'Y'

    #type2 xiniu hasnot company funding, cross check itjuzi/36 to see if they have have funding or not
    if type == 2:
        if source == 13022 and investmentflag is False: kr36Investor = 'Y'
        if source == 13030 and investmentflag is False: itjuziInvestor = 'Y'

    if type == 3:
        xiniuInvestor = 'Y'
        if investmentflag is True: gongshangInvestor = 'Y'

    if type == 4:
        if investmentflag is False: gongshangInvestor = 'Y'

    if type == 2 and companyId is None:
        audit = conn.get("select * from audit_investor_company where investorId=%s and name=%s and xiniuInvestor='N' limit 1", investorId, companyName)
    else:
        audit = conn.get("select * from audit_investor_company where investorId=%s and companyId=%s limit 1", investorId, companyId)
    if audit is None:
        aic_id = conn.insert(insert_sql, companyName, companyId, investorId, xiniuInvestor, itjuziInvestor, kr36Investor, gongshangInvestor)

    else:
        aic_id = audit["id"]
        if source == 13022:
            conn.update("update audit_investor_company set xiniuInvestor=%s,kr36Investor=%s where id=%s", xiniuInvestor, kr36Investor, aic_id)
        elif source == 13030:
            conn.update("update audit_investor_company set xiniuInvestor=%s,itjuziInvestor=%s where id=%s", xiniuInvestor, itjuziInvestor, aic_id)
        elif source is None:
            conn.update("update audit_investor_company set xiniuInvestor=%s,gongshangInvestor=%s where id=%s", xiniuInvestor,gongshangInvestor, aic_id)

    #for prior2017
    if prior2017 is False:
        conn.update("update audit_investor_company set prior2017='N' where id=%s",aic_id)

    if source is not None and len(sourceIds)>0:
        for sourceId in sourceIds:
            audit_source = conn.get("select * from audit_investor_company_source where auditInvestorCompanyId=%s and source=%s and sourceId=%s limit 1",
                                    aic_id, source, sourceId)
            if audit_source is None:
                conn.insert(insert_sql_sub, aic_id, source, sourceId)

    conn.close()
    pass

def front_find(investorId, sourceInvestorIds,prior2017=False):
    conn = db.connect_torndb()

    funding_investor_rels = conn.query("select distinct fundingId from funding_investor_rel where investorId=%s and (active is null or active='Y')", investorId)
    companyIds = []
    for fir in funding_investor_rels:
        if prior2017 is False:
            funding = conn.get("select * from funding where id=%s and (active is null or active='Y')"
                               " and fundingDate >='2017-01-01'", fir["fundingId"])
        else:
            funding = conn.get("select * from funding where id=%s and (active is null or active='Y')"
                               , fir["fundingId"])
        # if fir["fundingId"] != 109428: continue
        # funding = conn.get("select * from funding where id=%s and (active is null or active='Y')", fir["fundingId"])
        if funding is not None and funding["corporateId"] is not None:
            # logger.info(funding)
            cs = conn.query("select id from company where corporateId=%s and (active is null or active='Y')", funding["corporateId"])
            for c in cs:
                # logger.info(c)
                if c["id"] not in companyIds:
                    companyIds.append(c["id"])
    logger.info(companyIds)
    logger.info("found %s companies", len(companyIds))

    for sourceInvestorId in sourceInvestorIds:
        sourceInvestor = conn.get("select * from source_investor where id=%s", sourceInvestorId)
        if sourceInvestor is not None:
            source = sourceInvestor["source"]
        else:
            continue

        for companyId in companyIds:
            company = conn.get("select * from company where id=%s and (active is null or active='Y')", companyId)
            if company is None: continue
            investmentflag = False
            source_companys = conn.query("select id,name,source,sourceId from source_company where companyId=%s and source=%s "
                                         "and (active is null or active='Y')", companyId, source)
            sourceIds = []
            for sc in source_companys:
                sourceIds.append(sc["id"])
                sc_fundings = conn.query("select * from source_funding where sourceCompanyId=%s", sc["id"])
                for scf in sc_fundings:
                    scf_rels = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s and sourceInvestorId=%s"
                                          , scf["id"], sourceInvestorId)
                    if len(scf_rels) > 0:
                        investmentflag = True
                        break
            logger.info("company: %s|%s|%s has %s funding is %s", companyId, company["code"], company["name"], source, investmentflag)
            save(1, companyId, company["name"] if company["name"] != "" else company["fullName"],
                 investorId, sourceInvestorId, source, sourceIds, investmentflag, prior2017)

    #goshang part
    investor_alias = conn.query("select * from investor_alias where investorId=%s and (active is null or active='Y')", investorId)
    if len(investor_alias) > 0:
        investorAlias =  [ia["name"] for ia in investor_alias if ia["type"]==12010]
        # investmentflag = False
        mongo = db.connect_mongo()
        collection_goshang = mongo.info.gongshang

        for companyId in companyIds:
            investmentflag = False
            company = conn.get("select * from company where id=%s and (active is null or active='Y')", companyId)
            if company is None: continue
            # company_alias = conn.query("select * from company_alias where companyId=%s and type=12010 and (active is null or active='Y')", companyId)
            corporateId = company["corporateId"]
            if corporateId is None: continue
            corporate_alias = conn.query("select * from corporate_alias where corporateId=%s "
                                         "and (active is null or active='Y')", corporateId)
            for ca in corporate_alias:
                name_gongshang =collection_goshang.find_one({"name": ca["name"]})
                if name_gongshang is None or name_gongshang.has_key("investors") is False: continue
                for investor_gongshang in name_gongshang["investors"]:
                    if investor_gongshang["name"] in investorAlias:
                        investmentflag = True
                        break
                if investmentflag is True: break
            logger.info("company: %s|%s|%s has gongshang funding is %s", companyId, company["code"],company["name"], investmentflag)
            save(3, companyId, company["name"] if company["name"] != "" else company["fullName"],
                 investorId, None, None, [], investmentflag,prior2017)

        mongo.close()

    conn.close()


def back_find(investorId, sourceInvestorIds,prior2017=False):
    conn = db.connect_torndb()
    for sourceInvestorId in sourceInvestorIds:

        sourceInvestor = conn.get("select * from source_investor where id=%s", sourceInvestorId)
        if sourceInvestor is not None:
            source = sourceInvestor["source"]
        else:
            continue
        scf_rels = conn.query("select distinct sourceFundingId from source_funding_investor_rel where sourceInvestorId=%s", sourceInvestorId)
        sourceCompanyIds = []
        for scfr in scf_rels:
            if prior2017 is False:
                source_funding = conn.get("select * from source_funding where id=%s "
                                          "and fundingDate>='2017-01-01'", scfr["sourceFundingId"])
            else:
                source_funding = conn.get("select * from source_funding where id=%s "
                                          , scfr["sourceFundingId"])
            if source_funding is not None and source_funding["sourceCompanyId"] not in sourceCompanyIds:
                sourceCompanyIds.append(source_funding["sourceCompanyId"])

        for sourceCompanyId in sourceCompanyIds:
            source_company = conn.get("select * from source_company where id=%s and (active is null or active='Y')", sourceCompanyId)
            if source_company is None: continue
            investmentflag = False


            if source_company["companyId"] is None:
                logger.info("source_company: %s|%s|%s has funding but company is missing", source_company["id"], source_company["name"],source)
                save(2,None, source_company["name"], investorId, sourceInvestorId, source, [source_company["sourceId"]], investmentflag,prior2017)
            else:
                company = conn.get("select id,name,fullName,code,corporateId from company where id=%s and "
                                   "(active is null or active='Y')", source_company["companyId"])
                if company is None:
                    logger.info("source_company: %s|%s|%s has funding but company is None", source_company["id"],source_company["name"], source)

                    save(2,None, source_company["name"], investorId, sourceInvestorId, source, [source_company["sourceId"]], investmentflag,prior2017)
                else:
                    # logger.info(company)
                    fundings = conn.query("select * from funding where corporateId=%s and "
                                          "(active is null or active='Y')", company["corporateId"])
                    for f in fundings:
                        f_rels = conn.query("select * from funding_investor_rel where fundingId=%s and investorId=%s "
                                              "and (active is null or active='Y')", f["id"], investorId)
                        if len(f_rels) > 0:
                            investmentflag = True
                            break

                    if investmentflag is False:
                        logger.info("company: %s|%s|%s has no funding from %s", company["id"], company["code"],company["name"], source)
                        save(2, company["id"], company["name"] if company["name"] != "" else company["fullName"],
                             investorId, sourceInvestorId, source, [source_company["sourceId"]], investmentflag,prior2017)

    # goshang part
    investor_alias = conn.query("select * from investor_alias where investorId=%s and (active is null or active='Y')", investorId)
    if len(investor_alias) > 0:
        investorAlias = [ia["name"] for ia in investor_alias if ia["type"] == 12010]
        # investmentflag = False
        mongo = db.connect_mongo()
        collection_goshang = mongo.info.gongshang

        for ia in investorAlias:
            ia_gongshang = collection_goshang.find_one({"name": ia})
            if ia_gongshang is None or ia_gongshang.has_key("invests") is False: continue

            for invest in ia_gongshang["invests"]:
                company_name = invest["name"]
                # icompanys = conn.query("select distinct companyId from company_alias where name=%s and (active is null or active='Y')", company_name)
                icorporates = conn.query("select distinct corporateId from corporate_alias where name=%s and (active is null or active='Y')", company_name)

                for icorporate in icorporates:
                    icompanys = conn.query("select id from company where corporateId=%s and (active is null or active='Y')",icorporate["corporateId"])

                    for icompany in icompanys:
                        investmentflag = False
                        company = conn.get("select id,name,fullName,code from company where id=%s and (active is null or active='Y')", icompany["id"])
                        if company is None:
                            continue
                        else:

                            fundings = conn.query("select * from funding where corporateId=%s and (active is null or active='Y')", icorporate["corporateId"])
                            for f in fundings:
                                f_rels = conn.query("select * from funding_investor_rel where fundingId=%s and investorId=%s "
                                                    "and (active is null or active='Y')", f["id"], investorId)
                                if len(f_rels) > 0:
                                    investmentflag = True
                                    break

                            if investmentflag is False:
                                logger.info("company: %s|%s|%s has gongshang funding is %s", company["id"], company["code"],company["name"], investmentflag)
                                save(4, company["id"], company["name"] if company["name"] != "" else company["fullName"],
                                     investorId, None, None, [],investmentflag,prior2017)

        mongo.close()

    conn.close()

def get_kr36sId(kr36sourceId):
    conn = db.connect_torndb()
    sinvestor =  conn.get("select * from source_investor where source=13022 and sourceId=%s limit 1", kr36sourceId)
    conn.close()
    if sinvestor is not None:
        return int(sinvestor["id"])
    else:
        return None

def cal_fundnum():
    conn = db.connect_torndb()
    invs = conn.query("select * from investor where (active is null or active='Y')")
    # cnt_event = 0
    for inv in invs:
        cnt_event = 0
        # check investor_shortname

        if inv["name"] is not None and inv["name"].strip() != "":
            ialias = conn.get("select * from investor_alias where investorId=%s and name=%s and "
                              "(active is null or active != 'N') limit 1", inv["id"], inv["name"])
            if ialias is None:
                insql = "insert investor_alias(investorId,name,type,createTime,modifyTime,createUser) " \
                        "values(%s,%s,%s,now(),now(),139)"
                conn.insert(insql, inv["id"], inv["name"], 12020)
                logger.info("**********add name for %s %s", inv["name"],inv["id"])

        funding_investor_rels = conn.query("select distinct fundingId from funding_investor_rel "
                                           "where investorId=%s and (active is null or active='Y')", inv["id"])
        companyIds = []
        for fir in funding_investor_rels:
            funding = conn.get("select * from funding where id=%s and (active is null or active='Y')"
                               " and "
                               "("
                               "(publishDate is not null and publishDate>='2017-01-01')"
                               " or "
                               "(publishDate is null and fundingDate>='2017-01-01')"
                               ")", fir["fundingId"])

            if funding is not None and funding["corporateId"] is not None:
                # logger.info(funding)
                corporate = conn.get("select * from corporate where id=%s and (active is null or active='Y')",
                                     funding["corporateId"])
                cs = conn.query("select id from company where corporateId=%s and (active is null or active='Y')",
                                funding["corporateId"])
                # cs = conn.query("select id from company where corporateId=%s and (active is null or active='Y')",
                #                 funding["corporateId"])
                if len(cs) > 0 and corporate is not None:
                    cnt_event += 1
                for c in cs:
                    # logger.info(c)
                    if c["id"] not in companyIds:
                        companyIds.append(c["id"])
                        # break
        logger.info(companyIds)
        logger.info("found %s companies by investor: %s", len(companyIds), inv["id"])

        if len(companyIds) > 0:
            conn.update("update investor set fundingCntFrom2017=%s where id=%s", cnt_event, inv["id"])
    conn.close()




if __name__ == "__main__":
    # global DATE
    if len(sys.argv) > 1:
        invid = sys.argv[1]
        mongo = db.connect_mongo()
        collection = mongo.investor.checklist
        clists = list(collection.find({"investorId": str(invid)}))

        for clist in clists:
            logger.info("calc cross check for : %s, %s", invid, clist["investorName"])

            sids = []
            if clist["itjuziSourceInvestorId"] != "None":
                itjuziId = int(clist["itjuziSourceInvestorId"])
                sids.append(itjuziId)

            if clist["kr36InvestorId"] != "None":
                kr36Id = get_kr36sId(clist["kr36InvestorId"])
                if kr36Id is not None:
                    sids.append(kr36Id)
                    str_kr36Id = str(kr36Id)
                else:
                    str_kr36Id = None
            else:
                str_kr36Id = None
            if clist.has_key("itjuziSourceInvestorId2"):
                sids.append(int(clist["itjuziSourceInvestorId2"]))
            investorId = int(clist["investorId"])
            logger.info("cross check for %s", clist["investorName"])
            # process zhenge
            # investor id:122  --> itjuzi sourceInvestorId: 122   36kr sourceInvestorId: 18439
            # front_find(investorId, [itjuziId, kr36Id])
            # back_find(investorId, [itjuziId, kr36Id])
            front_find(investorId, sids)
            back_find(investorId, sids)
            front_find(investorId, sids, prior2017=True)
            back_find(investorId, sids, prior2017=True)
            collection.update_one({"_id": clist["_id"]},
                                  {"$set": {"crossChecked": True, "kr36SourceInvestorId": str_kr36Id,
                                            "checkTime": datetime.datetime.now()}})


    else:
        while True:
            dt = datetime.date.today()
            datestr = datetime.date.strftime(dt, '%Y%m%d')
            logger.info("last date %s", DATE)
            logger.info("now date %s", datestr)

            if datestr != DATE:
                # init
                cal_fundnum()
                DATE = datestr

            mongo = db.connect_mongo()
            collection = mongo.investor.checklist
            collection_raw = mongo.raw.projectdata
            logger.info("check investor start...")
            clists = list(collection.find({"itjuziSourceInvestorId": {"$ne": None}, "kr36Processed":True, "crossChecked": {"$ne": True}},limit=1000))
            # clists = list(collection.find({"investorId":"122"}))
            kr36s = list(collection_raw.find({"source":13022, "type":36001, "processed":{"$ne":True}}))
            logger.info("%s, %s",len(clists), len(kr36s))

            if len(kr36s) ==0:
                for clist in clists:
                    sids = []
                    if clist["itjuziSourceInvestorId"] != "None":
                        itjuziId= int(clist["itjuziSourceInvestorId"])
                        sids.append(itjuziId)

                    if clist["kr36InvestorId"] != "None":
                        kr36Id = get_kr36sId(clist["kr36InvestorId"])
                        if kr36Id is not None:
                            sids.append(kr36Id)
                            str_kr36Id = str(kr36Id)
                        else:
                            str_kr36Id = None
                    else:
                        str_kr36Id = None
                    if clist.has_key("itjuziSourceInvestorId2"):
                        sids.append(int(clist["itjuziSourceInvestorId2"]))
                    investorId = int(clist["investorId"])
                    logger.info("cross check for %s", clist["investorName"])
                    #process zhenge
                    # investor id:122  --> itjuzi sourceInvestorId: 122   36kr sourceInvestorId: 18439
                    # front_find(investorId, [itjuziId, kr36Id])
                    # back_find(investorId, [itjuziId, kr36Id])
                    front_find(investorId, sids)
                    back_find(investorId, sids)
                    front_find(investorId, sids, prior2017=True)
                    back_find(investorId, sids, prior2017=True)
                    collection.update_one({"_id": clist["_id"]},
                                                  {"$set": {"crossChecked": True, "kr36SourceInvestorId": str_kr36Id,
                                                            "checkTime": datetime.datetime.now()}})

            time.sleep(10*60)

