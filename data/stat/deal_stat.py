# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import util
import config
import db
import loghelper

#logger
loghelper.init_logger("deal_stat", stream=True)
logger = loghelper.get_logger("deal_stat")

def updateprocessStatus(id, processStatus):
    conn = db.connect_torndb()
    conn.update("update stat_fund set processStatus=%s where id=%s", processStatus, id)
    conn.close()

def get_organization(id):
    conn = db.connect_torndb()
    organization = conn.get("select * from organization where id=%s and (active is null or active='Y')",id)
    conn.close()
    if organization is None:
        return None
    if organization["name"] is not None and organization["name"].strip() != "":
        return organization["name"]
    else:
        return organization["id"]

def get_users_under_org(id):
    conn = db.connect_torndb()
    user_rels = conn.query("select * from user_organization_rel where organizationId=%s and "
                         "(active is null or active='Y')",id)
    conn.close()
    return user_rels


def get_dinvestment(dealId):
    conn = db.connect_torndb()
    dinvestment = conn.get("select * from deal_investment where dealId=%s and (active is null or active='Y') limit 1",dealId)
    conn.close()
    return dinvestment

def check_userRole(userId):
    flag = False
    conn = db.connect_torndb()
    userroles = conn.query("select * from user_role where userId=%s", userId)
    conn.close()
    if len(userroles) > 0:
        for userrole in userroles:
            if userrole["role"] is None:
                continue
            # if userrole["role"] in [25032,25033,25040,25041]:
            if userrole["role"] in [25032, 25033, 25040]:
                logger.info("UserId: %s, role: %s is right person for calculating", userId, userrole["role"])
                flag = True
                break
    return flag


def get_userStatus(userId):
    conn = db.connect_torndb()
    user = conn.get("select * from user where id=%s",userId)
    conn.close()
    return user

def fulfill_dealflows(deal, deal_flows):
    dfs = []
    dealflows_dict = {}
    # for case of dealId:37185/15618, "19020->19040/double 19050
    maxstatus = 19000
    for dealflow in deal_flows:
        dealflow["createTime"] = dealflow["createTime"] + datetime.timedelta(hours=8)
        if dealflow["status"] is None:
            continue

        if dealflows_dict.has_key(dealflow["status"]) is False:
            dealflows_dict[dealflow["status"]] = dealflow
        else:
            if dealflows_dict[dealflow["status"]]["createTime"] < dealflow["createTime"]:
                dealflows_dict[dealflow["status"]] = dealflow

        if dealflow["status"] > maxstatus:
            maxstatus =  dealflow["status"]
    # logger.info(json.dumps(dealflows_dict, ensure_ascii=False, cls=util.CJsonEncoder))
    # if maxstatus < deal["status"]:
    if deal["status"] is not None:
        maxstatus = deal["status"]

    # deal status 19020 deal flow 1 return:19000/19010
    dstatuses = [status for status in [19050, 19040, 19030, 19020, 19010] if maxstatus >= status]
    modtime = None
    for dstatus in dstatuses:
        if dealflows_dict.has_key(dstatus) is False:
            #todo modifyTime:createTime
            modtime = modtime if modtime is not None else deal["createTime"]
            estimate = 1
        else:
            modtime = dealflows_dict[dstatus]["createTime"]
            estimate = 0

        if dstatus == 19050:
            # check deal_investment time
            dinvestment = get_dinvestment(deal["id"])
            if dinvestment is not None and dinvestment["date"] is not None:
                modtime = dinvestment["date"]

        dfs.append({"status": dstatus, "createTime": modtime, "estimate": estimate})
    return dfs

def insert_deal_flow_organization(deal, deal_flows):
    sql = "insert tmp_deal_flow(dealId,companyId,organizationId,dealStatus,dealflowStatus,dealLastModifyTime,\
                                         dealflowLastModifyTime,declineStatus,estimate) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    conn = db.connect_torndb()

    if deal["modifyTime"] is None:
        deal["modifyTime"] = deal["createTime"]
    #Safe check for dup deals for same company
    dealdata = conn.get("select * from tmp_deal_flow where companyId=%s and organizationId=%s limit 1", deal["companyId"], deal["organizationId"])
    if dealdata is not None:
        logger.info("deal data for company:%s of organization:%s is already existed!!!", deal["companyId"],deal["organizationId"])
        conn.close()
        return

    dfs = fulfill_dealflows(deal, deal_flows)

    for deal_flow in dfs:
        conn.insert(sql, deal["id"], deal["companyId"], deal["organizationId"], deal["status"], deal_flow["status"],
                        deal["modifyTime"],deal_flow["createTime"], deal["declineStatus"], deal_flow["estimate"])
    conn.close()

