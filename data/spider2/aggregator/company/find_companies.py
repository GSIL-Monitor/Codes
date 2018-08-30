# -*- coding: utf-8 -*-
# find all candidates
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper, hz
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

#logger
loghelper.init_logger("find_company", stream=True)
logger = loghelper.get_logger("find_company")

def add_to_candidates(candidates, cand):
    exist = False
    for c in candidates:
        if c["companyId"] == cand["companyId"]:
            exist = True
            break
    if exist is False:
        candidates.append(cand)


def find_company1(sourceCompanyId):
    conn = db.connect_torndb()
    source_company = conn.get("select * from source_company where id=%s", sourceCompanyId)
    conn.close()
    return find_company(source_company)


def find_company(source_company):
    candidates = []
    logger.info("find_company")

    #已聚合
    if source_company["companyId"] is not None:
        cand = {"companyId": source_company["companyId"],
                "type": 1}
        return [cand]

    #按公司名查询
    if source_company["fullName"] is not None and source_company["fullName"].strip() != "":
        companyIds = find_company_by_full_name(source_company["fullName"])
        for company_id in companyIds:
            cand = {"companyId": company_id,
                    "type": 10}
            add_to_candidates(candidates, cand)

        companyIds = find_company_by_full_name_from_alias(source_company["fullName"])
        for company_id in companyIds:
            cand = {"companyId": company_id,
                    "type": 11}
            add_to_candidates(candidates, cand)

    #按扩展出来的公司名查询
    conn = db.connect_torndb()
    company_names = list(conn.query("select * from source_company_name "
                                    "where sourceCompanyId=%s and type=12010 "
                                    "and (verify is null or verify='Y')",
                                    source_company["id"]))
    conn.close()
    for company_name in company_names:
        logger.info(company_name["name"])
        companyIds = find_company_by_full_name(company_name["name"])
        for company_id in companyIds:
            cand = {"companyId": company_id,
                    "type": 12}
            add_to_candidates(candidates, cand)

        companyIds = find_company_by_full_name_from_alias(company_name["name"])
        for company_id in companyIds:
            cand = {"companyId": company_id,
                    "type": 13}
            add_to_candidates(candidates, cand)


    #按artifact查询
    conn = db.connect_torndb()
    source_artifacts = list(conn.query("select * from source_artifact "
                                       "where sourceCompanyId=%s and (verify is null or verify='Y')",
                                       source_company["id"]))
    conn.close()

    for source_artifact in source_artifacts:
        #website
        companyIds = find_company_by_artifact_website(source_artifact)
        for company_id in companyIds:
            cand = {"companyId": company_id,
                    "type": 20}
            add_to_candidates(candidates, cand)
        #weibo, wechat
        #ios, android


    #按短名(产品名)查询
    _candidates = find_company_by_short_name(source_company)
    candidates.extend(_candidates)

    return candidates


def find_company_by_full_name(full_name):
    logger.info("find_company_by_full_name")
    if full_name is None or full_name == "":
        return []

    full_name = name_helper.company_name_normalize(full_name)

    conn = db.connect_torndb()
    companies = conn.query("select * from company where fullName=%s and (active is null or active !='N')", full_name)
    conn.close()
    companyIds =[]
    for company in companies:
        companyIds.append(company["id"])
    return companyIds


def find_company_by_full_name_from_alias(full_name):
    logger.info("find_company_by_full_name_from_aias")
    if full_name is None or full_name == "":
        return []

    full_name = name_helper.company_name_normalize(full_name)

    conn = db.connect_torndb()
    company_aliases = conn.get("select a.* from company_alias a join company c on c.id=a.companyId "
                             "where (c.active is null or c.active !='N') and "
                             "(a.active is null or a.active != 'N' and "
                             "a.type=12010 and a.name=%s",
                             full_name)
    conn.close()
    companyIds =[]
    for company_alias in company_aliases:
        companyIds.append(company_alias["companyId"])
    return companyIds


def find_company_by_artifact_website(source_artifact):
    logger.info("find_company_by_artifact_website")
    companyIds = []
    if source_artifact["type"] == 4010:
        if source_artifact["link"] is not None and source_artifact["type"] != "":
            conn = db.connect_torndb()
            artifacts = conn.get("select a.* from artifact a join company c on c.id=a.companyId "
                                "where (c.active is null or c.active !='N') and "
                                "(a.active is null or a.active != 'N' and "
                                "a.type=%s and a.link=%s",
                                source_artifact["type"],
                                source_artifact["link"])
            conn.close()
            for artifact in artifacts:
                companyIds.append(artifact["companyId"])

        if source_artifact["domain"] is not None and source_artifact["domain"] != "":
            conn = db.connect_torndb()
            artifacts = conn.get("select a.* from artifact a join company c on c.id=a.companyId "
                                "where (c.active is null or c.active !='N') "
                                "(a.active is null or a.active != 'N' and "
                                "and a.type=%s and a.domain=%s",
                                    source_artifact["type"],
                                    source_artifact["domain"])
            conn.close()
            for artifact in artifacts:
                companyIds.append(artifact["companyId"])

    return companyIds


