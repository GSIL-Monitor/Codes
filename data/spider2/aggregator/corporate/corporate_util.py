# -*- coding: utf-8 -*-
import os, sys, datetime
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper, hz

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/beian'))
import icp_chinaz
import beian_links

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/screenshot'))
import screenshot_website

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../corporate'))
import company_info_expand
# import company_aggregator
import company_aggregator_new
import company_aggregator_baseinfo
import corporate_aggregator
import company_replacement

beian_links_crawler = beian_links.BeianLinksCrawler()
icp_chinaz_crawler = icp_chinaz.IcpchinazCrawler()
screenshot_crawler = screenshot_website.phantomjsScreenshot()


#logger
loghelper.init_logger("corporate_util", stream=True)
logger = loghelper.get_logger("corporate_util")


def insert_company(name, fullName, aliases):

    conn = db.connect_torndb()
    sql = "insert company(code,name,fullName,createTime,modifyTime,active) \
           values(%s,%s,%s,now(),now(),'P')"

    code = company_aggregator_baseinfo.get_company_code(name)

    company_id = conn.insert(sql, code, name, fullName)

    aliases.extend([name, fullName])
    for s in aliases:
        if s["name"] is None or s["name"].strip() == "":
            continue
        name = s["name"].strip()
        alias = conn.get("select * from company_alias where companyId=%s and name=%s limit 1", company_id, name)
        if alias is None:
            sql = "insert company_alias(companyId,name,type,active,createTime) values(%s,%s,%s,%s,now())"
            conn.insert(sql, company_id, name, s["type"], 'Y')

    conn.close()
    return company_id


def copy_company(oldCompanyId, newCorporateId):

    conn = db.connect_torndb()
    sql = "insert company(code,name,fullName,website,brief,description,round,roundDesc,companyStatus,fundingType,currentRound,currentRoundDesc, \
           preMoney,investment,postMoney,shareRatio,currency,headCountMin,headCountMax,locationId,address,phone,establishDate,logo, \
           verify,active,createTime,modifyTime,createUser,modifyUser,confidence,privatization,shouldIndex,statusDate,corporateId) \
           values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s,%s,%s,%s,%s,%s,%s)"

    s = conn.get("select * from company where id=%s and (active is null or active='Y') limit 1",oldCompanyId)

    if s is not None:
        code = company_aggregator_baseinfo.get_company_code(s["name"])

        company_id = conn.insert(sql,
                                    code, s["name"], s["fullName"], s["website"], s["brief"], s["description"], s["round"], s["roundDesc"],
                                    s["companyStatus"], s["fundingType"], s["currentRound"], s["currentRoundDesc"],s["preMoney"], s["investment"],
                                    s["postMoney"], s["shareRatio"], s["currency"], s["headCountMin"], s["headCountMax"], s["locationId"], s["address"],
                                    s["phone"], s["establishDate"], s["logo"], s["verify"], 'P', s["createUser"], s["modifyUser"], s["confidence"],
                                    s["privatization"], s["shouldIndex"], s["statusDate"], newCorporateId
                                    )
    else:
        company_id = None

    if company_id is not None:
        #copy alias
        old_aliases = conn.query("select * from company_alias where companyId=%s", oldCompanyId)
        for oa in old_aliases:
            if oa["name"] is None or oa["name"].strip() == "":
                continue
            name = oa["name"].strip()
            alias = conn.get("select * from company_alias where companyId=%s and name=%s limit 1",company_id, name)
            if alias is None:
                sql = "insert company_alias(companyId,name,type,active,createTime) values(%s,%s,%s,%s,now())"
                conn.insert(sql, company_id, name, oa["type"], 'Y')

    conn.close()
    return company_id


def expand(sourceCompanyId):
    company_info_expand.expand_source_company(sourceCompanyId, beian_links_crawler, icp_chinaz_crawler, screenshot_crawler,test=True)

def aggregate(sourceCompany):
    company_aggregator_new.aggregator(sourceCompany)

