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


def find_company(company):
    #logger.info("Start id: %s, name: %s", company["id"], company["name"])
    #logger.info("short_name: %s", company["name"])
    conn = db.connect_torndb()
    cc = conn.get("select * from company where id=%s", company["id"])
    if cc is None or (cc["active"] is not None and cc["active"] =='N'):
        return None
    candidate_company_ids = []
    cs = list(conn.query("select * from company where name=%s and (active is null or active !='N') and id!=%s order by id desc ", company["name"], company["id"]))
    for c in cs:
        company_id = c["id"]
        candidate_company_ids.append(company_id)

    # sort id
    candidate_company_ids.sort(reverse=True)
    # logger.info("candidate companies id: %s", candidate_company_ids)
    matched_company = None
    for company_id in candidate_company_ids:
        company_candidate = conn.get("select * from company where id=%s and (active is null or active='Y')", company_id)
        if company_candidate is None:
            continue

        if company["fullName"] is not None and company["fullName"].strip() != "" and company["fullName"] == company_candidate["fullName"]:
            matched_company = company_candidate
            logger.info("find_company_by_full_name")
            break

        artifacts = list(conn.query("select * from artifact where companyId=%s and (verify is null or verify='Y') and (active is null or active !='N')", company["id"]))

        for artifact in artifacts:
            flag = find_company_by_artifact(artifact, company_id)
            if flag:
                matched_company = company_candidate
                break

        if matched_company is not None:
            break

    conn.close()
    return matched_company


def find_company_by_artifact(artifact, companyId2):

    if artifact["type"] == 4010:
        #pass
        if artifact["link"] is not None and artifact["link"] != "":
            conn = db.connect_torndb()
            artifact_new = conn.get("select * from artifact where (active is null or active !='N') and (verify is null or verify='Y') and \
                                   type=%s and link=%s and companyId=%s limit 1", artifact["type"], artifact["link"], companyId2)
            conn.close()
            if artifact_new is not None:
                logger.info("find_company_by_artifact 1, %s, %s", artifact_new["type"], artifact_new["link"])
                return True

        if artifact["domain"] is not None and artifact["domain"] != "":
            conn = db.connect_torndb()
            artifact_new = conn.get("select * from artifact where (active is null or active !='N') and (verify is null or verify='Y') and \
                                    type=%s and domain=%s and companyId=%s limit 1", artifact["type"], artifact["domain"], companyId2)
            conn.close()
            if artifact_new is not None:
                logger.info("find_company_by_artifact 2, %s, %s", artifact_new["type"], artifact_new["domain"])
                return True
    return False


if __name__ == "__main__":
    start = 0
    num=0
    cid = 100000000000
    while True:
        conn = db.connect_torndb()
        #companies = list(conn.query("select * from company where (active is null or active='Y') and id <=14502 order by id desc limit %s, 1000", start))
        companies = list(conn.query("select * from company where (active is null or active='Y') and id<%s order by id desc limit 1000", cid))
        if len(companies) == 0:
            break

        #companies = list(conn.query("select * from company where id in (180458) order by id desc"))
        for company in companies:
            #logger.info(company["id"])
            cid = company["id"]
            company_du = find_company(company)
            if company_du is None:
                continue
            logger.info("***************************************duplicate id: %s,%s,    %s, %s", company["id"], company_du["id"], company["code"],company_du["code"])
            num +=1
            merge_company.merge_company(company["id"], company_du["id"])

            # exit()
        conn.close()

        start += 1000
    logger.info("number of companies found: %d", num)