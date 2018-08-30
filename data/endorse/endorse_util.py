# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("endorse_util", stream=True)
logger = loghelper.get_logger("endorse_util")


def is_exist(candidate_companies, company):
    for c in candidate_companies:
        if c["id"] == company["id"]:
            return True
    return False


def find_company_candidate(name, fullname, conn):
    candidate_companies = []
    companies = conn.query("select * from company where name=%s and (active is null or active='Y')",name)
    for c in companies:
        #logger.info("company: %s", c["name"])
        if not is_exist(candidate_companies,c):
            candidate_companies.append(c)

    cas = conn.query("select * from company_alias where name=%s and (active is null or active='Y')",name)
    for ca in cas:
        company = conn.get("select * from company where id=%s", ca["companyId"])
        if company['active'] != 'N':
            #logger.info("company: %s", company["name"])
            if not is_exist(candidate_companies,company):
                candidate_companies.append(company)

    if fullname == u"":
        isCN, isCompany = name_helper.name_check(name)
        #logger.info("isCN: %s, isCompany: %s", isCN, isCompany)
        if isCN and isCompany:
            fullname = name

    if fullname != u"":
        #logger.info("***fullname: %s", fullname)
        companies = conn.query("select * from company where fullname=%s and (active is null or active='Y')", fullname)
        for c in companies:
            #logger.info("company: %s", c["name"])
            if not is_exist(candidate_companies,c):
                candidate_companies.append(c)

        cas = conn.query("select * from corporate_alias where name=%s and (active is null or active='Y')", fullname)
        for ca in cas:
            companies = conn.query("select * from company where corporateId=%s", ca["corporateId"])
            for company in companies:
                if company['active'] != 'N':
                    #logger.info("company: %s", company["name"])
                    if not is_exist(candidate_companies,company):
                        candidate_companies.append(company)

    return candidate_companies