def copy_artifacts(oldCompanyId, newCompanyId, artifactId=None):

    sql = "insert artifact(companyId,name,description,link,domain,alexa,type,productId,tags,others,rank,nameIndex,nameIndexTime,verify, \
           active,createTime,modifyTime,createUser,modifyUser,confidence,recommend,releaseDate,artifactStatus,androidExplosion,display) \
           values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s,%s,%s,%s,%s,%s,%s,%s)"
    conn = db.connect_torndb()
    if artifactId is None:
        artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y')", oldCompanyId)
    else:
        artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') and id=%s", oldCompanyId,artifactId)
    # domains = []
    for a in artifacts:
        # if a["type"] in [4010, 4040, 4050] and a["domain"] is not None and a["domain"] in domains: continue
        try:
            if a["type"] in [4010, 4040, 4050] and a["domain"] is not None and a["domain"].strip() != "":
                artifact_check = conn.get("select * from artifact where companyId=%s and domain=%s limit 1", newCompanyId, a["domain"])
            else:
                artifact_check = conn.get("select * from artifact where companyId=%s and type=%s and link=%s limit 1", newCompanyId, a["type"], a["link"])
        except:
            artifact_check = None

        if artifact_check is None:
            artifact_id = conn.insert(sql,
                               newCompanyId, a["name"],a["description"],a["link"],a["domain"],a["alexa"], a["type"], a["productId"],
                               a["tags"], a["others"], a["rank"], a["nameIndex"],a["nameIndexTime"],a["verify"],a["active"],
                               a["createUser"], a["modifyUser"],a["confidence"],a["recommend"],a["releaseDate"],a["artifactStatus"],
                               a["androidExplosion"], a["display"]
                               )
    conn.close()


def copy_fundings(newCompanyId, newCorporateId, oldCompanyId, oldCorporateId=None):
    sql = "insert funding(companyId,preMoney,postMoney,investment,shareRatio,round,roundDesc,currency,precise,fundingDate,fundingType, \
           verify,active,createTime,modifyTime,createUser,modifyUser,confidence,investorsRaw,investors,newsId,publishDate,corporateId) \
           values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),%s,%s,%s,%s,%s,%s,%s,%s)"

    conn = db.connect_torndb()
    if oldCorporateId is None:
        fundings = conn.query("select * from funding where companyId=%s and (active is null or active='Y')",  oldCompanyId)
    else:
        fundings = conn.query("select * from funding where corporateId=%s and (active is null or active='Y')",  oldCorporateId)
    for f in fundings:
        #do not check duplicate funding, need to manual check
        funding_id = conn.insert(sql,
                                  newCompanyId, f["preMoney"], f["postMoney"], f["investment"], f["shareRatio"], f["round"], f["roundDesc"],
                                  f["currency"], f["precise"], f["fundingDate"], f["fundingType"], f["verify"], f["active"],
                                  f["createTime"], f["createUser"], f["modifyUser"], f["confidence"],
                                  f["investorsRaw"], f["investors"],
                                  f["newsId"], f["publishDate"], newCorporateId
                                 )
        fundingInvestorRels = conn.query("select * from funding_investor_rel where fundingId=%s", f["id"])
        for fir in fundingInvestorRels:
            sql2 = "insert funding_investor_rel(fundingId,investorType,investorId,companyId,currency,investment,precise,verify,active, \
                   createTime,modifyTime,createUser,modifyUser,confidence) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s,%s,%s)"

            conn.insert(sql2,
                        funding_id, fir["investorType"], fir["investorId"], fir["companyId"], fir["currency"], fir["investment"],
                        fir["precise"], fir["verify"], fir["active"], fir["createUser"], fir["modifyUser"], fir["confidence"])

        mongo = db.connect_mongo()
        collection_fnews = mongo.company.funding_news
        ofnews = collection_fnews.find_one({"funding_id": int(f["id"])})
        if ofnews is not None:
            ofnews.pop("_id")
            ofnews["funding_id"] = int(funding_id)
            collection_fnews.insert(ofnews)
        mongo.close()

    conn.close()

