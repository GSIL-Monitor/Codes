# -*- coding: utf-8 -*-
import os, sys, time
import datetime
import json
import pymongo
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util

#logger
loghelper.init_logger("check_diff", stream=True)
logger = loghelper.get_logger("check_diff")



def insert_new_company(item, download_crawler):
    sourceCompanyId = parser_mysql_util.save_company(item["source_company"], download_crawler)
    set_diff("source_company", "create", sourceCompanyId)
    if item.has_key("source_artifact"):
        for sartifact in item["source_artifact"]:
            said = parser_mysql_util.save_artifact(sourceCompanyId, sartifact)
            set_diff("source_artifact", "create", said)
    if item.has_key("source_company_name"):
        for scompanyname in item["source_company_name"]:
            scnid = parser_mysql_util.save_company_name(sourceCompanyId, scompanyname)
            set_diff("source_company_name", "create", scnid)
    if item.has_key("source_mainbeianhao"):
        for smainbeianhao in item["source_mainbeianhao"]:
            parser_mysql_util.save_mainbeianhao(sourceCompanyId, smainbeianhao)
    if item.has_key("source_funding"):
        for sfunding in item["source_funding"]:
            sfid = parser_mysql_util.save_funding(sourceCompanyId, sfunding, download_crawler)
            set_diff("source_funding", "create", sfid)
    if item.has_key("source_company_member"):
        for scmember in item["source_company_member"]:
            scmrid = parser_mysql_util.save_company_member_rel(sourceCompanyId, scmember, download_crawler)
            set_diff("source_company_member_rel", "create", scmrid)
    return sourceCompanyId

DIFF = {
    "create": 1,
    "update": 2,
    "delete": 3
}

def check_item(source_mongo, source_mysql, items):
    for item in items:
        if source_mongo[item] is None:
            continue
        try:
            if source_mysql[item] is None and source_mongo[item].strip() != "":
                return "update"
            if source_mongo[item].strip() != source_mysql[item].strip():
                return "update"
        except:
            if source_mysql[item] is None and source_mongo[item] != "":
                return "update"
            if source_mongo[item] != source_mysql[item]:
                return "update"
    return None

def set_diff(table, diff, row_id, diff_position=None):
    conn = db.connect_torndb()
    diff_value = DIFF.get(diff)
    if diff_value is not None:
        if diff_position is None:
            sql = "update " + table + " set diffResult=%s where id=%s"
            conn.update(sql, diff_value, row_id)
        else:
            sql = "update " + table + " set diffResult=%s, diffPosition=%s where id=%s"
            conn.update(sql, diff_value, diff_position, row_id)
    conn.close()