def extract_dealflow(organizationId):
    conn = db.connect_torndb()
    #Delete old data
    conn.execute("delete from tmp_deal_flow where id>0")
    # Case: status>19000 but declineStatus=18020, calc deal_flow and mark this as one decline case
    # deals = conn.query("select * from deal where organizationId=%s and status>19000 and companyId in (881,30281,5109,97467)", organizationId)
    deals = conn.query("select * from deal where organizationId=%s and status>19000", organizationId)
    for deal in deals:
        # case of deal: 1204 ! status should>19000-> fullfill process?
        # logger.info("deal_id: %s",deal["id"])
        # dealflows = conn.query("select * from deal_flow where dealId=%s and active='Y' and status>19000", deal["id"])
        # dealflows = conn.query("select * from deal_flow where dealId=%s and status>19000", deal["id"])
        # deal_flow data is not changed to mongodb
        mongo = db.connect_mongo()
        collection = mongo.log.deal_log
        dealflows = list(collection.find({"type": 1, "deal_id": int(deal["id"]), "status": {"$gt":19000}}))
        mongo.close()
        insert_deal_flow_organization(deal, dealflows)
    conn.close()

def count_deals_byStatus(statFund):
    result = {}
    sql = "update stat_fund set newDealCnt=%s,activeDealCnt=%s,tsCnt=%s,ddCnt=%s,portfolioCnt=%s,declinedCnt=%s," \
          "declinedFundingCnt=%s, sourceDealCnt=%s where id=%s"
    conn = db.connect_torndb()
    endDate = statFund["endDate"]+datetime.timedelta(days=1)
    for dstatus in [19010,19020,19030,19040,19050]:
        count = conn.get("select count(*) from tmp_deal_flow where organizationId=%s and dealflowStatus=%s \
                         and dealflowLastModifyTime>=%s and dealflowLastModifyTime<%s",statFund["organizationId"], dstatus, statFund["startDate"],
                         endDate)
        result[dstatus] = count["count(*)"]
        # logger.info("%s, %s, %s", endDate, dstatus, result[dstatus])
        # mms = conn.query("select * from tmp_deal_flow where organizationId=%s and dealflowStatus=%s \
        #                  and dealflowLastModifyTime>=%s and dealflowLastModifyTime<%s",statFund["organizationId"], dstatus, statFund["startDate"],
        #                  endDate)
        # logger.info(mms)

    #sourcedeal count for gobi
    count_sd = conn.get("select count(*) from sourcedeal where orgId=%s and createTime>=%s and createTime<=%s",
                        statFund["organizationId"], statFund["startDate"],endDate)

    conn.update(sql, result[19010], result[19020], result[19030], result[19040], result[19050],
                statFund["declinedCnt"], statFund["declinedFundingCnt"], count_sd["count(*)"], statFund["id"])
    conn.close()
    return result

