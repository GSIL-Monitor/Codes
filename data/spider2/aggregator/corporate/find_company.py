# -*- coding: utf-8 -*-
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper, hz
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper

#logger
loghelper.init_logger("find_company", stream=True)
logger = loghelper.get_logger("find_company")

def find_company_grade1(source_company):
    if source_company["companyId"] is not None:
        return source_company["companyId"]

    if source_company["fullName"] is not None and source_company["fullName"].strip() != "":
        full_name = name_helper.company_name_normalize(source_company["fullName"].strip())
        conn = db.connect_torndb()
        company = conn.get("select * from company where fullName=%s and "
                           "(active is null or active !='N') limit 1", full_name)
        conn.close()
        if company is not None:
            logger.info("find_company_by_full_name 1")
            return company["id"]

    return None

def find_company_grade2(source_company,idmax=0):
    # if source_company["companyId"] is not None:
    #     return source_company["companyId"]

    conn = db.connect_torndb()
    company_names = list(
        conn.query("select * from source_company_name where sourceCompanyId=%s and "
                   "(chinese is null or chinese='Y') and type=12010", source_company["id"]))
    conn.close()

    fullNames = [company_name["name"] for company_name in company_names]
    if source_company["fullName"] is not None and source_company["fullName"].strip() != "" and \
       source_company["fullName"] not in fullNames:
        fullNames.append(source_company["fullName"])


    company_ids = find_companies_by_full_name_corporate(fullNames, idmax)

    # if len(company_ids) == 0:
    #     conn = db.connect_torndb()
    #     source_artifacts = list(conn.query("select * from source_artifact where sourceCompanyId=%s and "
    #                                        "(verify is null or verify='Y') and (active is null or active='Y')",
    #                                        source_company["id"]))
    #     conn.close()
    #
    #     company_ids = find_companies_by_artifacts(source_artifacts, idmax)

    # company_ids1 = find_companies_by_full_name_corporate(fullNames, idmax)
    #
    # # if len(company_ids) == 0:
    # conn = db.connect_torndb()
    # source_artifacts = list(conn.query("select * from source_artifact where sourceCompanyId=%s and "
    #                                    "(verify is null or verify='Y') and (active is null or active='Y')",
    #                                    source_company["id"]))
    # conn.close()
    #
    # company_ids2 = find_companies_by_artifacts(source_artifacts, idmax)
    #
    # company_ids = []
    #
    # if len(company_ids1)>0:
    #     for cid1 in company_ids1:
    #         if cid1 in company_ids2: company_ids.append(cid1)

    # return company_ids
    if len(company_ids) > 0:
        return company_ids[0]
    else:
        return None


def find_reference(source_company,idmax=0):
    # if source_company["companyId"] is not None:
    #     return source_company["companyId"]
    candidate_company_ids = []
    conn = db.connect_torndb()
    company_names = list(
        conn.query("select * from source_company_name where sourceCompanyId=%s and type=12020", source_company["id"]))
    conn.close()

    for cn in company_names:
        short_name = cn["name"]
        if short_name is None or short_name.strip() == "":
            continue
        short_name = short_name.strip()

        logger.info("short_name: %s", short_name)
        # candidate_company_ids = []
        cs = list(conn.query("select * from company" 
                             " where name=%s and (active is null or active !='N')", short_name))
        for c in cs:
            company_id = c["id"]
            candidate_company_ids.append(company_id)
            break

        aliases = list(conn.query("select a.companyId from company_alias"
                                  " a join company c on c.id=a.companyId " +
                                  "where (c.active is null or c.active!='N') and a.name=%s",short_name))
        for alias in aliases:
            company_id = alias["companyId"]
            candidate_company_ids.append(company_id)
            break

    # return company_ids
    if len(candidate_company_ids) > 0:
        return candidate_company_ids[0]
    else:
        return None

