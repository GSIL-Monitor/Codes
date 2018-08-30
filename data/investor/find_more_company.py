# -*- coding: utf-8 -*-
# 以investor为起点，发现更多的公司
import os, sys
import datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper
import find_investor_alias

#logger
loghelper.init_logger("find_more_company", stream=True)
logger = loghelper.get_logger("find_more_company")


# 由于工商信息的获取是异步的，且investor_alias会有补充，所以要find多次才会遍历到所有可能的公司
def find(investor_id):
    # 查表investor_alias
    # 从每个investor_alias工商中获取公司的股东和对外投资
    find_from_investor_alias(investor_id)

    # 查表funding_investor_rel
    # 从每个portfolio工商中获取公司的股东和对外投资
    find_from_portfolio(investor_id)


def find_from_investor_alias(investor_id):
    conn = db.connect_torndb()
    all_alias = conn.query("select * from investor_alias where (active is null or active='Y') and investorId=%s", investor_id)
    for alias in all_alias:
        add_2_company_list(alias["name"])
        find_from_gongshang(alias["name"])
    conn.close()

def find_from_portfolio(investor_id):
    conn = db.connect_torndb()
    companies = conn.query("select distinct c.* from company c "
                           "join funding f on c.id=f.companyId "
                           "join funding_investor_rel r on f.id=r.fundingId "
                           "where (c.active is null or c.active='Y') and "
                           "(f.active is null or f.active='Y') and "
                           "(r.active is null or r.active='Y') and "
                           "r.investorId=%s",
                           investor_id)
    for c in companies:
        logger.info("company name: %s", c["name"])
        company_name = c["fullName"]
        add_2_company_list(company_name)
        all_alias = conn.query("select * from company_alias where (active is null or active='Y') and companyId=%s",
                               c["id"])
        for alias in all_alias:
            company_name = alias["name"]
            add_2_company_list(company_name)
            find_from_gongshang(company_name)
    conn.close()


def find_from_gongshang(name):
    name = name_helper.company_name_normalize(name)
    if name is None:
        return
    chinese, company = name_helper.name_check(name)
    if chinese is True and company is True:
        gs = mongo.info.gongshang.find_one({"name":name})
        if gs is not None:
            for investor in gs["investors"]:
                if investor["type"] == u"企业投资":
                    logger.info("gongshang name: %s", investor["name"])
                    add_2_company_list(investor["name"])
            if gs.has_key("invests"):
                for invest in gs["invests"]:
                    add_2_company_list(invest["name"])


def add_2_company_list(name):
    name = name_helper.company_name_normalize(name)
    if name is None:
        return
    chinese, company = name_helper.name_check(name)
    if chinese is True and company is True:
        logger.info("fullname: %s", name)
        name_md5 = util.md5str(name)
        c = mongo.info.company_idx.find_one({"name_md5": name_md5})
        if c is None:
            data = {
                "name": name,
                "name_md5": name_md5,
                "createTime": datetime.datetime.utcnow()
            }
            mongo.info.company_idx.insert_one(data)

def add_2_checklist():
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    famous_investors = conn.query("select * from famous_investor where (active is null or active='Y')")
    for finvesot in famous_investors:
        item = mongo.investor.checklist.find_one({"investorId": str(finvesot["investorId"])})
        if item is None:
            investor_name = conn.get("select * from investor where id=%s", finvesot["investorId"])
            if investor_name is not None:
                mongo.investor.checklist.insert({
                    "investorName": investor_name["name"], "investorId": str(finvesot["investorId"])})
    mongo.close()
    conn.close()



if __name__ == "__main__":
    if len(sys.argv) <= 1:
        logger.info("usage: python find_more_company <investorId> | <all>")
        exit()
    investor_id = sys.argv[1]
    if investor_id == "all":
        while True:
            add_2_checklist()
            mongo = db.connect_mongo()
            items = list(mongo.investor.checklist.find())
            mongo.close()
            for item in items:
                logger.info("********** %s **********", item["investorName"])
                mongo = db.connect_mongo()
                find(item["investorId"])
                find_investor_alias.mongo = mongo
                find_investor_alias.find(item["investorId"])
                mongo.close()
                logger.info("")
                logger.info("")

            time.sleep(4*3600)  #8hours
    else:
        mongo = db.connect_mongo()
        find(investor_id)
        find_investor_alias.mongo = mongo
        find_investor_alias.find(investor_id)
        mongo.close()