def count_declined(statFund):
    conn = db.connect_torndb()
    dCnt = 0
    dFCnt = 0
    #Only check declinedStatus=18020
    declinedeals = conn.query("select * from deal where organizationId=%s and declineStatus=18020 and status>19000", statFund["organizationId"])
    for declinedeal in declinedeals:
        # todo modifyTime:createTime
        lastDeclineDate = declinedeal["createTime"]
        # df = conn.get("select * from deal_flow where declineStatus=18020 and dealId=%s limit 1",declinedeal["id"])
        mongo = db.connect_mongo()
        collection = mongo.log.deal_log
        df = list(collection.find({"type": 1, "declineStatus": 18020, "deal_id": int(declinedeal["id"])}).sort("_id", pymongo.DESCENDING))
        mongo.close()
        if len(df)>0:
            lastDeclineDate = df[0]["createTime"] + datetime.timedelta(hours=8)
            # lastDeclineDate = df["createTime"]

        if lastDeclineDate is None or lastDeclineDate >= (statFund["endDate"]+datetime.timedelta(days=1)) or lastDeclineDate < statFund["startDate"]:
        # if lastDeclineDate is None or lastDeclineDate < statFund["startDate"]:
            continue
        # logger.info("%s----->%s", lastDeclineDate, statFund["startDate"])
        dCnt += 1
        dfunding = conn.get("select * from funding where companyId=%s and fundingDate>=%s and (active is null or active='Y') "
                            "limit 1",declinedeal["companyId"], lastDeclineDate)

        if dfunding is not None:
            logger.info("Declined Company: %s got funding on %s", declinedeal["companyId"], dfunding["fundingDate"])
            dFCnt += 1
            sql = "insert stat_fund_declined_funding(statFundId,companyId,createTime) values(%s,%s,now())"
            company = conn.get("select * from stat_fund_declined_funding where statFundId=%s and companyId=%s limit 1", statFund["id"],declinedeal["companyId"])
            if company is None:
                conn.insert(sql, statFund["id"],declinedeal["companyId"])
    conn.close()
    return dCnt, dFCnt

def count_deals_byTag(dealResult, statFund):
    sql = "insert stat_fund_figure(statFundId,status,name,cnt,percentage,createTime) values(%s,%s,%s,%s,%s,now())"
    conn = db.connect_torndb()
    conn.execute("delete from stat_fund_figure where statFundId=%s", statFund["id"])

    tags = conn.query("select * from tag where type=11012")
    for dstatus in [19010, 19020, 19030, 19040, 19050]:
        # zero is off
        if dealResult[dstatus] == 0:
            continue
        for tag in tags:
            count = conn.get("select count(*) from tmp_deal_flow dfo join company_tag_rel ctr on dfo.companyId=ctr.companyId \
                             where dfo.dealflowStatus=%s and ctr.tagId=%s and dfo.dealflowLastModifyTime>=%s and dfo.dealflowLastModifyTime<%s",
                             dstatus, tag["id"], statFund["startDate"], statFund["endDate"]+datetime.timedelta(days=1))
            percentage = float(count["count(*)"]) * 100 /float(dealResult[dstatus])
            if percentage>0:
                # logger.info("%s, %s, %s", percentage, count["count(*)"], dealResult[dstatus])
                conn.insert(sql, statFund["id"], dstatus, tag["name"], count["count(*)"],percentage)
    conn.close()

def count_deals_byAssignee(statFund):
    resultUser = {}
    sql = "insert stat_staff(type,startDate,endDate,name,newDealCnt,activeDealCnt,tsCnt,ddCnt,portfolioCnt,\
                            createTime,processStatus,organizationId,userId,sourceDealCnt) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),%s,%s,%s,%s)"
    conn = db.connect_torndb()
    conn.execute("delete from stat_staff where organizationId=%s and type=%s",statFund["organizationId"], statFund["type"])

    for dstatus in [19010, 19020, 19030, 19040, 19050]:
        userCounts = conn.query("select da.userId as userId, count(*) as cnt from tmp_deal_flow dfo join deal_assignee da on dfo.dealId=da.dealId \
                                where dfo.organizationId=%s and dfo.dealflowStatus=%s and dfo.dealflowLastModifyTime>=%s and dfo.dealflowLastModifyTime<%s \
                                and (dfo.estimate is null or dfo.estimate=%s) group by da.userId", statFund["organizationId"], dstatus, statFund["startDate"],
                                statFund["endDate"]+datetime.timedelta(days=1), 0)
        for usercount in userCounts:
            userId = int(usercount["userId"])
            if resultUser.has_key(userId) is False:
                resultUser[userId] = {}
            resultUser[userId][dstatus] = usercount["cnt"]

    # for userId in resultUser:
    for user_rel in get_users_under_org(statFund["organizationId"]):
        userId = int(user_rel["userId"])
        #check user if active=D
        user = get_userStatus(userId)
        if user is None or user["active"] == 'D':
            logger.info("User: %s is not right for organization: %s", userId,statFund["organizationId"])
            continue
        if check_userRole(userId) is False:
            continue
        if resultUser.has_key(userId):
            ruc = resultUser[userId]
            # sourcedeal count for gobi
            count_sd = conn.get("select count(*) from sourcedeal where orgId=%s and createTime>=%s and createTime<=%s and assignee=%s",
                                statFund["organizationId"], statFund["startDate"], statFund["endDate"]+datetime.timedelta(days=1), userId)

            conn.insert(sql, statFund["type"], statFund["startDate"], statFund["endDate"], statFund["name"],
                        ruc.get(19010,0), ruc.get(19020,0), ruc.get(19030,0), ruc.get(19040,0), ruc.get(19050,0),
                        1, statFund["organizationId"], userId, count_sd["count(*)"])
        else:
            count_sd = conn.get(
                "select count(*) from sourcedeal where orgId=%s and createTime>=%s and createTime<=%s and assignee=%s",
                statFund["organizationId"], statFund["startDate"], statFund["endDate"] + datetime.timedelta(days=1),
                userId)

            conn.insert(sql, statFund["type"], statFund["startDate"], statFund["endDate"], statFund["name"],
                        0,0,0,0,0,
                        1, statFund["organizationId"], userId, count_sd["count(*)"])
    conn.close()

    return