def copy_memberRels(oldCompanyId, newCompanyIds):
    sql = "insert company_member_rel(companyId,memberId,position,joinDate,leaveDate,type,verify,active,createTime,modifyTime,createUser,modifyUser,confidence) \
           values(%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s,%s,%s)"

    conn = db.connect_torndb()
    memberRels = conn.query("select * from company_member_rel where companyId=%s and (active is null or active='Y')",oldCompanyId)
    for newCompanyId in newCompanyIds:
        for mr in memberRels:
            # do check duplicate memberRel
            mr_check = conn.get("select * from company_member_rel where companyId=%s and memberId=%s and (active is null or active='Y') limit 1",
                                newCompanyId, mr["memberId"])
            if mr_check is None:
                mr_id = conn.insert(sql,
                                    newCompanyId, mr["memberId"], mr["position"], mr["joinDate"], mr["leaveDate"], mr["type"],
                                    mr["verify"], mr["active"], mr["createUser"], mr["modifyUser"], mr["confidence"]
                                    )
    conn.close()


def copy_news(newCompanyId, oldCompanyId, oldCorporateId=None):
    conn = db.connect_torndb()
    if oldCorporateId is None:
        companies = conn.query("select * from company where companyId=%s and (active is null or active='Y')", oldCompanyId)
    else:
        companies = conn.query("select * from company where corporateId=%s and (active is null or active='Y')", oldCorporateId)
    conn.close()
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    for c in companies:
        newes = list(collection_news.find({"companyIds": int(c["id"])}))
        logger.info("***************find %s news", len(newes))
        for news in newes:
            if int(newCompanyId) not in news["companyIds"]:
                collection_news.update_one({"_id": news["_id"]}, {'$addToSet': {"companyIds": int(newCompanyId)}})
    mongo.close()

    pass

def set_active():
    pass

def get_artifacts(companyId):
    conn = db.connect_torndb()
    artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y')", companyId)
    conn.close()
    artifact_ids = [int(a["id"]) for a in artifacts]
    return artifact_ids



def decompose(oldCorporateId, newCorporateIds, replacements):
    conn = db.connect_torndb()

    for newCorporateId in newCorporateIds:
        companies = conn.query("select * from company where corporateId=%s and "
                               "(active is null or active='Y' or active='P')", newCorporateId)
        for company in companies:
            if company["code"] is None:
                code = company_aggregator_baseinfo.get_company_code(company["name"])
                conn.update("update company set code=%s where id=%s", code, company["id"])
            scs = conn.query("select * from source_company where companyId=%s and (active is null or active='Y')", company["id"])
            for sc in scs:
                logger.info("expand-aggregate %s", sc["id"])
                expand(sc["id"])
                aggregate(sc)
            logger.info("update corporate")
            corporate_aggregator.update_column(company["id"], newCorporateId)
            # add corporate_alias
            corporate_aggregator.add_corporate_alias_new(None, company["id"], newCorporateId)
            # copy_fundings(company["id"], newCorporateId, None, oldCorporateId)
            copy_news(company["id"], None, oldCorporateId)

            copy_fundings(company["id"], newCorporateId, None, oldCorporateId)

    for replacement in replacements:
        ncId = replacement["newCompanyId"]
        ocId = replacement["oldCompanyId"]
        ocompany = conn.get("select * from company where id=%s and modifyUser is not null",int(ocId))
        logger.info("old: %s", ocId)
        logger.info("new: %s", ncId)
        if ocompany is not None:
            # logger.info("company: %s|%s", ocompany["code"], ocompany["description"])
            # logger.info("update company set description=%s where id=%s", ocompany["description"], int(ncId))
            conn.update("update company set description=%s where id=%s", ocompany["description"], int(ncId))
    conn.close()

