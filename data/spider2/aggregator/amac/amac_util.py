# -*- coding: utf-8 -*-
import os, sys, re, json, time
import datetime
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util, url_helper
import db

#join amac for find_investor_alias_by_fund with active and verify
#todo query for 12010 but not active
#logger
loghelper.init_logger("amac_util", stream=True)
logger = loghelper.get_logger("amac_util")

# investor_alias amacType amacId
# investor_alias_candidate amacType amacId

def get_websit_domains(managerIds):
    domains = []
    mongo = db.connect_mongo()
    collection_manager = mongo.amac.manager
    for managerId in managerIds:
        manager = collection_manager.find_one({"_id": ObjectId(managerId)})
        if manager is not None and manager.has_key("domain") is True \
            and manager["domain"] is not None and manager["domain"].strip() != "" \
            and manager["domain"].strip() not in ["www.com","baidu.com"]:

            if manager["domain"] not in domains: domains.append(manager["domain"])
    mongo.close()
    return domains


def get_legalPerson_names(managerIds, legal=True):
    peopleNames = []
    mongo = db.connect_mongo()
    collection_manager = mongo.amac.manager
    for managerId in managerIds:
        manager = collection_manager.find_one({"_id": ObjectId(managerId)})
        if manager is not None and manager.has_key("managerLegalPerson") is True \
                and manager["managerLegalPerson"] is not None and manager["managerLegalPerson"].strip() != "":

            if manager["managerLegalPerson"] not in peopleNames: peopleNames.append(manager["managerLegalPerson"])

        if legal is False:
            for executive in manager["executives'"]:
                if executive.has_key("name") is True \
                        and executive["name"] is not None and executive["name"].strip() != "":
                    if executive["name"] not in peopleNames: peopleNames.append(executive["name"])

    mongo.close()
    return peopleNames

def make_query():
    pass

def add_mongo(investorId,iaId):
    mongo = db.connect_mongo()
    conn = db.connect_torndb()
    if conn.get('select * from famous_investor where investorId=%s limit 1', investorId) is not None:
        mongo.task.investor.insert_one({
            "processStatus": 0,
            "investorId": int(investorId),
            "taskDate": datetime.datetime.now().strftime("%Y%m%d"),
            "createTime": datetime.datetime.now(),
            "modifyTime": datetime.datetime.now(),
            "type": 'name',
            "relateId": iaId,
            "comments": None,
        })

    mongo.close()
    conn.close()

def add_investor_alias_from_amac(investorId, name, amacMangerId, addFund=False):
    conn = db.connect_torndb()
    sql1 = "insert investor_alias(investorId,name,type,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,now(),now(),-539)"
    sql2 = "insert investor_alias_amac(investorAliasId,investorId,amacType,amacId,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,%s,now(),now(),-539)"
    alias = conn.get("select * from investor_alias where type=12010 and name=%s and investorId=%s "
                     "limit 1", name, investorId)
    aliass = conn.query("select * from investor_alias ia join investor i on i.id=ia.investorid "
                        "where ia.type=12010 and ia.name=%s and (ia.active = 'Y' or ia.active is null) "
                        "and (i.active = 'Y' or i.active is null)",
                        name)
    # if alias is None:
    if len(aliass) == 0 and alias is None:
        logger.info("Find new manger: %s", name)
        iaid = conn.insert(sql1, investorId, name, 12010)
        add_mongo(investorId,int(iaid))
    else:
        # alias = conn.get("select * from investor_alias where type=12010 and name=%s and investorId=%s "
        #                  "limit 1", name, investorId)
        if alias is not None:
            iaid = alias["id"]
        else:
            iaid = None

    if iaid is not None:
        alias_amac = conn.get("select * from investor_alias_amac where investorAliasId=%s and amacType='M' "
                              "limit 1", iaid)
        if alias_amac is None:
            conn.insert(sql2, iaid, investorId,'M',amacMangerId)

    if addFund is True:
        funds = find_amac_funds_by_manager(amacMangerId)
        for fund in funds:
            aliasfs = conn.query("select * from investor_alias ia join investor i on i.id=ia.investorid "
                                 "where ia.type=12010 and ia.name=%s and (ia.active = 'Y' or ia.active is null) "
                                 "and (i.active = 'Y' or i.active is null)",
                                 fund["fundName"])
            aliasf = conn.get(
                "select * from investor_alias where type=12010 and name=%s and investorId=%s "
                "limit 1", fund["fundName"], investorId)
            if len(aliasfs) == 0 and aliasf is None:
                logger.info("Find new fund: %s", fund["fundName"])
                iafid = conn.insert(sql1, investorId, fund["fundName"], 12010)
            else:
                logger.info("Find existed fund: %s", fund["fundName"])
                # aliasf = conn.get(
                #     "select * from investor_alias where type=12010 and name=%s and investorId=%s "
                #     "limit 1", fund["fundName"], investorId)
                if aliasf is not None:
                    iafid = aliasf["id"]
                else:
                    iafid = None

            if iafid is not None:
                aliasf_amac = conn.get("select * from investor_alias_amac where investorAliasId=%s and amacType='F' "
                                       "limit 1", iafid)
                if aliasf_amac is None:
                    conn.insert(sql2, iafid, investorId, 'F', str(fund["_id"]))
                else:
                    pass
                    # logger.info("investor_alias_amac have now!")

    conn.close()