def find_company_new(source_company,idmax=0):
    # if source_company["companyId"] is not None:
    #     return source_company["companyId"]

    conn = db.connect_torndb()
    company_names = list(
        conn.query("select * from source_company_name where sourceCompanyId=%s and "
                   "(chinese is null or chinese='Y') and type=12010", source_company["id"]))
    conn.close()

    fullNames = [company_name["name"] for company_name in company_names]
    if source_company["fullName"] is not None and source_company["fullName"].strip() != "" and \
       source_company["fullName"] not in fullNames:
        fullNames.append(source_company["fullName"])


    company_ids = find_companies_by_full_name_corporate(fullNames, idmax)

    if len(company_ids) == 0:
        conn = db.connect_torndb()
        source_artifacts = list(conn.query("select * from source_artifact where sourceCompanyId=%s and "
                                           "(verify is null or verify='Y') and (active is null or active='Y')",
                                           source_company["id"]))
        conn.close()

        company_ids = find_companies_by_artifacts(source_artifacts, idmax)

    # company_ids1 = find_companies_by_full_name_corporate(fullNames, idmax)
    #
    # # if len(company_ids) == 0:
    # conn = db.connect_torndb()
    # source_artifacts = list(conn.query("select * from source_artifact where sourceCompanyId=%s and "
    #                                    "(verify is null or verify='Y') and (active is null or active='Y')",
    #                                    source_company["id"]))
    # conn.close()
    #
    # company_ids2 = find_companies_by_artifacts(source_artifacts, idmax)
    #
    # company_ids = []
    #
    # if len(company_ids1)>0:
    #     for cid1 in company_ids1:
    #         if cid1 in company_ids2: company_ids.append(cid1)

    # return company_ids
    if len(company_ids) > 0:
        return company_ids[0]
    else:
        return None

def find_company(source_company, test=False):
    logger.info("find_company")
    if not test:
        if source_company["companyId"] is not None:
            return source_company["companyId"]

    #按公司名查询
    if source_company["fullName"] is not None and source_company["fullName"].strip() != "":
        company_id = find_company_by_full_name(source_company["fullName"], test)
        if company_id is not None:
            return company_id

    conn = db.connect_torndb()
    company_names = list(conn.query("select * from source_company_name where sourceCompanyId=%s and type=12010", source_company["id"]))
    conn.close()

    for company_name in company_names:
        logger.info(company_name["name"])
        company_id = find_company_by_full_name(company_name["name"], test)
        if company_id is not None:
            return company_id

    #按artifact查询
    conn = db.connect_torndb()
    source_artifacts = list(conn.query("select * from source_artifact where sourceCompanyId=%s and (verify is null or verify='Y')", source_company["id"]))
    conn.close()

    for source_artifact in source_artifacts:
        company_id = find_company_by_artifact(source_artifact, test)
        if company_id is not None:
            return company_id

    #按短名(产品名)查询
    company_id = find_company_by_short_name(source_company, test)

    return company_id


def find_company_by_full_name(full_name, test=False):
    logger.info("find_company_by_full_name")
    if full_name is None or full_name == "":
        return None

    full_name = name_helper.company_name_normalize(full_name)

    # table_names = helper.get_table_names(test)
    #
    # conn = db.connect_torndb()
    # company = conn.get("select * from " + table_names["company"] + " where fullName=%s and (active is null or active !='N') limit 1", full_name)
    # conn.close()
    # if company is not None:
    #     logger.info("find_company_by_full_name 1")
    #     return company["id"]
    #
    # conn = db.connect_torndb()
    # company_alias = conn.get("select a.* from " + table_names["company_alias"] +
    #                          " a join " + table_names["company"] + " c on c.id=a.companyId " +
    #                          "where (c.active is null or c.active !='N') and a.type=12010 and a.name=%s limit 1",
    #                          full_name)
    # conn.close()
    # if company_alias is not None:
    #     logger.info("find_company_by_full_name 2")
    #     return company_alias["companyId"]
    # return None

    company_ids = find_companies_by_full_name_corporate([full_name])

    if len(company_ids) > 0:
        return company_ids[0]
    else:
        return None

def find_companies_by_full_name_corporate(full_names, idmax=0):
    companyIds = []
    for full_name in full_names:
        if full_name is None or full_name == "":
            continue

        full_name = name_helper.company_name_normalize(full_name)

        conn = db.connect_torndb()
        corporate_aliases = conn.query("select a.* from corporate_alias a join corporate c on c.id=a.corporateId where "
                                       "(c.active is null or c.active !='N') and (a.active is null or a.active !='N') "
                                       "and a.name=%s",
                                       full_name)
        # conn.close()
        for ca in corporate_aliases:
            # logger.info("*******found %s",ca)
            company = conn.get("select * from company where corporateId=%s and (active is null or active!='N') limit 1",
                               ca["corporateId"])
            if company is not None:
                logger.info("find_company_by_full_name %s: %s", full_name, company["id"])
                if company["id"] not in companyIds:
                    if int(company["id"]) > idmax:
                        companyIds.append(company["id"])
        conn.close()
    return companyIds


