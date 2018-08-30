# -*- coding: utf-8 -*-
#重新聚合融资信息
import os, sys, datetime
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("patch_company_round", stream=True)
logger = loghelper.get_logger("patch_company_round")

def asign(comid, coid):
    mongo = db.connect_mongo()
    collection = mongo.task.homework_company
    if collection.find_one({'corporateIds': coid}) is not None:
        logger.info('already exists corporate:%s', coid)
    else:
        logger.info('inserting corporate:%s', coid)
        assignee = -548
        innnfo = getinfo(comid, coid)

        collection.insert_one({"corporateIds": [coid],
                               "taskType": 1,
                               "createTime": datetime.datetime.now(),
                               "processStatus": 0,
                               "auditStatus": 0,
                               "assignee": assignee,
                               "memo": innnfo,
                               'mark': '2013-2014融资任务'
                               })
    mongo.close()

def process(corporate_id):
    logger.info("corporate id: %s", corporate_id)
    conn = db.connect_torndb()
    funding = conn.get("select * from funding where corporateId=%s and (active is null or active !='N') order by fundingDate desc limit 1",
                       corporate_id)
    if funding is not None:
        # corporate = conn.get("select * from corporate where id=%s", corporate_id)
        # if corporate is not None:
            conn.update("update corporate set round=%s, roundDesc=%s where id=%s",
                        funding["round"],funding["roundDesc"],corporate_id)
    else:
        pass
    conn.close()

def check_homework(corporate_id):
    mongo = db.connect_mongo()
    collection = mongo.task.homework_company
    if collection.find_one({'corporateIds': corporate_id}) is not None:
        logger.info("find task")
        flag = True
    else:
        flag = False
    mongo.close()
    return flag


def getinfo(companyId, corporateId):
    info = ""
    verfyinfo = ""
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    cor = conn.query("select * from corporate where (active is null or active='Y')"
                     " and verify is null and id=%s", corporateId)
    if len(cor) > 0: verfyinfo += "corporate "
    comp = conn.query("select * from company where (active is null or active='Y')"
                      " and verify is null and id=%s", companyId)
    if len(comp) > 0: verfyinfo += "基本信息 "
    fundings = conn.query("select * from funding f left join corporate c on f.corporateId=c.id "
                          "where f.corporateId=%s and (c.active is null or c.active='Y')  and "
                          "(f.active is null or f.active='Y') and f.verify is null", corporateId)
    if len(fundings) > 0: verfyinfo += "融资 "
    artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') "
                           "and verify is null", companyId)
    if len(artifacts) > 0: verfyinfo += "产品 "
    members = conn.query("select cmr.* from company_member_rel  cmr left join member m on cmr.memberId=m.id "
                         "where cmr.companyId=%s and m.verify is null and "
                         "(cmr.type = 0 or cmr.type = 5010 or cmr.type = 5020) and "
                         "(cmr.active is null or cmr.active='Y')", companyId)
    if len(members) > 0: verfyinfo += "团队 "
    comaliases = conn.query("select * from company_alias where companyId=%s and (active is null or active='Y')"
                            " and verify is null and type=12020", companyId)
    if len(comaliases) > 0: verfyinfo += "产品线短名 "
    corpaliaes = conn.query("select * from corporate_alias where (active is null or active='Y') "
                            "and verify is null  and corporateId=%s", corporateId)
    if len(corpaliaes) > 0: verfyinfo += "corporate公司名 "
    comrecs = conn.query("select * from company_recruitment_rel where companyId=%s and "
                         "(active is null or active='Y') and verify is null", companyId)
    if len(comrecs) > 0:  verfyinfo += "招聘 "

    desc = mongo.company.modify.find_one({'companyId': companyId, 'sectionName': 'desc'})
    if desc is None:  verfyinfo += "简介 "

    conn.close()
    if len(verfyinfo) > 0:
        info = verfyinfo + "未verify"
    else:
        info = "都verify"
    # logger.info("company: %s->%s", companyId, info)
    return info