def add_investor_alias_candidate_from_amac(investorId, name, amacMangerId, addFund=False):
    conn = db.connect_torndb()

    sql1 = "insert investor_alias_candidate(investorId,name,type,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,now(),now(),-538)"
    sql2 = "insert investor_alias_candidate_amac(investorAliasCandidateId,investorId,amacType,amacId,createTime,modifyTime) " \
           "values(%s,%s,%s,%s,now(),now())"

    alias = conn.get("select * from investor_alias_candidate where type=12010 and name=%s and investorId=%s "
                     "limit 1", name, investorId)
    if alias is None:
        logger.info("Find new manger: %s", name)
        iaid = conn.insert(sql1, investorId, name, 12010)
    else:
        iaid = alias["id"]

    alias_amac = conn.get("select * from investor_alias_candidate_amac where investorAliasCandidateId=%s and amacType='M' "
                          "limit 1", iaid)
    if alias_amac is None:
        conn.insert(sql2, iaid, investorId, 'M', amacMangerId)

    if addFund is True:
        funds = find_amac_funds_by_manager(amacMangerId)
        for fund in funds:
            aliasfs = conn.query("select * from investor_alias ia join investor i on i.id=ia.investorid "
                                 "where ia.type=12010 and ia.name=%s and (ia.active = 'Y' or ia.active is null) "
                                 "and (i.active = 'Y' or i.active is null)",
                                 fund["fundName"])
            aliasf = conn.get(
                "select * from investor_alias_candidate where type=12010 and name=%s and investorId=%s "
                "limit 1", fund["fundName"], investorId)
            if len(aliasfs) == 0 and aliasf is None:
                logger.info("Find new fund: %s", fund["fundName"])
                iafid = conn.insert(sql1, investorId, fund["fundName"])
            else:
                # aliasf = conn.get(
                #     "select * from investor_alias_candidate where type=12010 and name=%s and investorId=%s "
                #     "limit 1", fund["fundName"], investorId)
                if aliasf is not None:
                    iafid = aliasf["id"]
                else:
                    iafid = None

            if iafid is not None:
                aliasf_amac = conn.get("select * from investor_alias_candidate_amac where investorAliasId=%s and amacType='F' "
                                       "limit 1", iafid)
                if aliasf_amac is None:
                    conn.insert(sql2, iafid, investorId, 'F', str(fund["_id"]))

    conn.close()

def find_amac_manager(managerName):
    mongo = db.connect_mongo()
    collection_manager = mongo.amac.manager
    manager = collection_manager.find_one({"managerName": managerName})
    mongo.close()
    if manager is None: return None
    else: return manager

def find_amac_fund(fundName):
    mongo = db.connect_mongo()
    collection_fund = mongo.amac.fund
    fund = collection_fund.find_one({"fundName": fundName})
    mongo.close()
    if fund is None: return None
    else: return fund

def find_amac_manager_by_id(managerId):
    mongo = db.connect_mongo()
    collection_manager = mongo.amac.manager
    manager = collection_manager.find_one({"_id": ObjectId(managerId)})
    mongo.close()
    if manager is None: return None
    else: return manager

def find_amac_fund_by_id(fundId):
    mongo = db.connect_mongo()
    collection_fund = mongo.amac.fund
    fund = collection_fund.find_one({"_id": ObjectId(fundId)})
    mongo.close()
    if fund is None: return None
    else: return fund

def find_amac_manager_by_domains(domains):
    mongo = db.connect_mongo()
    collection_manager = mongo.amac.manager
    managers = list(collection_manager.find({"domain": {"$in":domains}}))
    mongo.close()
    return managers