def calcDeals(statFundId):
    conn = db.connect_torndb()
    statFund = conn.get("select * from stat_fund where id=%s",statFundId)
    if statFund is None:
        logger.info("Stat_fund not found")
        conn.close()
        return

    logger.info("Calculating : %s", statFund["name"])

    #Calculate declined number
    dCnt, dFCnt = count_declined(statFund)
    statFund["declinedCnt"] = dCnt
    statFund["declinedFundingCnt"] = dFCnt
    logger.info("Declined stat: %s, df: %s", dCnt, dFCnt)

    #add deal data into temporary table:tmp_deal_flow
    extract_dealflow(statFund["organizationId"])

    #Calculate deal Result and save stat_fund
    dealResult = count_deals_byStatus(statFund)
    logger.info(json.dumps(dealResult, ensure_ascii=False, cls=util.CJsonEncoder))
    #
    #Calculate deal figure and save stat_fund_figure
    count_deals_byTag(dealResult, statFund)

    # if statFund["type"] == 1:
        #Calculate deal by staff and save stat_staff only for monthly
    count_deals_byAssignee(statFund)
    #
    updateprocessStatus(statFund["id"], 1)
    logger.info("DONE")

def calcDeclined(statFundId):
    conn = db.connect_torndb()
    statFund = conn.get("select * from stat_fund where id=%s", statFundId)
    if statFund is None:
        logger.info("Stat_fund not found")
        conn.close()
        return

    logger.info("Re-Calculating declined : %s during %s to %s", statFund["name"], str(statFund["startDate"]), str(statFund["endDate"]))

    # Calculate declined number
    dCnt, dFCnt = count_declined(statFund)
    statFund["declinedCnt"] = dCnt
    statFund["declinedFundingCnt"] = dFCnt
    logger.info("Declined stat: %s, df: %s", dCnt, dFCnt)
    sql = "update stat_fund set declinedCnt=%s,declinedFundingCnt=%s where id=%s"
    conn.update(sql,statFund["declinedCnt"], statFund["declinedFundingCnt"], statFund["id"])
    conn.close()