def check_funding_verify(corporate_id):
    conn = db.connect_torndb()
    fundings = conn.query("select * from funding where corporateId=%s and (active is null or active !='N')",
                          corporate_id)
    flag = True
    if len(fundings) > 0:
        for funding in fundings:
            if funding["verify"] is None:
                flag = False
                break
    else:
        flag = False
    conn.close()
    return flag

def check_verify(company_id, corporate_id):
    innfo = getinfo(company_id, corporate_id)
    if innfo == "都verify":
        logger.info("all verify")
        flag = True
    else:
        flag = False
    return flag

def check_sourcefunding(company_id, corporate_id, sources):
    conn = db.connect_torndb()
    fundings = conn.query("select * from funding where corporateId=%s and (active is null or active !='N')", corporate_id)
    flag = True
    for funding in fundings:
        if funding["round"] in [1105,1106,1110]: continue

        rels = conn.query(
            "select * from funding_investor_rel where (active is null or active='Y') and "
            "fundingId=%s order by investorId", funding["id"])
        investorIds = [int(rel["investorId"]) for rel in rels]

        f = False
        for source in sources:
            scs = conn.query("select id from source_company where companyId=%s and source=%s and "
                             "(active is null or active!='N')", company["id"], source)
            for sc in scs:
                if funding["investment"] is None:
                    sfunding = conn.get("select * from source_funding where sourceCompanyId =%s and"
                                        " fundingDate>date_sub(%s,interval 1 month) and "
                                        "fundingDate<date_add(%s,interval 1 month) and round=%s and "
                                        "(investment is null or investment=0) limit 1",
                                        sc["id"], funding["fundingDate"], funding["fundingDate"],
                                        funding["round"])
                else:
                    sfunding = conn.get("select * from source_funding where sourceCompanyId =%s and"
                                        " fundingDate>date_sub(%s,interval 1 month) and "
                                        "fundingDate<date_add(%s,interval 1 month) and round=%s and "
                                        "investment=%s limit 1",
                                        sc["id"], funding["fundingDate"], funding["fundingDate"],
                                        funding["round"], funding["investment"])
                if sfunding is not None:
                    srels = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s "
                                       , sfunding["id"])
                    if len(rels) == len(srels):
                        logger.info("total same with funding:%s and source funding:%s", funding["id"],sfunding["id"])
                        f = True
                        break
            if f is True: break

        if f is False:
            flag = False
            break
    conn.close()
    return flag