def find_amac_manager_by_managerLegalPersons(managerLegalPersons):
    mongo = db.connect_mongo()
    collection_manager = mongo.amac.manager
    managers = list(collection_manager.find({"managerLegalPerson": {"$in": managerLegalPersons}}))
    mongo.close()
    return managers

def find_amac_funds_by_manager(managerId):
    mongo = db.connect_mongo()
    collection_fund = mongo.amac.fund
    funds = collection_fund.find({"managerId": managerId})
    mongo.close()
    return funds


def get_investor_alias_full(investorId):
    pass

def check_amacType(investorId=None):
    conn = db.connect_torndb()
    if investorId is None:
        aliases = conn.query("select * from investor_alias where type=12010 and "
                             "(active is null or active='Y')")
    else:
        aliases = conn.query("select * from investor_alias where type=12010 and "
                             "(active is null or active='Y') and investorId=%s", investorId)

    sql = "insert investor_alias_amac(investorAliasId,investorId,amacType,amacId,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,%s,now(),now(),-537)"
    for alias in aliases:
        manager = find_amac_manager(alias["name"])
        fund = find_amac_fund(alias["name"])
        if alias["name"] is None or alias["name"].strip() == "": continue
        if manager is not None:
            alias_amac = conn.get("select * from investor_alias_amac where investorAliasId=%s and amacType='M' "
                                  "and (active is null or active='Y')", alias["id"])
            if alias_amac is None:
                conn.insert(sql, alias["id"], alias["investorId"],'M', str(manager["_id"]))
        if fund is not None:
            aliasf_amac = conn.get("select * from investor_alias_amac where investorAliasId=%s and amacType='F' "
                                  "and (active is null or active='Y')", alias["id"])
            if aliasf_amac is None:
                conn.insert(sql, alias["id"], alias["investorId"], 'F', str(fund["_id"]))
    conn.close()

def find_investor_alias(investorId):
    conn = db.connect_torndb()
    investor = conn.get("select * from investor where (active is null or active='Y') and id=%s", investorId)
    if investor is None:
        logger.info("investor :%s is not available", investorId)
        conn.close()
        return

    aliases = conn.query("select * from investor_alias where (active is null or active='Y') and "
                         "(verify is null or verify !='N') and investorId=%s", investorId)

    aliases_amac = conn.query("select iaa.* from investor_alias_amac iaa join investor_alias ia on "
                              "iaa.investorAliasId = ia.id  where (ia.active is null or ia.active='Y') and "
                              "(ia.verify is null or ia.verify !='N') and ia.investorId=%s", investorId)

    managerIds = [alias["amacId"] for alias in aliases_amac if alias["amacId"] is not None and alias["amacId"] is not
                   None and alias["amacType"] is not None and alias["amacType"] == 'M']

    managerIds_mysql = [alias["investorAliasId"] for alias in aliases_amac if alias["amacId"] is not None and
                        alias["amacId"] is not None and alias["amacType"] is not None and alias["amacType"] == 'M']

    names = [alias["name"] for alias in aliases if alias["name"] is not None and alias["type"] == 12010]

    manager_names = [alias["name"] for alias in aliases if alias["name"] is not None and alias["type"] == 12010 and
                     alias["id"] in managerIds_mysql]

    logger.info("managerId: %s", ";".join(managerIds))
    logger.info("names: %s", ";".join(names))
    logger.info("manager_names: %s", ";".join(manager_names))

    #find by domains
    InvestorDms = []
    if investor["website"] is not None and investor["website"].strip() != "":
        if investor["domain"] is not None and investor["domain"].strip() != "":
            InvestorDms.append(investor["domain"])
        else:
            type, market, website_domain = url_helper.get_market(investor["website"])
            if type == 4010 and website_domain is not None:
                conn.update("update investor set domain=%s where id=%s", website_domain, investorId)
                InvestorDms.append(website_domain)
    logger.info("investor: %s has self domain: %s", investor["name"], ":".join(InvestorDms))

    if len(managerIds) > 0:
        amac_domains = get_websit_domains(managerIds)
        for amac_domain in amac_domains:
            if amac_domain not in InvestorDms: InvestorDms.append(amac_domain)

    logger.info("investor: %s has total domain: %s", investor["name"], ":".join(InvestorDms))

    if len(InvestorDms) > 0:
        newMangers = find_amac_manager_by_domains(InvestorDms)
        logger.info("investor: %s has found %s amac managers by domain", investor["name"], len(newMangers))
        if len(newMangers) > 0:
            for newManger in newMangers:
                if newManger["managerName"] is not None:
                    if newManger["managerName"] not in names or newManger["managerName"] not in manager_names:
                        logger.info("investor: %s has a new alias: %s", investor["name"], newManger["managerName"])

                        add_investor_alias_from_amac(investorId, newManger["managerName"],
                                                     str(newManger["_id"]), addFund=True)
                        names.append(newManger["managerName"])
                    else:
                        logger.info("investor: %s already has alias: %s", investor["name"], newManger["managerName"])

    #find by names
    # PeopleNames = []
    # if len(managerIds) > 0:
    #     amac_names = get_legalPerson_names(managerIds)
    #     for amac_name in amac_names:
    #         if amac_name not in PeopleNames: PeopleNames.append(amac_name)
    #
    # logger.info("investor: %s has total legalname: %s", investor["name"], ":".join(PeopleNames))
    #
    # if len(PeopleNames) > 0:
    #     newMangers = find_amac_manager_by_managerLegalPersons(PeopleNames)
    #     logger.info("investor: %s has found %s amac managers by legalname", investor["name"], len(newMangers))
    #     if len(newMangers) > 0:
    #         for newManger in newMangers:
    #             if newManger["managerName"] is not None:
    #                 if newManger["managerName"] not in names:
    #                     logger.info("investor: %s has a new alias for can: %s", investor["name"], newManger["managerName"])
    #                     add_investor_alias_candidate_from_amac(investorId, newManger["managerName"],
    #                                                            str(newManger["_id"]), addFund=False)
    #                     names.append(newManger["managerName"])
    #                 else:
    #                     logger.info("investor: %s already has alias: %s", investor["name"], newManger["managerName"])

    conn.close()