def reaggregate(oldCorporateIds, newCorporateId, oldCompanies):
    conn = db.connect_torndb()
    artifactIds_resort = []
    newsIds_resort = []
    old_company_ids = []
    new_company_ids = []
    for oldCompany in oldCompanies:
        #保留
        if oldCompany["decision"] == 1:
            new_company_id = copy_company(oldCompany["companyId"], newCorporateId)
            copy_artifacts(oldCompany["companyId"], new_company_id)
            old_company_ids.append(oldCompany["companyId"])
            new_company_ids.append(new_company_id)
        #拆分重组
        elif oldCompany["decision"] == 2:
            artifactIds_resort.extend(get_artifacts(oldCompany["companyId"]))
            #todo put artifacts and news into resort pool
            old_company_ids.append(oldCompany["companyId"])
        #删除
        elif oldCompany["decision"] == 3:
            pass
        #新增
        elif oldCompany["decision"] == 4:
            new_company_id = insert_company(oldCompany["name"], oldCompany["fullName"], oldCompany["aliases"])
            new_company_ids.append(new_company_id)

    # insert company_corporate or update company_corporate
    for ncid in new_company_ids:
        corporate_aggregator.update_corporate(ncid)
        # add corporate_alias
        corporate_aggregator.add_corporate_alias(None, ncid, newCorporateId)

    # insert member
    for ocid in old_company_ids:
        copy_memberRels(ocid, new_company_ids)

    # insert funding
    for ocid in old_company_ids:
        for ncid in new_company_ids:
            copy_fundings(ncid, newCorporateId, ocid)


def patch_company_round(company_id):
    logger.info("company id: %s", company_id)
    conn = db.connect_torndb()
    corporate = conn.get("select * from corporate where id in (select corporateId from company where id=%s)", company_id)
    if corporate is not None:
        conn.execute("delete from corporate_alias where corporateId=%s", corporate["id"])
        corporate_id = corporate["id"]
        funding = conn.get("select * from funding where corporateId=%s and (active is null or active !='N') "
                           "order by fundingDate desc limit 1",
                           corporate_id)
        if funding is not None:
                conn.update("update corporate set round=%s where id=%s",
                            funding["round"],corporate_id)
        else:
            if corporate["round"] is not None:
                conn.update("update corporate set round=-1 where id=%s", corporate["id"])
    conn.close()

def delete_old_data(company_id):
    logger.info("Deleting old data for company: %s", company_id)
    conn = db.connect_torndb()
    conn.execute("delete from company_member_rel where companyId=%s", company_id)

    fundings = list(conn.query("select id from funding where companyId=%s and "
                               "(createUser is null or createUser=-2 or createUser=-544) and "
                               "modifyUser is null", company_id))
    for funding in fundings:
        fundingId = funding["id"]
        conn.execute("delete from funding_investor_rel where fundingId=%s", fundingId)
        conn.execute("delete from funding where id=%s", fundingId)
    patch_company_round(company_id)

    conn.execute("delete from footprint where companyId=%s", company_id)
    conn.execute("delete from job where companyId=%s", company_id)
    conn.execute("delete from company_alias where companyId=%s", company_id)
    conn.execute("delete from company_recruitment_rel where companyId=%s", company_id)

    #check artifact
    artifacts = list(conn.query("select id from artifact where companyId=%s", company_id))
    for artifact in artifacts:
        artifactId= artifact["id"]
        deal_artifact = conn.get("select * from deal_artifact_rel where artifactId=%s limit 1", artifactId)
        if deal_artifact is not None:
            logger.info("artifact: %s is in deal_artifact_rel, reserve!!!")
        else:
            conn.execute("delete from source_summary_android where artifactId=%s", artifactId)
            conn.execute("delete from artifact_pic where artifactId=%s", artifactId)
            conn.execute("delete from artifact where id=%s", artifactId)
    conn.close()


def set_processStatus_zero(company_id, exclude_scid, hard):
    logger.info("Reset other source companies for company: %s", company_id)
    #aggregateGrade 1 聚合等级尽按公司全名查询
    conn = db.connect_torndb()
    if hard is True:
        conn.update("update source_company set processStatus=0, companyId=null, aggregateGrade=1"
                    " where companyId=%s and id !=%s",company_id, exclude_scid)
    else:
        conn.update("update source_company set processStatus=0, companyId=null, aggregateGrade=0"
                    " where companyId=%s and id !=%s", company_id, exclude_scid)
    conn.close()