def check_diff(source, sourceId, download_crawler):
    mongo = db.connect_mongo()
    collection_company = mongo.source.company
    sourcecompany = collection_company.find_one({"source": source, "sourceId": sourceId})
    mongo.close()
    if sourcecompany is None:
        return None

    if sourcecompany.has_key("source_company") is False:
        return None

    conn = db.connect_torndb()

    source_company = conn.get("select * from source_company where source=%s and sourceId=%s limit 1", source, sourceId)

    # Check new company <-> add all data into mysql and waitfor review
    if source_company is None:
        logger.info("Insert New source_company for source: %s, sourceId: %s", source, sourceId)
        new_sourceCompanyId = insert_new_company(sourcecompany, download_crawler)
        conn.close()
        return new_sourceCompanyId

    sourceCompanyId = source_company["id"]

    update = None
    #Check basic info for "update"
    if sourcecompany.has_key("source_company"):
        scompany = sourcecompany["source_company"]
        diff = check_item(scompany, source_company, ["name", "fullName", "description", "companyStatus", "locationId", "establishDate"])
        if diff is not None:
            logger.info("Basic info changed for source: %s, sourceId: %s", source, sourceId)
            set_diff("source_company", diff, source_company["id"])
            update = diff

    #Check artifact
    if sourcecompany.has_key("source_artifact"):
        sartifacts = sourcecompany["source_artifact"]
        sa_position = 0
        sourceartifactIds = []
        source_artifacts = conn.query("select * from source_artifact where sourceCompanyId=%s", sourceCompanyId)
        # Check artifact for "create" or "update"
        for sartifact in sartifacts:
            # if sartifact.has_key("active") is False:
            #     continue
            #alive
            # if sartifact["alive"] == 'N':
            #     continue
            source_artifact = None
            if sartifact["domain"] is not None:
                source_artifact = conn.get("select * from source_artifact where type=%s and domain=%s and sourceCompanyId =%s limit 1",
                                            sartifact["type"], sartifact["domain"], sourceCompanyId)
            if source_artifact is None and sartifact["type"] in [4010, 4020, 4030]:
                source_artifact = conn.get("select * from source_artifact where type=%s and link=%s and sourceCompanyId =%s limit 1",
                                            sartifact["type"], sartifact["link"], sourceCompanyId)

            if source_artifact is None:
                #New artifact
                logger.info("New source_artifact found under sc:%s : %s, %s", sourceCompanyId, sartifact["name"], sartifact["link"])
                said = parser_mysql_util.save_artifact(sourceCompanyId, sartifact)
                set_diff("source_artifact", "create", said)
                update = "create"
            else:
                sourceartifactIds.append(source_artifact["id"])

                if source_artifact["artifactStatus"] is None:
                    # Todo
                    continue

                #source_artifact is accessible
                if source_artifact["artifactStatus"] != 11:
                    if sartifact["artifactStatus"] is not None and sartifact["artifactStatus"] == 11:
                        # artifact now not accessible but alive before, now mark
                        logger.info("Inactive source_artifact under sc:%s : %s, %s", sourceCompanyId, sartifact["name"], sartifact["link"])
                        set_diff("source_artifact", "delete", source_artifact["id"])
                        update = "delete"
                    else:
                        # Same artifact, no action
                        pass
                # source_artifact is not accessible
                else:
                    if sartifact["artifactStatus"] is not None and sartifact["artifactStatus"] != 11:
                        # artifact now accessible, mark
                        logger.info("Reactive source_artifact under sc:%s : %s, %s", sourceCompanyId, sartifact["name"], sartifact["link"])
                        set_diff("source_artifact", "update", source_artifact["id"], sa_position)
                        update ="update"

            sa_position += 1

        #Check artifact for "disappear"
        # for sartifact in sartifacts:
        #     if sartifact.has_key("active") is False:
        #         continue
        #     if sartifact["active"] == 'N':
        #         source_artifact = conn.get("select * from source_artifact where type=%s and domain=%s and sourceCompanyId =%s limit 1",
        #                                     sartifact["type"], sartifact["domain"], sourceCompanyId)
        #         if source_artifact is not None and (source_artifact["active"] is None or source_artifact["active"] == "Y"):
        #             #Inactive artifact
        #             logger.info("Inactive source_artifact found under sc:%s : %s, %s", sourceCompanyId, sartifact["name"], sartifact["link"])
        #             set_diff("source_artifact", "delete", source_artifact["id"])
        #             update = "delete"

        # Check source_artifact has artifacts which do not existed in sartifact(mongo expand)
        for sourceArtifact in source_artifacts:
            if sourceArtifact["id"] not in sourceartifactIds:
                logger.info("Recent expand not found source_artifact under sc:%s : %s, %s", sourceCompanyId, sourceArtifact["name"], sourceArtifact["link"])
                set_diff("source_artifact", "delete", sourceArtifact["id"])
                update = "delete"

    #Check source_company_name
    if sourcecompany.has_key("source_company_name"):
        scnames = sourcecompany["source_company_name"]
        sourcecompanynameIds = []
        source_company_names = conn.query("select * from source_company_name where sourceCompanyId=%s", sourceCompanyId)
        for scname in scnames:
            source_company_name = conn.get("select * from source_company_name where sourceCompanyId=%s and name=%s limit 1",
                                            sourceCompanyId, scname["name"])
            if source_company_name is None:
                logger.info("New source_company_name under sc: %s : %s", sourceCompanyId, scname["name"])
                scnid = parser_mysql_util.save_company_name(sourceCompanyId, scname)
                set_diff("source_company_name", "create", scnid)
                update = "create"
            else:
                sourcecompanynameIds.append(source_company_name["id"])

        # Check source_company_name has names which do not existed in scname(mongo expand)
        for sourceCompanyName in source_company_names:
            if sourceCompanyName["id"] not in sourcecompanynameIds:
                logger.info("Recent expand not found source_company_name under sc:%s : %s", sourceCompanyId, sourceCompanyName["name"])
                set_diff("source_company_name", "delete", sourceCompanyName["id"])
                update = "delete"


    #Check source_funding
    if sourcecompany.has_key("source_funding"):
        sfundings = sourcecompany["source_funding"]
        sf_position = 0
        # Check funding for "create" or "update"
        for sfunding in sfundings:
            source_funding = conn.get("select * from source_funding where round=%s and sourceCompanyId =%s limit 1",
                                        sfunding["round"], sourceCompanyId)
            if source_funding is None:
                # New Funding
                logger.info("New source_funding found under sc:%s : round: %s, %s", sourceCompanyId, sfunding["round"],sfunding["investment"])
                sfid = parser_mysql_util.save_funding(sourceCompanyId, sfunding, download_crawler)
                set_diff("source_funding", "create", sfid)
                update = "create"
            else:
                #Update funding
                diff = check_item(sfunding, source_funding, ["currency", "investment", "precise", "fundingDate"])
                if diff is not None:
                    logger.info("Update source_funding found under sc:%s : %s, %s", sourceCompanyId, sfunding["round"],sfunding["investment"])
                    set_diff("source_funding", diff, source_funding["id"], sf_position)
                    update = diff
                else:
                    source_funding_investor_rel = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s", source_funding["id"])

                    if len(source_funding_investor_rel) != len(sfunding["_investorIds"]):
                        #Update investors
                        logger.info("Update source_funding by diff investors under sc:%s : round: %s", sourceCompanyId, sfunding["round"])
                        set_diff("source_funding", "update", source_funding["id"], sf_position)
                        update = "update"

                    elif len(sfunding["_investorIds"]) > 0:
                        mongo = db.connect_mongo()
                        collection_investor = mongo.source.investor
                        for sinvestorId in sfunding["_investorIds"]:
                            sinvestor = collection_investor.find_one({"_id": sinvestorId})

                            if sinvestor is None:
                                continue
                            #Itjuzi sometimes do not provide investor id
                            if sinvestor["sourceId"] is not None:
                                source_investor = conn.get("select i.* from source_funding_investor_rel r join source_investor i on r.sourceInvestorId=i.id "
                                                         "where r.sourceFundingId=%s and i.sourceId=%s limit 1", source_funding["id"], sinvestor["sourceId"])
                            else:
                                source_investor = conn.get("select i.* from source_funding_investor_rel r join source_investor i on r.sourceInvestorId=i.id "
                                                         "where r.sourceFundingId=%s and i.name=%s limit 1", source_funding["id"],sinvestor["name"])

                            if source_investor is None:
                                #Update investors - new added investor
                                logger.info("Update source_funding by new investor under sc:%s : round: %s", sourceCompanyId, sfunding["round"])
                                set_diff("source_funding", "update", source_funding["id"], sf_position)
                                update = "update"
                            # else:
                            #     # Update investors - update investor info
                            #     diff = check_item(sinvestor, source_investor, ["name", "website", "desription"])
                            #     if diff is not None:
                            #         logger.info("Update source_funding by update investor info under sc:%s : round: %s", sourceCompanyId, sfunding["round"])
                            #         set_diff("source_funding", diff, source_funding["id"], sf_position)
                            #         update = diff
                        mongo.close()
            sf_position += 1
        # Check funding for "disappear"
        # if round is found in mysql but not existed in mongo, add diff for "delete"?


    #Check source_member
    if sourcecompany.has_key("source_company_member"):
        company_members = sourcecompany["source_company_member"]
        cm_position = 0
        #Check company_member for "create" or "update"
        for company_member in company_members:
            if company_member["_memberId"] is None:
                continue
            mongo = db.connect_mongo()
            collection_member = mongo.source.member
            smember = collection_member.find_one({"_id": company_member["_memberId"]})
            mongo.close()
            if smember is None:
                continue

            if smember["sourceId"] is not None:
                source_member = conn.get("select m.*,r.position,r.type,r.id as relId from source_company_member_rel r join source_member m on r.sourceMemberId=m.id "
                                         "where r.sourceCompanyId=%s and m.sourceId=%s limit 1", sourceCompanyId, smember["sourceId"])
            else:
                source_member = conn.get("select m.*,r.position,r.type,r.id as relId from source_company_member_rel r join source_member m on r.sourceMemberId=m.id "
                                         "where r.sourceCompanyId=%s and m.name=%s limit 1", sourceCompanyId, smember["name"])
            if source_member is None:
                # New Member
                logger.info("New source_member found under sc:%s : %s, %s", sourceCompanyId, smember["name"], company_member["position"])
                scmrid = parser_mysql_util.save_company_member_rel(sourceCompanyId, company_member, download_crawler)
                set_diff("source_company_member_rel", "create", scmrid)
                update = "create"
            else:
                #Update Members
                smember["position"] = company_member["position"]
                smember["type"] = company_member["type"]
                # logger.info(smember)
                diff = check_item(smember, source_member, ["position", "type", "name", "education", "work", "description"])
                if diff is not None:
                    logger.info("Update source_member under sc:%s : %s, %s", sourceCompanyId, smember["name"], company_member["position"])
                    set_diff("source_company_member_rel", diff, source_member["relId"], cm_position)
                    update = diff
            cm_position += 1

    conn.close()
    if update is not None:
        return sourceCompanyId
    else:
        return None


if __name__ == "__main__":
    check_diff()