def find_investor_alias_by_manager(investorId):
    conn = db.connect_torndb()
    investor = conn.get("select * from investor where (active is null or active='Y') and id=%s", investorId)
    if investor is None:
        logger.info("investor :%s is not available", investorId)
        conn.close()
        return

    aliases_amac = conn.query("select iaa.* from investor_alias_amac iaa join investor_alias ia on "
                              "iaa.investorAliasId = ia.id  where (ia.active is null or ia.active='Y') and "
                              "(ia.verify is null or ia.verify !='N') and ia.investorId=%s", investorId)
    managerIds = [alias["amacId"] for alias in aliases_amac if alias["amacId"] is not None and alias["amacId"] is not
              None and alias["amacType"] is not None and alias["amacType"] == 'M']

    logger.info("managerId: %s", ";".join(managerIds))

    for managerId in managerIds:
        newManger = find_amac_manager_by_id(managerId)
        logger.info("%s -> %s", investorId,newManger["managerName"])
        add_investor_alias_from_amac(investorId, newManger["managerName"],
                                     str(newManger["_id"]), addFund=True)
    conn.close()


def find_investor_alias_by_fund(investorId):
    conn = db.connect_torndb()
    investor = conn.get("select * from investor where (active is null or active='Y') and id=%s", investorId)
    if investor is None:
        logger.info("investor :%s is not available", investorId)
        conn.close()
        return

    aliases_amac = conn.query("select iaa.* from investor_alias_amac iaa join investor_alias ia on "
                              "iaa.investorAliasId = ia.id  where (ia.active is null or ia.active='Y') and "
                              "(ia.verify is null or ia.verify !='N') and ia.investorId=%s", investorId)
    fundIds = [alias["amacId"] for alias in aliases_amac if alias["amacId"] is not None and alias["amacId"] is not
              None and alias["amacType"] is not None and alias["amacType"] == 'F']

    managerIds = []
    for fundId in fundIds:
        fund = find_amac_fund_by_id(fundId)
        if fund is not None and fund["managerId"] is not None and fund["managerId"] not in managerIds:
            managerIds.append(fund["managerId"])

    logger.info("managerId: %s", ";".join(managerIds))

    for managerId in managerIds:
        newManger = find_amac_manager_by_id(managerId)
        logger.info("%s -> %s", investorId,newManger["managerName"])
        add_investor_alias_from_amac(investorId, newManger["managerName"],
                                     str(newManger["_id"]), addFund=True)
    conn.close()