def request_calcDeals(organizationId, startDate, endDate, type, name=None):
    """
    calculate deals during fromDate to endDate.

                fromDate: "YYYY-MM-DD", cannnot be None
                endDate: "YYYY-MM-DD" default: today
                organizationId: id of organization cannot be None
                type: 1. monthly 2. quarterly 3. yearly 0. special
                      4. last 4 week 5. last 12 week 6. last year 7. this year
                name: Default: XXXXX基金_fromDate_endDate
    """
    if startDate is None:
        logger.info("startDate is missing!")
        return
    if endDate is None:
        endDate = datetime.date.today()
    if organizationId is None and get_organization(organizationId) is None:
        logger.info("organization id is incorrect!")
        return

    # create name
    if name is None:
        name = str(get_organization(organizationId)) + "_" + str(startDate) + "_" + str(endDate)
        logger.info("Generating deal report for %s", name)

    conn = db.connect_torndb()
    sql = "insert stat_fund(type,startDate,endDate,name,createTime,organizationId,processStatus) values(%s,%s,%s,%s,now(),%s,%s)"
    if type == 0:
        statFundId = conn.insert(sql, type, startDate, endDate, name, organizationId, 0)
    else:
        #Check if it is already calculated
        statFund = conn.get("select * from stat_fund where organizationId=%s and startDate=%s and endDate=%s and type=%s limit 1",
                            organizationId, startDate, endDate, type)
        if statFund is None:
            statFundId = conn.insert(sql, type, startDate, endDate, name, organizationId, 0)
        else:
            logger.info("Report for %s is existed", name)
            return statFund["id"]
    conn.close()
    return statFundId



if __name__ == "__main__":
    DATE = None
    autoGen = True
    # id = request_calcDeals(1, "2016-12-01", "2017-03-31", 0)
    # calcDeals(114363)
    # calcDeals(114362)
    # exit()
    while True:
        conn = db.connect_torndb()

        dt = datetime.date.today()
        prev_week_first = dt - datetime.timedelta(dt.weekday()) + datetime.timedelta(weeks=-1)
        prev_week_end = prev_week_first + datetime.timedelta(days=6)
        prev_month_end = datetime.date(dt.year, dt.month, 1) - datetime.timedelta(days=1)
        prev_month_first = datetime.date(prev_month_end.year, prev_month_end.month, 1)
        currQuarter = (dt.month - 1) / 3 + 1
        if currQuarter == 1:
            prev_quarter_first = datetime.date(dt.year - 1, 10, 1)
            prev_quarter_end = datetime.date(dt.year - 1, 12, 31)
        else:
            prev_quarter_first = datetime.date(dt.year, 3 * (currQuarter - 1) - 2, 1)
            prev_quarter_end = datetime.date(dt.year, 3 * (currQuarter - 1) + 1, 1) + datetime.timedelta(days=-1)

        #New type 4,5,6,7
        prev_4week_first = dt - datetime.timedelta(dt.weekday()) + datetime.timedelta(weeks=-4)
        prev_4week_end = prev_4week_first + datetime.timedelta(days=27)
        prev_12week_first = dt - datetime.timedelta(dt.weekday()) + datetime.timedelta(weeks=-12)
        prev_12week_end = prev_12week_first + datetime.timedelta(days=83)
        prev_1year_first = datetime.date(dt.year - 1, 1, 1)
        prev_1year_end = datetime.date(dt.year - 1, 12, 31)
        prev_0year_first = datetime.date(dt.year, 1, 1)
        prev_0year_end = dt - datetime.timedelta(days=1)

        if DATE != dt and autoGen is True:
            logger.info("DATE change! Generating report for %s",dt)
            organizations = conn.query("select * from organization where grade=33010")
            for organization in organizations:
                # request_calcDeals(organization["id"], prev_quarter_first, prev_quarter_end, 2)
                # request_calcDeals(organization["id"], prev_month_first, prev_month_end, 1)
                # request_calcDeals(organization["id"], prev_week_first, prev_week_end, 4)
                request_calcDeals(organization["id"], prev_4week_first, prev_4week_end, 4)
                request_calcDeals(organization["id"], prev_12week_first, prev_12week_end, 5)
                request_calcDeals(organization["id"], prev_1year_first, prev_1year_end, 6)
                request_calcDeals(organization["id"], prev_0year_first, prev_0year_end, 7)
            DATE = dt

            sfs = conn.query("select * from stat_fund where processStatus=1 and type in (4,5,6,7) and createTime>%s", dt+datetime.timedelta(days=-10))
            logger.info("%s-----", len(sfs))

            for sf in sfs:
                calcDeclined(sf["id"])

        sfs = conn.query("select * from stat_fund where processStatus=0")
        for sf in sfs:
            calcDeals(sf["id"])
        conn.close()
        logger.info("calculate end")
        time.sleep(60)

