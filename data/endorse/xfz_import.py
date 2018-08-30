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
loghelper.init_logger("xfz_import", stream=True)
logger = loghelper.get_logger("xfz_import")

SOURCE=13102


def is_exist(candidate_companies, company):
    for c in candidate_companies:
        if c["id"] == company["id"]:
            return True

    return False


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
    '''
                "sourceId": sourceId,
                "name": name,
                "fullname": fullname,
                "website": website,
                "publishDate": publishDate,
                "establishDate": establishDate,
                "location": location,
                "tags": tags,
                "productDesc": product_desc,
                "advantageDesc": advantage_desc,
                "marketDesc": market_desc,
                "modelDesc": model_desc,
                "operationDesc": operation_desc,
                "members": members,
                "investmentHistory": str_investment,
                "investorHistory": str_investor,
                "candidate_companies": candidate_companies,
                "advisor": advisor
    '''
    conn = db.connect_torndb()
    cfa = conn.get("select * from company_fa where source=%s and sourceId=%s", SOURCE, data["sourceId"])
    if cfa is None:
        company_fa_id = conn.insert("insert company_fa("
                                    "name,source,sourceId,publishDate,"
                                    "productDesc, advantageDesc, marketDesc, modelDesc,operationDesc,"
                                    "field, investmentHistory, investorHistory,"
                                    "processStatus,createTime, modifyTime, faId"
                                    ") values("
                                    "%s,%s,%s,%s,"
                                    "%s,%s,%s,%s,%s,"
                                    "%s,%s,%s,"
                                    "0,now(),now(),3)",
                                    data["name"], SOURCE, data["sourceId"], data["publishDate"],
                                    data["productDesc"], data["advantageDesc"], data["marketDesc"], data["modelDesc"], data["operationDesc"],
                                    data["tags"], data["investmentHistory"], data["investorHistory"]
                                    )
        #company_fa_candidate
        candidate_companies = data["candidate_companies"]
        for c in candidate_companies:
            conn.insert("insert company_fa_candidate(companyFaId, companyId) values(%s,%s)",
                        company_fa_id, c["id"])

        #fa_advisor
        if data["advisor"]["name"] != "":
            advisor = conn.get("select * from fa_advisor where source=%s and name=%s", SOURCE, data["advisor"]["name"])
            if advisor:
                faAdvisorId = advisor["id"]
            else:
                faAdvisorId = conn.insert("insert fa_advisor(source,name,phone,wechat,email,createTime,active) "
                            "values(%s,%s,%s,%s,%s,now(),'Y')",
                                          SOURCE,
                                          data["advisor"]["name"],
                                          data["advisor"]["phone"],
                                          data["advisor"]["wechat"],
                                          data["advisor"]["email"])
            conn.insert("insert company_fa_advisor_rel(companyFaId, faAdvisorId,createTime) values(%s,%s,now())",
                        company_fa_id, faAdvisorId)
    else:
        company_fa_id = cfa["id"]
    conn.close()


def gen_members(members, name, position, desc):
    if name != "":
        member = {
            "name": name,
            "position": position,
            "desc": desc
        }
        members.append(member)

def process(table):

    nrows = table.nrows
    for i in range(0, nrows):
        row = table.row_values(i)
        sourceId = row[0]

        try:
            sourceId = int(sourceId)
            publishDate = xlrd.xldate.xldate_as_datetime(row[1],0)
            name = row[2].strip()
            fullname = row[3].strip()
            website = row[4].strip()
            establishDate = None
            if row[5] != "":
                establishDate = xlrd.xldate.xldate_as_datetime(row[5],0)
            location = row[6]
            tags = row[7].strip()

            product_desc = row[8].strip()
            advantage_desc = row[9].strip()
            market_desc = row[10].strip()
            model_desc = row[11].strip()
            operation_desc = row[12].strip()

            members = []
            member_name1= row[13].strip()
            member_position1 = row[14].strip()
            member_desc1 = row[15].strip()
            gen_members(members, member_name1, member_position1, member_desc1)

            member_name2= row[16].strip()
            member_position2 = row[17].strip()
            member_desc2 = row[18].strip()
            gen_members(members, member_name2, member_position2, member_desc2)

            member_name3= row[19].strip()
            member_position3 = row[20].strip()
            member_desc3 = row[21].strip()
            gen_members(members, member_name3, member_position3, member_desc3)

            str_round = row[22].strip()
            str_investment = row[23].strip()
            str_share = row[24].strip()

            funding_round1 = row[25].strip()
            funding_investment1 = row[26].strip()
            funding_investor1 = row[27].strip()
            funding_round2 = row[28].strip()
            funding_investment2 = row[29].strip()
            funding_investor2 = row[30].strip()
            str_investor = ""
            str_investment = ""
            if funding_investor1 != "":
                str_investor = funding_investor1
                str_investment = "融资轮次" + funding_round1 + ", 融资金额" + funding_investment1 + ", 投资方" + funding_investor1 + "; "
            if funding_investor2 != "":
                str_investor += ", " + funding_investor2
                str_investment += "\n融资轮次" + funding_round2 + ", 融资金额" + funding_investment2 + ", 投资方" + funding_investor2 + ";"

            advisor_name = row[31].strip()
            advisor_phone = row[32]
            advisor_wechat = row[33].strip()
            advisor_email = row[34].strip()
            advisor = {"name": advisor_name,
                       "phone": advisor_phone,
                       "wechat": advisor_wechat,
                       "email": advisor_email}

            candidate_companies = find_company_candidate(name, fullname)
            for c in candidate_companies:
                logger.info("candidate: %s", c["name"])
            if len(candidate_companies) == 0:
                logger.info("*** not found candidate ***")

            data = {
                "sourceId": sourceId,
                "name": name,
                "fullname": fullname,
                "website": website,
                "publishDate": publishDate,
                "establishDate": establishDate,
                "location": location,
                "tags": tags,
                "productDesc": product_desc,
                "advantageDesc": advantage_desc,
                "marketDesc": market_desc,
                "modelDesc": model_desc,
                "operationDesc": operation_desc,
                "members": members,
                "investmentHistory": str_investment,
                "investorHistory": str_investor,
                "candidate_companies": candidate_companies,
                "advisor": advisor
            }

            save(data)
            #logger.info(data)
            #break
        except:
            traceback.print_exc()
            pass
        logger.info("")


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "usage: python xfz_import.py <filename>"
        exit()
    filename = sys.argv[1]
    data = xlrd.open_workbook(filename)
    process(data.sheets()[0])