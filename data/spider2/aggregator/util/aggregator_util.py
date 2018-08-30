# -*- coding: utf-8 -*-
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper
import name_helper

#logger
loghelper.init_logger("aggregator_util", stream=True)
logger = loghelper.get_logger("aggregator_util")

# #mongo
# mongo = db.connect_mongo()
# collection_gongshang = mongo.info.gongshang

def find_company(sc_mongo):

    fullNames = []
    if sc_mongo["fullName"] is not None and sc_mongo["fullName"].strip() != "" and \
            sc_mongo["fullName"] not in fullNames:
        fullNames.append(sc_mongo["fullName"])


    company_ids = find_companies_by_full_name_corporate(fullNames)

    if len(company_ids) == 0:
        source_artifacts = sc_mongo["artifacts"]

        company_ids = find_companies_by_artifacts(source_artifacts)

    if len(company_ids) > 0:
        return company_ids[0]
    else:
        return None

def find_companies_by_full_name_corporate(full_names):
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
                    companyIds.append(company["id"])
        conn.close()
    return companyIds


def find_companies_by_artifacts(source_artifacts):
    companyIds = []
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
                            # if int(artifact["companyId"]) > idmax:
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
                                # if int(artifact["companyId"]) > idmax:
                                    companyIds.append(artifact["companyId"])
    return companyIds