def find_company_by_short_name(source_company):
    #产品名相同,则判断
    #1. 地区相同
    #2. 成立日期相同
    #3. member有相同
    #4. 融资事件

    logger.info("find_company_by_short_name")
    candidates = []

    conn = db.connect_torndb()
    source_members = list(conn.query("select m.* from source_company_member_rel r "
                                     "join source_member m on m.id=r.sourceMemberId "
                                     "where (r.verify is null or r.verify='Y') and "
                                     "r.sourceCompanyId=%s",
                                     source_company["id"]))

    source_investor_ids = {}
    source_fundings = list(conn.query("select * from source_funding "
                                      "where (verify is null or verify='Y') and sourceCompanyId=%s",
                                      source_company["id"]))
    for sf in source_fundings:
        rels = list(conn.query("select * from source_funding_investor_rel "
                               "where (verify is null or verify='Y') and sourceFundingId=%s",
                               sf["id"]))
        for rel in rels:
            source_investor = conn.get("select * from source_investor where id=%s",
                                       rel["sourceInvestorId"])
            if source_investor["investorId"] is not None:
                source_investor_ids[source_investor["investorId"]] = 1

    short_names = list(conn.query("select * from source_company_name "
                                  "where (verify is null or verify='Y') and type=12020 and sourceCompanyId=%s",
                                  source_company["id"]))
    sns = []
    for s in short_names:
        sns.append(s["name"])

    if source_company["name"] not in sns:
        sns.append(source_company["name"])

    for short_name in sns:
        if short_name is None or short_name.strip() == "":
            continue
        short_name = short_name.strip()

        logger.info("short_name: %s", short_name)
        candidate_company_ids = []
        cs = list(conn.query("select * from company "
                             "where name=%s and (active is null or active !='N')",
                             short_name))
        for c in cs:
            company_id = c["id"]
            candidate_company_ids.append(company_id)

        aliases = list(conn.query("select a.companyId from company_alias a "
                                  "join company c on c.id=a.companyId "
                                  "where (c.active is null or c.active='Y') and "
                                  "(a.active is null or a.active='Y') and "
                                  "a.name=%s",
                                  short_name))
        for alias in aliases:
            company_id = alias["companyId"]
            candidate_company_ids.append(company_id)

        for company_id in candidate_company_ids:
            company = conn.get("select * from company "
                               "where id=%s and (active is null or active='Y')",
                               company_id)
            if company is None:
                continue

            #地区
            location1 = source_company["locationId"]
            location2 = company["locationId"]
            if location1 > 0 and location1==location2:
                cand = {"companyId": company_id,
                        "type": 31}
                add_to_candidates(candidates, cand)


            #成立日期
            date1 = source_company["establishDate"]
            date2 = company["establishDate"]
            if date1 is not None and date2 is not None and \
                date1.year==date2.year and date1.month==date2.month:
                cand = {"companyId": company_id,
                        "type": 32}
                add_to_candidates(candidates, cand)

            #member
            members = list(conn.query("select m.* from company_member_rel r "
                                      "join member m on m.id=r.memberId "
                                      "where (r.active is null or r.active='Y') and r.companyId=%s",
                                      company_id))
            for member in members:
                member_name = member["name"]
                if member_name is None or member_name == "":
                    continue
                if not hz.is_chinese_string(member_name):
                    continue
                for source_member in source_members:
                    #logger.info("source_member_name: %s", source_member["name"])
                    if member_name == source_member["name"]:
                        cand = {"companyId": company_id,
                                "type": 33}
                        add_to_candidates(candidates, cand)

            #funding
            fundings = list(conn.query("select * from funding where (active is null or active='Y') and "
                                       "companyId=%s",
                                       company_id))
            for f in fundings:
                rels = list(conn.query("select * from funding_investor_rel where (active is null or active='Y') and "
                                       "fundingId=%s",
                                       f["id"]))
                for rel in rels:
                    if source_investor_ids.has_key(rel["investorId"]):
                        cand = {"companyId": company_id,
                                "type": 34}
                        add_to_candidates(candidates, cand)

    conn.close()
    return candidates


if __name__ == "__main__":
    candidates = find_company1(1)
    for can in candidates:
        print "companyId: %s, type: %s" % (can["companyId"], can["type"])