def find_company_by_artifact(source_artifact, test=False):
    table_names = helper.get_table_names(test)

    # author是运营者, apkname是开发者
    # logger.info("find_company_by_artifact")
    #if source_artifact["type"] != 4040 and source_artifact["type"] != 4050:
    if source_artifact["type"] == 4010:
        if source_artifact["link"] is not None and source_artifact["type"] != "":
            link = source_artifact["link"]
            if link.endswith("/") > 0:
                link1 = link
                link2 = link[:-1]
            else:
                link1 = link
                link2 = link + "/"

            logger.info("link 1 2 try to figure out %s / %s", link1, link2)
            conn = db.connect_torndb()
            artifact = conn.get("select a.* from " + table_names["artifact"] + " a join " +
                                table_names["company"] + " c on c.id=a.companyId " +
                                "where (c.active is null or c.active !='N') and a.type=%s and a.link=%s limit 1",
                                source_artifact["type"],
                                link1)
            if artifact is not None:
                artifact = conn.get("select a.* from " + table_names["artifact"] + " a join " +
                                    table_names["company"] + " c on c.id=a.companyId " +
                                    "where (c.active is null or c.active !='N') and a.type=%s and a.link=%s limit 1",
                                    source_artifact["type"],
                                    link2)
            conn.close()
            if artifact is not None:
                logger.info("find_company_by_artifact 1, %s, %s", artifact["type"], artifact["link"])
                return artifact["companyId"]

        if source_artifact["domain"] is not None and source_artifact["domain"] != "":
            conn = db.connect_torndb()
            artifact = conn.get("select a.* from " + table_names["artifact"] + " a join " +
                                table_names["company"] + " c on c.id=a.companyId " +
                                "where (c.active is null or c.active !='N') and a.type=%s and a.domain=%s limit 1",
                                    source_artifact["type"],
                                    source_artifact["domain"])
            conn.close()
            if artifact is not None:
                logger.info("find_company_by_artifact 2, %s, %s", artifact["type"], artifact["domain"])
                return artifact["companyId"]
    return None

def find_companies_by_artifacts(source_artifacts, idmax=0):
    companyIds = []
    # author是运营者, apkname是开发者
    # logger.info("find_company_by_artifact")
    #if source_artifact["type"] != 4040 and source_artifact["type"] != 4050:
    for source_artifact in source_artifacts:
        if source_artifact["type"] == 4010:
            if source_artifact["link"] is not None and source_artifact["type"] != "":
                link = source_artifact["link"]
                if link.endswith("/") > 0:
                    link1 = link
                    link2 = link[:-1]
                else:
                    link1 = link
                    link2 = link + "/"

                logger.info("link 1 2 try to figure out %s / %s", link1, link2)
                conn = db.connect_torndb()
                artifacts = conn.query("select a.* from artifact a join company c on c.id=a.companyId "
                                       "where (c.active is null or c.active !='N') and a.type=%s and a.link=%s",
                                       source_artifact["type"],
                                       link1)
                if len(artifacts) == 0:
                    artifacts = conn.query("select a.* from artifact a join company c on c.id=a.companyId "
                                           "where (c.active is null or c.active !='N') and a.type=%s and a.link=%s",
                                           source_artifact["type"],
                                           link2)
                conn.close()
                if len(artifacts) > 0:
                    for artifact in artifacts:
                        logger.info("find_company_by_artifact 1, %s, %s, %s", artifact["type"], artifact["link"],
                                    artifact["companyId"])
                        if artifact["companyId"] not in companyIds:
                            if int(artifact["companyId"]) > idmax:
                                companyIds.append(artifact["companyId"])

            if len(companyIds) == 0:
                if source_artifact["domain"] is not None and source_artifact["domain"] != "":
                    conn = db.connect_torndb()
                    artifacts = conn.query("select a.* from artifact a join company c on c.id=a.companyId "
                                        "where (c.active is null or c.active !='N') and a.type=%s and a.domain=%s",
                                            source_artifact["type"],
                                            source_artifact["domain"])
                    conn.close()
                    if len(artifacts) > 0:
                        for artifact in artifacts:
                            logger.info("find_company_by_artifact 2, %s, %s, %s", artifact["type"], artifact["domain"],
                                        artifact["companyId"])
                            if artifact["companyId"] not in companyIds:
                                if int(artifact["companyId"]) > idmax:
                                    companyIds.append(artifact["companyId"])
    return companyIds