def find_fof_alias_by_fund(investorId):
    conn = db.connect_torndb()
    investor = conn.get("select * from fof where (active is null or active='Y') and id=%s", investorId)
    if investor is None:
        logger.info("investor :%s is not available", investorId)
        conn.close()
        return

    aliases_amac = conn.query("select iaa.* from fof_alias_amac iaa join fof_alias ia on "
                              "iaa.fofAliasId = ia.id  where (ia.active is null or ia.active='Y') and "
                              "(ia.verify is null or ia.verify !='N') and ia.fofId=%s", investorId)
    fundIds = [alias["amacId"] for alias in aliases_amac if alias["amacId"] is not None and alias["amacId"] is not
              None and alias["amacType"] is not None and alias["amacType"] == 'F']

    managerIds = []
    for fundId in fundIds:
        fund = find_amac_fund_by_id(fundId)
        if fund is not None and fund["managerId"] is not None and fund["managerId"] not in managerIds:
            managerIds.append(fund["managerId"])

    logger.info("managerId: %s", ";".join(managerIds))

    for managerId in managerIds:
        newManger = find_amac_manager_by_id(managerId)
        logger.info("%s -> %s", investorId,newManger["managerName"])
        add_fof_alias_from_amac(investorId, newManger["managerName"],
                                     str(newManger["_id"]), addFund=True)
    conn.close()

def find_fof_alias_by_manager(investorId):
    conn = db.connect_torndb()
    investor = conn.get("select * from fof where (active is null or active='Y') and id=%s", investorId)
    if investor is None:
        logger.info("investor :%s is not available", investorId)
        conn.close()
        return

    aliases_amac = conn.query("select iaa.* from fof_alias_amac iaa join fof_alias ia on "
                              "iaa.fofAliasId = ia.id  where (ia.active is null or ia.active='Y') and "
                              "(ia.verify is null or ia.verify !='N') and ia.fofId=%s", investorId)
    managerIds = [alias["amacId"] for alias in aliases_amac if alias["amacId"] is not None and alias["amacId"] is not
              None and alias["amacType"] is not None and alias["amacType"] == 'M']

    logger.info("managerId: %s", ";".join(managerIds))

    for managerId in managerIds:
        newManger = find_amac_manager_by_id(managerId)
        logger.info("%s -> %s", investorId,newManger["managerName"])
        add_fof_alias_from_amac(investorId, newManger["managerName"],
                                     str(newManger["_id"]), addFund=True)
    conn.close()

def find_fof_alias(investorId):
    conn = db.connect_torndb()
    investor = conn.get("select * from fof where (active is null or active='Y') and id=%s", investorId)
    if investor is None:
        logger.info("investor :%s is not available", investorId)
        conn.close()
        return

    aliases = conn.query("select * from fof_alias where (active is null or active='Y') and "
                         "(verify is null or verify !='N') and fofId=%s", investorId)

    aliases_amac = conn.query("select iaa.* from fof_alias_amac iaa join fof_alias ia on "
                              "iaa.fofAliasId = ia.id  where (ia.active is null or ia.active='Y') and "
                              "(ia.verify is null or ia.verify !='N') and ia.fofId=%s", investorId)

    managerIds = [alias["amacId"] for alias in aliases_amac if alias["amacId"] is not None and alias["amacId"] is not
                   None and alias["amacType"] is not None and alias["amacType"] == 'M']

    managerIds_mysql = [alias["fofAliasId"] for alias in aliases_amac if alias["amacId"] is not None and
                        alias["amacId"] is not None and alias["amacType"] is not None and alias["amacType"] == 'M']

    names = [alias["name"] for alias in aliases if alias["name"] is not None and alias["type"] == 12010]

    manager_names = [alias["name"] for alias in aliases if alias["name"] is not None and alias["type"] == 12010 and
                     alias["id"] in managerIds_mysql]

    logger.info("managerId: %s", ";".join(managerIds))
    logger.info("names: %s", ";".join(names))
    logger.info("manager_names: %s", ";".join(manager_names))

    #find by domains
    InvestorDms = []
    if investor["website"] is not None and investor["website"].strip() != "":
        if investor["domain"] is not None and investor["domain"].strip() != "":
            InvestorDms.append(investor["domain"])
        else:
            type, market, website_domain = url_helper.get_market(investor["website"])
            if type == 4010 and website_domain is not None:
                conn.update("update investor set domain=%s where id=%s", website_domain, investorId)
                InvestorDms.append(website_domain)
    logger.info("investor: %s has self domain: %s", investor["name"], ":".join(InvestorDms))

    if len(managerIds) > 0:
        amac_domains = get_websit_domains(managerIds)
        for amac_domain in amac_domains:
            if amac_domain not in InvestorDms: InvestorDms.append(amac_domain)

    logger.info("investor: %s has total domain: %s", investor["name"], ":".join(InvestorDms))

    if len(InvestorDms) > 0:
        newMangers = find_amac_manager_by_domains(InvestorDms)
        logger.info("investor: %s has found %s amac managers by domain", investor["name"], len(newMangers))
        if len(newMangers) > 0:
            for newManger in newMangers:
                if newManger["managerName"] is not None:
                    if newManger["managerName"] not in names or newManger["managerName"] not in manager_names:
                        logger.info("investor: %s has a new alias: %s", investor["name"], newManger["managerName"])

                        add_fof_alias_from_amac(investorId, newManger["managerName"],
                                                     str(newManger["_id"]), addFund=True)
                        names.append(newManger["managerName"])
                    else:
                        logger.info("investor: %s already has alias: %s", investor["name"], newManger["managerName"])


