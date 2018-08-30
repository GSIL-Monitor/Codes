# -*- coding: utf-8 -*-
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper, hz

import merge_company

#logger
loghelper.init_logger("find_duplicate_company", stream=True)
logger = loghelper.get_logger("find_duplicate_company")

#companyalias flag
caflag = False
#artifact flag
aflag = False
#website flag
wflag = False
#fullName flag
fflag = True
#short Name flag
sflag = True

def find_company(company):
    global caflag
    global aflag
    global wflag
    global fflag
    global sflag

    logger.info("Start id: %s, name: %s", company["id"], company["name"])
    conn = db.connect_torndb()
    cc = conn.get("select * from company where id=%s", company["id"])
    conn.close()
    if cc is None or (cc["active"] is not None and cc["active"] == 'N'):
        return None

    company_id = None
    #按公司名
    companyNames = []

    # add company_alias into checking list
    if caflag is True:
        conn = db.connect_torndb()
        company_names = list(conn.query("select * from company_alias where companyId=%s and type=12010", company["id"]))
        conn.close()
        for company_name in company_names:
            if company_name["name"] is not None and company_name not in companyNames:
                companyNames.append(company_name["name"])

    if fflag is True:
        if company["fullName"] is not None and company["fullName"] not in companyNames:
            companyNames.append(company["fullName"])

    for companyName in companyNames:
        logger.info(companyName)
        company_id = find_company_by_full_name(company["id"], companyName)
        if company_id is not None:
            return company_id

    if wflag is True:
        if company["website"] is not None:
            company_id = find_company_by_website(company["id"], company["website"])
            if company_id is not None:
                return company_id

    #按artifact查询
    if aflag is True:
        conn = db.connect_torndb()
        artifacts = list(conn.query("select * from artifact where companyId=%s and (verify is null or verify='Y') and (active is null or active='N')", company["id"]))
        conn.close()

        for artifact in artifacts:
            company_id = find_company_by_artifact(company["id"], artifact)
            if company_id is not None:
                return company_id

    #按短名(产品名)查询
    if sflag is True:
        company_id = find_company_by_short_name(company)

    return company_id


def find_company_by_full_name(companyId, full_name):
    global caflag
    logger.info("find_company_by_full_name")
    if full_name is None or full_name.strip() == "":
        return None

    full_name = name_helper.company_name_normalize(full_name)
    conn = db.connect_torndb()
    company = conn.get("select * from company where fullName=%s and (active is null or active !='N') and id!=%s order by id desc limit 1", full_name, companyId)
    conn.close()
    if company is not None:
        logger.info("find_company_by_full_name 1")
        return company["id"]

    # add company_alias into checking list
    if caflag is True:
        conn = db.connect_torndb()
        company_alias = conn.get("select a.* from company_alias a join company c on c.id=a.companyId where (c.active is null or c.active !='N') \
                                    and a.type=12010 and a.name=%s and c.id!=%s order by c.id desc limit 1", full_name, companyId)
        conn.close()
        if company_alias is not None:
            logger.info("find_company_by_full_name 2")
            return company_alias["companyId"]
    return None


def find_company_by_website(companyId, website):
    logger.info("find_company_by_website")
    if website is None or website.strip() == "":
        return None

    conn = db.connect_torndb()
    company = conn.get("select * from company where website=%s and (active is null or active !='N') and id!=%s order by id desc limit 1",website, companyId)
    conn.close()
    if company is not None:
        logger.info("find_company_by_website")
        return company["id"]
    return None

def find_company_by_artifact(companyId, artifact):
    # author是运营者, apkname是开发者
    logger.info("find_company_by_artifact")
    if artifact["type"] == 4010:
        #pass
        if artifact["link"] is not None and artifact["link"] != "":
            conn = db.connect_torndb()
            artifact_new = conn.get("select a.* from artifact a join company c on c.id=a.companyId where (c.active is null or c.active !='N') and a.type=%s and \
                                    a.link=%s and c.id!=%s order by c.id desc limit 1", artifact["type"], artifact["link"], companyId)
            conn.close()
            if artifact_new is not None:
                logger.info("find_company_by_artifact 1, %s, %s", artifact_new["type"], artifact_new["link"])
                return artifact_new["companyId"]

        if artifact["domain"] is not None and artifact["domain"] != "":
            conn = db.connect_torndb()
            artifact_new = conn.get("select a.* from artifact a join company c on c.id=a.companyId where (c.active is null or c.active !='N') and a.type=%s and \
                                    a.domain=%s and c.id!=%s order by c.id desc limit 1", artifact["type"], artifact["domain"], companyId)
            conn.close()
            if artifact_new is not None:
                logger.info("find_company_by_artifact 2, %s, %s", artifact_new["type"], artifact_new["domain"])
                return artifact_new["companyId"]
    return None