def update_column(company, source_company):
    columns = [
        "logo",
        "fullName",
        "description",
        "productDesc",
        "modelDesc",
        "operationDesc",
        "teamDesc",
        "marketDesc",
        "compititorDesc",
        "advantageDesc",
        "planDesc",
        "brief"
    ]

    conn = db.connect_torndb()
    for column in columns:
        sql = "update company set " + column + "=%s where id=%s"
        conn.update(sql, source_company[column], company["id"])
    conn.close()


def autoDecompose(corporate_id, company_id, hard=True):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    scs = list(conn.query(
        "select * from source_company where (active is null or active='Y') and "
        "(source is not null and source != 13002 and (source < 13100 or source >= 13110)) "
        "and companyStatus!=2020 and companyId=%s order by source",
        company_id))
    conn.close()

    if len(scs) < 2:
        logger.info("Company : %s has one active source company, no need decompose", company_id)
        return True

    name = company["name"]

    reserve_sc = None
    for sc in scs:
        logger.info("source company: %s, source: %s, sourceId: %s", sc["id"], sc["source"], sc["sourceId"])
        if sc["name"].strip() != "" and sc["name"] == name:
            reserve_sc = sc
            break

    if reserve_sc is None:
        reserve_sc = scs[0]

    logger.info("Reserve source company: %s, %s for company: %s, %s",
                reserve_sc["id"], reserve_sc["name"], company["id"], company["name"])
    update_column(company,reserve_sc)
    delete_old_data(company_id)
    expand(reserve_sc["id"])
    set_processStatus_zero(company_id, reserve_sc["id"], hard)

    company_aggregator_new.aggregator(reserve_sc)
    corporate_aggregator.add_corporate_alias(reserve_sc["id"], company_id, corporate_id)
    return True


def merge_company(coid, coids):
    # return
    conn = db.connect_torndb()
    company = conn.get("select * from company where corporateId=%s and (active is null or (active!='N' "
                           "and active!='P')) limit 1", coid)

    if company is not None:

        for coidold in coids:
            if coidold == coid:
                continue
            companyolds = conn.query("select * from company where corporateId=%s", coidold)
            for companyold in companyolds:
                conn.update("update source_company set companyId=%s where companyId=%s and id>0",
                            company["id"], companyold["id"])

                conn.update("update company_recruitment_rel set companyId=%s where companyId=%s and id>0",
                            company["id"], companyold["id"])

                conn.update("update company set active='N' where id=%s", companyold["id"])

                company_replacement.replacement_company(companyold["id"], company["id"], decompose=True)
                company_replacement.reaggregate_news(companyold["id"], company["id"])

    conn.close()


def count_lagou(corporate_ids):
    a = []
    b = []
    conn = db.connect_torndb()
    for coid in corporate_ids:
        ab = True
        companies = conn.query("select * from company where corporateId=%s and (active is null or active='Y')",coid)
        if len(companies) > 1:
            ab = False
            a.append(coid)
            continue

        scs = conn.query("select * from source_company where (active is null or active!='Y') and "
                         "companyId=%s", companies[0]["id"])
        for sc in scs:
            if sc["source"] not in [13050]:
                ab = False
                break

        if ab is False:
            a.append(coid)
            continue

        b.append(coid)
    conn.close()
    return a, b


def count_verified(corporate_ids):
    a = []
    b = []
    conn = db.connect_torndb()
    ss = datetime.datetime.strptime("2017-07-01", "%Y-%m-%d")
    for coid in corporate_ids:

        companies = conn.query("select * from company where corporateId=%s and (active is null or active!='N')",coid)
        if len(companies) > 1:
            a.append(coid)
            continue

        if len(companies) == 0:
            b.append(coid)
            continue

        company = companies[0]
        if company["modifyUser"] is not None and company["verify"] == 'Y' and company["modifyTime"] >= ss \
                and (company["active"] is None or company["active"] == "Y"):
            a.append(coid)
        else:
            b.append(coid)

    conn.close()
    return a, b

def select_one(corporate_ids):
    a = []
    b = []
    conn = db.connect_torndb()
    for coid in corporate_ids:

        companies = conn.query("select * from company where corporateId=%s and (active is null or active='Y')",coid)
        if len(companies) >= 1:
            a.append(coid)
            continue
        else:
            b.append(coid)

    conn.close()
    return a, b