def add_fof_alias_from_amac(investorId, name, amacMangerId, addFund=False):
    conn = db.connect_torndb()
    sql1 = "insert fof_alias(fofId,name,type,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,now(),now(),-539)"
    sql2 = "insert fof_alias_amac(fofAliasId,fofId,amacType,amacId,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,%s,now(),now(),-539)"
    alias = conn.get("select * from fof_alias where type=12010 and name=%s and fofId=%s "
                     "limit 1", name, investorId)
    if alias is None:
        logger.info("Find new manger: %s", name)
        iaid = conn.insert(sql1, investorId, name, 12010)
    else:
        iaid = alias["id"]

    alias_amac = conn.get("select * from fof_alias_amac where fofAliasId=%s and amacType='M' "
                          "limit 1", iaid)
    if alias_amac is None:
        conn.insert(sql2, iaid, investorId,'M',amacMangerId)

    if addFund is True:
        funds = find_amac_funds_by_manager(amacMangerId)
        for fund in funds:
            aliasf = conn.get("select * from fof_alias where type=12010 and name=%s and fofId=%s "
                              "limit 1", fund["fundName"], investorId)
            if aliasf is None:
                logger.info("Find new fund: %s", fund["fundName"])
                iafid = conn.insert(sql1, investorId, fund["fundName"], 12010)
            else:
                logger.info("Find existed fund: %s", fund["fundName"])
                iafid = aliasf["id"]

            aliasf_amac = conn.get("select * from fof_alias_amac where fofAliasId=%s and amacType='F' "
                                   "limit 1", iafid)
            if aliasf_amac is None:
                conn.insert(sql2, iafid, investorId, 'F', str(fund["_id"]))
            else:
                pass
                # logger.info("fof_alias_amac have now!")

    conn.close()


def check_amacType_fof(investorId=None):
    conn = db.connect_torndb()
    if investorId is None:
        aliases = conn.query("select * from fof_alias where type=12010 and "
                             "(active is null or active='Y')")
    else:
        aliases = conn.query("select * from fof_alias where type=12010 and "
                             "(active is null or active='Y') and fofId=%s", investorId)

    sql = "insert fof_alias_amac(fofAliasId,fofId,amacType,amacId,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,%s,now(),now(),-537)"
    for alias in aliases:
        manager = find_amac_manager(alias["name"])
        fund = find_amac_fund(alias["name"])
        if alias["name"] is None or alias["name"].strip() == "": continue
        if manager is not None:
            alias_amac = conn.get("select * from fof_alias_amac where fofAliasId=%s and amacType='M' "
                                  "and (active is null or active='Y')", alias["id"])
            if alias_amac is None:
                conn.insert(sql, alias["id"], alias["fofId"],'M', str(manager["_id"]))
        if fund is not None:
            aliasf_amac = conn.get("select * from fof_alias_amac where fofAliasId=%s and amacType='F' "
                                  "and (active is null or active='Y')", alias["id"])
            if aliasf_amac is None:
                conn.insert(sql, alias["id"], alias["fofId"], 'F', str(fund["_id"]))
    conn.close()




def fund_process_0(investorFundId):
    conn = db.connect_torndb_proxy()
    investor_fund = conn.get("select * from investor_fund where id=%s and (active is null or active='Y') and "
                             "processStatus=0", investorFundId)
    if investor_fund is None:
        conn.close()
        return
    name = investor_fund["fullName"]

    logger.info("start check 0: %s", investor_fund["fullName"])
    mongo = db.connect_mongo()
    collection_gongshang_name = mongo.info.gongshang_name
    if collection_gongshang_name.find_one({'name': name}) is None:
        logger.info("insert gongshang_name:%s", name)
        collection_gongshang_name.insert({"name": name, "type": 5, "lastCheckTime": None})
    else:
        collection_gongshang_name.update_one({"name": name}, {'$set': {"lastCheckTime": None}})
    mongo.close()
    conn.update("update investor_fund set processStatus=1, modifyTime=now() where id=%s", investorFundId)
    conn.close()