def find_company_by_short_name(company):
    #产品名相同,则判断
    #1. 地区相同
    #2. 成立日期相同
    #3. member有相同
    #4. 融资事件
    global caflag
    logger.info("find_company_by_short_name")
    matched_company_id = None

    conn = db.connect_torndb()
    members = list(conn.query("select m.* from company_member_rel r join member m on m.id=r.memberId where r.companyId=%s", company["id"]))

    investor_ids = {}
    fundings = list(conn.query("select * from funding where companyId=%s", company["id"]))
    for f in fundings:
        rels = list(conn.query("select * from funding_investor_rel where fundingId=%s", f["id"]))
        for rel in rels:
            investor_ids[rel["investorId"]] = 1

    sns = []
    #add company_alias into checking list
    if caflag is True:
        short_names = list(conn.query("select * from company_alias where type=12020 and companyId=%s", company["id"]))
        for s in short_names:
            sns.append(s["name"])

    if company["name"] not in sns:
        sns.append(company["name"])


    for short_name in sns:
        if short_name is None or short_name.strip() == "":
            continue
        short_name = short_name.strip()

        logger.info("short_name: %s", short_name)
        candidate_company_ids = []
        cs = list(conn.query("select * from company where name=%s and (active is null or active !='N') and id!=%s order by id desc ", short_name, company["id"]))
        for c in cs:
            company_id = c["id"]
            candidate_company_ids.append(company_id)

        #add caflag into checking list
        if caflag is True:
            aliases = list(conn.query("select a.companyId from company_alias a join company c on c.id=a.companyId where (c.active is null or c.active!='N') and a.name=%s and c.id!=%s",short_name, company["id"]))
            for alias in aliases:
                company_id = alias["companyId"]
                if company_id in candidate_company_ids:
                    continue
                candidate_company_ids.append(company_id)

        # sort id
        candidate_company_ids.sort(reverse= True)
        #logger.info("candidate companies id: %s", candidate_company_ids)

        for company_id in candidate_company_ids:
            company_candidate = conn.get("select * from company where id=%s and (active is null or active='Y')", company_id)
            if company_candidate is None:
                continue

            #地区
            location1 = company["locationId"]
            location2 = company_candidate["locationId"]
            if location1 > 0 and location1 == location2:
                matched_company_id = company_id
                logger.info("find_company_by_short_name, location")
                break

            #成立日期
            date1 = company["establishDate"]
            date2 = company_candidate["establishDate"]
            if date1 is not None and date2 is not None and \
                date1.year==date2.year and date1.month==date2.month:
                matched_company_id = company_id
                logger.info("find_company_by_short_name, establish date")
                break

            #member
            members_candidate = list(conn.query("select m.* from company_member_rel r join member m on m.id=r.memberId where r.companyId=%s", company_id))
            for member_candidate in members_candidate:
                member_name = member_candidate["name"]
                #logger.info("member_name: %s", member_name)
                if member_name is None or member_name == "":
                    continue
                if not hz.is_chinese_string(member_name):
                    continue
                for member in members:
                    #logger.info("source_member_name: %s", source_member["name"])
                    if member_name == member["name"]:
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
            fundings_candidate = list(conn.query("select * from funding where companyId=%s",company_id))
            for fc in fundings_candidate:
                rels = list(conn.query("select * from funding_investor_rel where fundingId=%s",fc["id"]))
                for rel in rels:
                    if investor_ids.has_key(rel["investorId"]):
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

if __name__ == "__main__":
    start = 0
    num=0
    cid = 1000000000
    while True:
        conn = db.connect_torndb()
        #companies = list(conn.query("select * from company where (active is null or active='Y') and id <=14502 order by id desc limit %s, 1000", start))
        companies = list(conn.query("select * from company where (active is null or active='Y') and id<%s order by id desc limit 1000", cid))
        if len(companies) == 0:
            break

        #companies = list(conn.query("select * from company where id in (180458) order by id desc"))
        for company in companies:
            cid = company["id"]
            company_id = find_company(company)
            if company_id is None:
                continue
            logger.info("***************************************duplicate id: %s,%s", company["id"], company_id)
            num +=1

            code1 = company["code"]
            company2 = conn.get("select * from company where id=%s",company_id)
            code2 = company2["code"]

            ts =  conn.query("select * from audit_reaggregate_company where type=1 and beforeProcess like %s",
                             "%" + code1 + "%")
            exists = False
            for t in ts:
                if t["beforeProcess"].find(code2)>=0:
                    exists = True
                    break
            if exists:
                continue

            conn.insert("insert audit_reaggregate_company(type,beforeProcess,createTime,processStatus) "
                        "values(1,%s,now(),0)",
                        "%s %s" % (code1, code2))
            # exit()
        conn.close()

        start += 1000
    logger.info("number of companies found: %d", num)