def find_company_by_short_name(source_company, test=False):
    #产品名相同,则判断
    #1. 地区相同
    #2. 成立日期相同
    #3. member有相同
    #4. 融资事件

    table_names = helper.get_table_names(test)

    logger.info("find_company_by_short_name")
    matched_company_id = None

    conn = db.connect_torndb()
    source_members = list(conn.query("select m.* from source_company_member_rel r join source_member m on m.id=r.sourceMemberId where r.sourceCompanyId=%s", source_company["id"]))

    source_investor_ids = {}
    source_fundings = list(conn.query("select * from source_funding where sourceCompanyId=%s",source_company["id"]))
    for sf in source_fundings:
        rels = list(conn.query("select * from source_funding_investor_rel where sourceFundingId=%s",sf["id"]))
        for rel in rels:
            source_investor = conn.get("select * from source_investor where id=%s", rel["sourceInvestorId"])
            if source_investor["investorId"] is not None:
                source_investor_ids[source_investor["investorId"]] = 1

    short_names = list(conn.query("select * from source_company_name where type=12020 and sourceCompanyId=%s", source_company["id"]))
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
        cs = list(conn.query("select * from " + table_names["company"] +
                             " where name=%s and (active is null or active !='N')", short_name))
        for c in cs:
            company_id = c["id"]
            candidate_company_ids.append(company_id)

        aliases = list(conn.query("select a.companyId from " + table_names["company_alias"] +
                                  " a join " + table_names["company"] + " c on c.id=a.companyId " +
                                  "where (c.active is null or c.active!='N') and a.name=%s",short_name))
        for alias in aliases:
            company_id = alias["companyId"]
            candidate_company_ids.append(company_id)

        for company_id in candidate_company_ids:
            company = conn.get("select * from " + table_names["company"] + " where id=%s and (active is null or active='Y')", company_id)
            if company is None:
                continue

            #地区
            location1 = source_company["locationId"]
            location2 = company["locationId"]
            if location1 > 0 and location1==location2:
                matched_company_id = company_id
                logger.info("find_company_by_short_name, location")
                break

            #成立日期
            date1 = source_company["establishDate"]
            date2 = company["establishDate"]
            if date1 is not None and date2 is not None and \
                date1.year==date2.year and date1.month==date2.month:
                matched_company_id = company_id
                logger.info("find_company_by_short_name, establish date")
                break

            #member
            members = list(conn.query("select m.* from " + table_names["company_member_rel"] +
                                      " r join " + table_names["member"] + " m on m.id=r.memberId where r.companyId=%s", company_id))
            for member in members:
                member_name = member["name"]
                logger.info("member_name: %s", member_name)
                if member_name is None or member_name == "":
                    continue
                if not hz.is_chinese_string(member_name):
                    continue
                for source_member in source_members:
                    #logger.info("source_member_name: %s", source_member["name"])
                    if member_name == source_member["name"]:
                        matched_company_id = company_id
                        logger.info("find_company_by_short_name, member")
                        break
                if matched_company_id is not None:
                    break
            if matched_company_id is not None:
                    break

            # gongshang member
            # TODO

            #funding
            fundings = list(conn.query("select * from " + table_names["funding"] + " where companyId=%s",company_id))
            for f in fundings:
                rels = list(conn.query("select * from " + table_names["funding_investor_rel"] + " where fundingId=%s",f["id"]))
                for rel in rels:
                    if source_investor_ids.has_key(rel["investorId"]):
                        matched_company_id = company_id
                        logger.info("find_company_by_short_name, funding")
                        break
                if matched_company_id is not None:
                    break

            if matched_company_id is not None:
                break
        if matched_company_id is not None:
            break
    conn.close()
    return matched_company_id