def fund_process_1(investorFundId):
    conn = db.connect_torndb_proxy()
    investor_fund = conn.get("select * from investor_fund where id=%s and (active is null or active='Y') and "
                             "processStatus=1", investorFundId)
    if investor_fund is None:
        conn.close()
        return
    name = investor_fund["fullName"]

    logger.info("start check 1: %s", investor_fund["fullName"])
    mongo = db.connect_mongo()
    collection_gongshang_name = mongo.info.gongshang_name
    collection_raw = mongo.raw.projectdata
    item = collection_gongshang_name.find_one({'name': name})
    if item is None:
        logger.info("insert gongshang_name:%s", name)
        collection_gongshang_name.insert({"name": name, "type": 5, "lastCheckTime": None})
    else:
        if item["lastCheckTime"] is None:
            logger.info("%s still waiting gongshang data, go to 1", name)
            pass
        else:
            item_raw = collection_raw.find_one({"source":13093,"type":36008,"key":name})
            if item_raw is None:
                logger.info("%s has no gongshang data, go to 3", name)
                conn.update("update investor_fund set processStatus=3, modifyTime=now() where id=%s", investorFundId)
            else:
                if item_raw.has_key("processed") and item_raw["processed"] is True:
                    logger.info("%s has new gongshang data, go to 2", name)
                    conn.update("update investor_fund set processStatus=2, modifyTime=now() where id=%s", investorFundId)
                else:
                    logger.info("%s still waiting gongshang parser, go to 1", name)
    mongo.close()
    conn.close()


def fund_process_2(investorFundId):
    conn = db.connect_torndb_proxy()
    investor_fund = conn.get("select * from investor_fund where id=%s and (active is null or active='Y') and "
                             "processStatus=2", investorFundId)
    if investor_fund is None:
        conn.close()
        return
    name = investor_fund["fullName"]

    logger.info("start check 2: %s", investor_fund["fullName"])
    mongo = db.connect_mongo()
    collection_gongshang = mongo.info.gongshang
    item = collection_gongshang.find_one({'name': name})
    if item is None:
        logger.info("No gonghshang data, something wrong checking :%s", name)
        #todo 邮件

    else:
        if item.has_key("legalPersonName") and item["legalPersonName"].strip() not in ["", "-", "—"]:

            ln = item["legalPersonName"].replace("(", "（").replace(")", "）")
            lnn = ln.split("（委派")[0].strip()
            memo = lnn + "是" + name + "的法人"
            investor_gp_id = add_name_investor_gp(lnn, investor_fund["investorId"], memo)
            conn.update("update investor_fund set investorGpId=%s where id=%s", investor_gp_id, investorFundId)
            logger.info("%s has gp data-%s, go to 3", name, lnn)
        else:
            logger.info("%s has nononono gp data-%s, go to 3", name, item["legalPersonName"])
        conn.update("update investor_fund set processStatus=3, modifyTime=now() where id=%s", investorFundId)
    mongo.close()
    conn.close()


def generalp_process_0(investorGpId):
    conn = db.connect_torndb_proxy()
    investor_gp = conn.get("select * from investor_gp where id=%s and (active is null or active='Y') and "
                             "processStatus=0", investorGpId)
    if investor_gp is None:
        conn.close()
        return
    name = investor_gp["fullName"]

    logger.info("start check 0: %s", investor_gp["fullName"])
    mongo = db.connect_mongo()
    collection_gongshang_name = mongo.info.gongshang_name
    if collection_gongshang_name.find_one({'name': name}) is None:
        logger.info("insert gongshang_name:%s", name)
        collection_gongshang_name.insert({"name": name, "type": 5, "lastCheckTime": None})
    else:
        collection_gongshang_name.update_one({"name": name}, {'$set': {"lastCheckTime": None}})
    mongo.close()

    if investor_gp["amacManagerId"] is not None:
        funds = find_amac_funds_by_manager(investor_gp["amacManagerId"])
        for fund in funds:
            memo = fund["fundName"] + "是" + name + "在amac中下属基金"
            logger.info(memo)
            add_name_investor_fund(fund["fundName"],investor_gp["investorId"], memo)
    conn.update("update investor_gp set processStatus=1, modifyTime=now() where id=%s", investorGpId)
    conn.close()


