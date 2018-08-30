# -*- coding: utf-8 -*-
# 寻找投资机构的所有可能的公司名称
import os, sys
import datetime

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("find_investor_alias", stream=True)
logger = loghelper.get_logger("find_investor_alias")


def find(investor_id):
    all_investors = []
    conn = db.connect_torndb()
    exist_names = conn.query("select * from investor_alias "
                             "where (active is null or active='Y') and type=12010 and investorId=%s",
                             investor_id)
    exist_shortnames = conn.query("select * from investor_alias "
                             "where (active is null or active='Y') and type=12020 and investorId=%s",
                             investor_id)
    investor = conn.get("select * from investor where id=%s", investor_id)
    exist_shortnames.append(investor)

    companies = conn.query("select distinct c.* from company c "
                           "join funding f on c.id=f.companyId "
                           "join funding_investor_rel r on f.id=r.fundingId "
                           "where (c.active is null or c.active='Y') and "
                           "(f.active is null or f.active='Y') and "
                           "(r.active is null or r.active='Y') and "
                           "r.investorId=%s",
                           investor_id)

    for c in companies:
        investors = find_investors_from_gongshang(c["fullName"])
        merge_2_all_investors(all_investors, investors)

        all_alias = conn.query("select * from company_alias where (active is null or active='Y') and companyId=%s",
                               c["id"])
        for alias in all_alias:
            investors = find_investors_from_gongshang(alias["name"])
            merge_2_all_investors(all_investors, investors)

    conn.close()

    # logger.info(all_investors)

    for n in exist_names:
        name = n["name"]
        if name in all_investors:
            all_investors.remove(name)

    for name in all_investors:
        if name is None:
            continue
        logger.info(name)
        candidate = 'N'
        if is_candidate(name, exist_shortnames):
            candidate = 'Y'
        conn = db.connect_torndb()
        c = conn.get("select * from investor_alias_candidate where investorId=%s and name=%s",
                     investor_id, name)
        if c is None:
            conn.insert("insert investor_alias_candidate(investorId, name, type, createTime, candidate) values(%s,%s,%s,now(),%s)",
                        investor_id, name, 12010, candidate)
        conn.close()

    # 重新检查已有记录
    conn = db.connect_torndb()
    candidates = conn.query("select * from investor_alias_candidate where investorId=%s and candidate='N'", investor_id)
    for c in candidates:
        if is_candidate(c["name"], exist_shortnames):
            conn.update("update investor_alias_candidate set candidate='Y' where id=%s", c["id"])
    conn.close()


def is_candidate(name, exist_shortnames):
    if name is None:
        return False

    for s in exist_shortnames:
        if s["name"] in name:
            return True

    return False


def find_investors_from_gongshang(name):
    gs = mongo.info.gongshang.find_one({"name":name})
    if gs is not None:
        return gs["investors"]
    return None


def merge_2_all_investors(all_investors, investors):
    if investors is None:
        return

    for investor in investors:
        if investor["type"] == u"企业投资":
            name = investor["name"]
            if name not in all_investors:
                # logger.info(name)
                all_investors.append(name)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "usage: python find_investor_alias <investorId>"
        exit()

    investor_id = sys.argv[1]
    mongo = db.connect_mongo()
    find(investor_id)
    mongo.close()