def select_one_more(corporate_ids):
    sid = None
    conn = db.connect_torndb()
    maxscore = 0
    for coid in corporate_ids:
        score = 0
        companies = conn.query("select * from company where corporateId=%s and (active is null or active='Y')",coid)
        if len(companies) > 1:
            sid = coid
            break
        fundings = conn.query("select * from funding where corporateId=%s and (active is null or active='Y') and "
                              "(createUser is not null and createUser!=-2 or createUser!=-544) and newsId is not null", coid)

        if len(fundings) > 0:
            score = 20 * len(fundings)

        scs = conn.query("select * from source_company where (active is null or active='Y') and "
                         "companyId=%s", companies[0]["id"])
        for sc in scs:
            logger.info("source: %s", sc["source"])
            if sc["source"] in [13022, 13030, 13400, 13401, 13402]:
                score += 10
            elif sc["source"] in [13020]:
                score += 2
            else:
                score += 1

        logger.info("cid: %s, tototo :%s", coid, score)
        if score >= maxscore:
            maxscore = score
            sid = coid

    conn.close()
    return sid


def autoMerge(corporate_ids,fullName):
    mflag = 0
    # a1, b1 = count_lagou(corporate_ids)
    # if len(corporate_ids) != len(a1) + len(b1):
    #     logger.info("wwwwrong")
    #     return

    #merge lagou other stuff
    # logger.info("Name:%s have 1 more corporates", fullName)
    # if len(corporate_ids) == len(b1) or len(corporate_ids) == len(b1) + 1:
    #     logger.info("%s - %s, %s", corporate_ids, a1, b1)
    #
    #     if len(corporate_ids) == len(b1):
    #         # merge_company(corporate_ids[0], corporate_ids)
    #         mflag = 1
    #     else:
    #         # merge_company(a1[0], corporate_ids)
    #         mflag = 1
    #
    # if mflag is 1:
    #     return mflag

    a2, b2 = count_verified(corporate_ids)
    if len(corporate_ids) != len(a2) + len(b2):
        logger.info("wwwwrong\n\n\n\n\n")
        return None

    if len(corporate_ids) == len(b2) or len(corporate_ids) == len(b2) + 1:
        # logger.info("%s - %s, %s", corporate_ids, a2, b2)

        if len(corporate_ids) == len(b2):
            a3, b3 = select_one(corporate_ids)
            if len(corporate_ids) != len(a3) + len(b3):
                logger.info("wwww222222rong\n\n\n\n\n")
                exit()
            if len(a3) == 1 and len(b3) > 0:

                # merge_company(a3[0], corporate_ids)
                mflag = 2
            elif len(a3) > 1:
                slid = select_one_more(a3)
                logger.info("selectid :%s", slid)
                # if slid is not None:
                # merge_company(slid, corporate_ids)
                mflag = 3
                # exit()
            else:
                mflag = 4
        elif len(a2) == 1 and len(b2) > 0:
            # merge_company(a2[0], corporate_ids)
            mflag = 1
        else:
            logger.info("%s - %s, %s", corporate_ids, a2, b2)
            exit()
    return mflag
    # pass



if __name__ == "__main__":
    # autoDecompose(91,295)
    # conn = db.connect_torndb()
    # cs = conn.query("select id from corporate where (active is null or active !='N') and "
    #                 "locationId is null and modifyTime>%s order by id desc",
    #                 datetime.datetime.now() - datetime.timedelta(days=3))
    # logger.info("missing %s cs location", len(cs))
    # for c in cs:
    #     patch_company_location(c["id"])
    #
    # cs2 = conn.query("select id from corporate where (active is null or active !='N') and "
    #                  "(locationId is not null and locationId<=370) and "
    #                  "establishDate is null and modifyTime>%s order by id desc",
    #                  datetime.datetime.now() - datetime.timedelta(days=3))
    #
    # logger.info("missing %s cs establishDate", len(cs2))
    # for c in cs2:
    #     patch_company_establish_date(c["id"])
    # conn.close()

    pass