def generalp_process_1(investorGpId):
    conn = db.connect_torndb_proxy()
    investor_gp = conn.get("select * from investor_gp where id=%s and (active is null or active='Y') and "
                             "processStatus=1", investorGpId)
    if investor_gp is None:
        conn.close()
        return
    name = investor_gp["fullName"]

    logger.info("start check 1: %s", investor_gp["fullName"])
    mongo = db.connect_mongo()
    collection_gongshang_name = mongo.info.gongshang_name
    collection_raw = mongo.raw.projectdata
    item = collection_gongshang_name.find_one({'name': name})
    if item is None:
        logger.info("insert gongshang_name:%s", name)
        collection_gongshang_name.insert({"name": name, "type": 5, "lastCheckTime": None})
    else:
        if item["lastCheckTime"] is None:
            logger.info("%s still waiting gongshang data, go to 1", name)
            pass
        else:
            item_raw = collection_raw.find_one({"source":13093,"type":36008,"key":name})
            if item_raw is None:
                logger.info("%s has no gongshang data, go to 3", name)
                conn.update("update investor_gp set processStatus=3, modifyTime=now() where id=%s", investorGpId)
            else:
                if item_raw.has_key("processed") and item_raw["processed"] is True:
                    logger.info("%s has new gongshang data, go to 2", name)
                    conn.update("update investor_gp set processStatus=2, modifyTime=now() where id=%s", investorGpId)
                else:
                    logger.info("%s still waiting gongshang parser, go to 1", name)
    mongo.close()
    conn.close()


def generalp_process_2(investorGpId):
    conn = db.connect_torndb_proxy()
    investor_gp = conn.get("select * from investor_gp where id=%s and (active is null or active='Y') and "
                             "processStatus=2", investorGpId)
    if investor_gp is None:
        conn.close()
        return
    name = investor_gp["fullName"]

    logger.info("start check 2: %s", investor_gp["fullName"])
    mongo = db.connect_mongo()
    collection_gongshang = mongo.info.gongshang
    item = collection_gongshang.find_one({'name': name})
    if item is None:
        logger.info("No gonghshang data, something wrong checking :%s", name)
        # todo 邮件

    else:
        if item.has_key("investors") and isinstance(item["investors"], list) and len(item["investors"]) == 1:

            ln = item["investors"][0]["name"].replace("(", "（").replace(")", "）").strip()
            if ln.find("公司") >=0 or ln.find("企业") >=0 or ln.find("合伙") >=0:
                lnn = ln.split("（委派")[0]
                memo = lnn + "是" + name + "的唯一股东"
                add_name_investor_gp(lnn, investor_gp["investorId"], memo)

                logger.info("%s has gp data-%s, go to 3", name, lnn)
            else:
                logger.info("%s has nononono gp data-%s, go to 3", name, item["investors"][0]["name"])


        conn.update("update investor_gp set processStatus=3, modifyTime=now() where id=%s", investorGpId)
    mongo.close()
    conn.close()



def add_name_investor_gp(name, investorId, memo):
    igid = None
    conn = db.connect_torndb()
    sql1 = "insert investor_gp(investorId,fullName,amacManagerId,memo,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,%s,now(),now(),-499)"

    manager = find_amac_manager(name)
    if manager is None:
        amacManagerId = None
    else:
        amacManagerId = str(manager["_id"])

    alias = conn.get("select * from investor_gp where fullName=%s and investorId=%s "
                     "limit 1", name, investorId)
    if alias is None:
        igid = conn.insert(sql1, investorId, name, amacManagerId, memo)
    else:
        igid = alias["id"]

    conn.close()
    return  igid

def add_name_investor_fund(name, investorId, memo):
    ifid = None
    conn = db.connect_torndb()
    sql1 = "insert investor_fund(investorId,fullName,amacFundId,memo,createTime,modifyTime,createUser) " \
           "values(%s,%s,%s,%s,now(),now(),-498)"

    fund = find_amac_fund(name)
    if fund is None:
        amacFundId = None
    else:
        amacFundId = str(fund["_id"])

    alias = conn.get("select * from investor_fund where fullName=%s and investorId=%s "
                     "limit 1", name, investorId)
    if alias is None:
        ifid = conn.insert(sql1, investorId, name, amacFundId, memo)
    else:
        ifid = alias['id']

    conn.close()
    return ifid
