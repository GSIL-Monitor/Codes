# -*- coding: utf-8 -*-
import os, sys
import datetime
import xlrd
import traceback
import re
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("pencilnews_import", stream=True)
logger = loghelper.get_logger("pencilnews_import")

SOURCE=13800
FA_ADVISOR_ID = 18

def is_exist(candidate_companies, company):
    for c in candidate_companies:
        if c["id"] == company["id"]:
            return True

    return False

def find_related_news(project_name, founder_name):
    rexExp1 = re.compile('.*%s.*' % project_name, re.IGNORECASE)
    rexExp2 = re.compile('.*%s.*' % founder_name, re.IGNORECASE)
    mongo = db.connect_mongo()
    ns = list(mongo.article.news.find({"source":13800, "contents.content":rexExp1, "contents.content":rexExp2}).sort("_id",pymongo.DESCENDING).limit(10))
    if len(ns) == 0:
        ns = list(mongo.article.news.find({"source":13800, "contents.content":rexExp1}).sort("_id",pymongo.DESCENDING).limit(10))
    if len(ns) == 0:
        ns = list(mongo.article.news.find({"source":13800, "contents.content":rexExp2}).sort("_id",pymongo.DESCENDING).limit(10))
    mongo.close()

    return ns

def find_company_candidate(name, fullname):
    conn = db.connect_torndb()
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

        cas = conn.query("select * from company_alias where name=%s and (active is null or active='Y')", fullname)
        for ca in cas:
            company = conn.get("select * from company where id=%s", ca["companyId"])
            if company['active'] != 'N':
                #logger.info("company: %s", company["name"])
                if not is_exist(candidate_companies,company):
                    candidate_companies.append(company)

    conn.close()

    return candidate_companies


def save(data):
    conn = db.connect_torndb()
    cfa = conn.get("select * from company_fa where source=%s and sourceId=%s", SOURCE, data["sourceId"])
    if cfa is None:
        code = data["code"]
        company_id = None
        processStatus=0
        if code != "":
            company = conn.get("select * from company where code=%s", code)
            if company:
                company_id = company["id"]
                processStatus=1

        company_fa_id = conn.insert("insert company_fa("
                                    "name,companyId,source,sourceId,publishDate,"
                                    "productDesc, modelDesc, operationDesc, planDesc,"
                                    "founder, founderDesc, field, investmentHistory, investorHistory,"
                                    "processStatus,createTime, modifyTime, faId"
                                    ") values("
                                    "%s,%s,%s,%s,%s,"
                                    "%s,%s,%s,%s,"
                                    "%s,%s,%s,%s,%s,"
                                    "%s,now(),now(), 7)",
                                    data["name"], company_id, SOURCE, data["sourceId"], data["publishDate"],
                                    data["productDesc"], data["modelDesc"], data["operationDesc"], data["planDesc"],
                                    data["founder"], data["founderDesc"], data["field"], data["investmentHistory"], data["investorHistory"],
                                    processStatus
                                    )
        #company_fa_candidate
        candidate_companies = data["candidate_companies"]
        for c in candidate_companies:
            conn.insert("insert company_fa_candidate(companyFaId, companyId) values(%s,%s)",
                        company_fa_id, c["id"])

        #company_fa_news_candidate
        candidate_news = data["candidate_news"]
        for c in candidate_news:
            conn.insert("insert company_fa_news_candidate(companyFaId, newsId) values(%s,%s)",
                        company_fa_id, c["_id"])

        #fa_advisor
        conn.insert("insert company_fa_advisor_rel(companyFaId, faAdvisorId,createTime) values(%s,%s,now())",
                    company_fa_id, FA_ADVISOR_ID)
    else:
        company_fa_id = cfa["id"]
    conn.close()


def process(table):

    nrows = table.nrows
    for i in range(0, nrows):
        row = table.row_values(i)
        sourceId = row[0]

        try:
            sourceId = int(sourceId)
            str_submit_time = row[1]
            #publishDate = datetime.datetime.strptime(str_submit_time, "%Y-%m-%d %H:%M:%S")
            publishDate = xlrd.xldate.xldate_as_datetime(str_submit_time, 0)
            logger.info(publishDate)
            name = row[2].strip()
            fullname = row[3].strip()
            code = row[4].strip()
            field = row[5].strip()
            product_desc = row[6].strip()
            model_desc = row[7].strip()
            operation_desc = row[8].strip()
            plan_desc = row[9].strip()
            str_investor = row[10].strip()
            str_investment = row[11].strip()
            str_round= row[12].strip()
            str_currency = row[13].strip()
            str_member_name = row[14].strip()
            str_member_background = row[15].strip()
            logger.info("ID: %s, project name: %s, fullname: %s", sourceId, name, fullname)

            if str_round == "" and str_investment == "":
                investmentHistory = None
            else:
                if str_round == "暂无":
                    investmentHistory = "暂无"
                elif str_investment == "暂未透露":
                    investmentHistory = "%s, 金额暂未透露" % (str_round)
                elif str_investment == "暂不透露":
                    investmentHistory = "%s, 金额暂不透露" % (str_round)
                else:
                    investmentHistory = "%s, %s%s" % (str_round, str_investment,str_currency)
                if investmentHistory.startswith(", "):
                    investmentHistory = investmentHistory[2:]

            members = str_member_name.replace('、', "###").split("###")
            # for member in members:
            #    logger.info(member)

            candidate_companies = find_company_candidate(name, fullname)
            for c in candidate_companies:
                logger.info("candidate: %s", c["name"])
            if len(candidate_companies) == 0:
                logger.info("***")

            ns = find_related_news(name, members[0])
            for n in ns:
                logger.info("news: %s", n["title"])

            data = {
                "name": name,
                "fullname": fullname,
                "sourceId": sourceId,
                "code": code,
                "publishDate": publishDate,
                "productDesc": product_desc,
                "modelDesc": model_desc,
                "operationDesc": operation_desc,
                "planDesc": plan_desc,
                "founder": str_member_name,
                "founderDesc": str_member_background,
                "field": field,
                "investmentHistory": investmentHistory,
                "investorHistory": str_investor,
                "candidate_companies": candidate_companies,
                "candidate_news": ns
            }

            save(data)
            #break
        except:
            traceback.print_exc()
            pass
        logger.info("")


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "usage: python pencilnews.py <filename>"
        exit()
    filename = sys.argv[1]
    data = xlrd.open_workbook(filename)
    process(data.sheets()[0])