if __name__ == '__main__':
    logger.info("Begin...")
    year = 2013
    endYear = 2015
    num = 0
    (num0, num1, num2, num3, num4, num5, num6, num7) = (0, 0, 0, 0, 0, 0, 0, 0)
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    results = []
    tasksMap = {}
    tasksCom = []
    # cids = list(mongo.aggreTest.fundingTest.find({}))
    # for cid in cids:
    #
    #     icompanies = conn.query("select * from company where (active is null or active !='N') "
    #                         "and id=%s", cid["companyId"])
    icompanies = conn.query("select * from company where (active is null or active !='N') ")
    #     results = []
    #     tasksMap = {}
    #     tasksCom = []
    for company in icompanies:
        if company["id"] is None or company["corporateId"] is None: continue
        corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
        # if corporate["locationId"] is not None and corporate["locationId"] > 370: continue

        company["xiniuInvestor"] = "N"
        company["itjuziInvestor"] = "N"
        company["kr36Investor"] = "N"

        fundings = conn.query("select * from funding where (active is null or active='Y')"
                              " and "
                              "((publishDate is not null and publishDate>='%s-01-01')"
                              " or "
                              "(publishDate is null and fundingDate>='%s-01-01'))"
                              "and ((publishDate is not null and publishDate<'%s-01-01')"
                              " or "
                              "(publishDate is null and fundingDate<'%s-01-01'))"
                              " and corporateId=%s", year, year, endYear, endYear, company["corporateId"])
        if len(fundings) == 1 and fundings[0]["round"] is not None and fundings[0]["round"] in [1105,
                                                                                                1110]: continue

        if len(fundings) >= 1: company["xiniuInvestor"] = "Y"

        for sname in ["itjuziInvestor", "kr36Investor"]:
            sfundings = []
            if sname == "kr36Investor":
                source = 13022
            else:
                source = 13030

            scs = conn.query("select id from source_company where companyId=%s and source=%s and "
                             "(active is null or active!='N')", company["id"], source)
            if len(scs) > 0:

                for sc in scs:
                    sfundings = conn.query("select * from source_funding where sourceCompanyId =%s and "
                                           "fundingDate>='%s-01-01' and fundingDate <'%s-01-01'", sc["id"], year,
                                           endYear
                                           )

                    if len(sfundings) >= 1:
                        # logger.info(sfundings[0])
                        company[sname] = "Y"

        if company["xiniuInvestor"] == "Y" or company["itjuziInvestor"] == "Y" or company["kr36Investor"] == "Y":
            logger.info("%s/%s/%s/%s/%s", company["id"],company["code"], company["xiniuInvestor"], company["itjuziInvestor"],
                        company["kr36Investor"])

            num += 1
            if company["corporateId"] not in tasksCom: tasksCom.append(company["corporateId"])
            if check_homework(company["corporateId"]) is False and check_verify(company["id"],company["corporateId"]) is False:
                tasksMap[company["corporateId"]] = {'vinfo': 1}

                if mongo.aggreTest.fundingTest.find_one({'companyId': company["id"]}) is not None:
                    pass
                else:
                    mongo.aggreTest.fundingTest.insert_one({'companyId': company["id"]})

                if check_funding_verify(company["corporateId"]) is True:
                    #done NUM1
                    num0 += 1
                    continue

                if company["xiniuInvestor"] == "Y":
                    if company["kr36Investor"] == "Y":
                        f1 = check_sourcefunding(company["id"], company["corporateId"], [13022])
                        if f1 is True:
                            num1 += 1
                            #DONE NUM2
                            logger.info("total match best one")
                            continue
                        else:

                            if company["itjuziInvestor"] == "Y":
                                f2 = check_sourcefunding(company["id"], company["corporateId"], [13022, 13030])
                                if f2 is True:
                                    num2 += 1
                                    #DONE NUM3
                                    asign(company["id"], company["corporateId"])
                                    logger.info("total match better one")
                                    continue

                            #DONE NUM5
                            logger.info("something wrong with 36funding******************")
                            num5 += 1
                            asign(company["id"], company["corporateId"])

                    else:
                        if company["itjuziInvestor"] == "Y":
                            f3 = check_sourcefunding(company["id"], company["corporateId"], [13030])
                            if f3 is True:
                                num3 += 1
                                #DONE NUM4
                                logger.info("total match best one 2")
                                continue

                            logger.info("something wrong with itjunzifunding*********")
                            num5 += 1
                            asign(company["id"],company["corporateId"])
                            # DONE NUM5

                        else:
                            num6 += 1
                            asign(company["id"], company["corporateId"])
                            #DONE NUM6
                            logger.info("something wrong with no evidence******************")
                        # else:
                        #     logger.info("******************")

                    # logger.info("************************")

                else:
                    if company["kr36Investor"] == "Y":
                        #DONE NUM7
                        num4 += 1
                        logger.info("patch 36kr")
                        if mongo.aggreTest.fundingTestPatch36Funding.find_one({'companyId': company["id"]}) is not None:
                            pass
                        else:
                            mongo.aggreTest.fundingTestPatch36Funding.insert_one({'companyId': company["id"]})
                    else:
                        num7 += 1
                        logger.info("missing")




    mongo.close()
    logger.info("total num, %s/%s", len(tasksCom), len(tasksMap))
    logger.info("%s/%s/%s/%s/%s/%s/%s/%s", num0, num1, num2, num3, num4, num5, num6, num7)