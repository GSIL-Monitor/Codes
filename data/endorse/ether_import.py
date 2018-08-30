# -*- coding: utf-8 -*-
import os, sys
import time
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db
import endorse_util

#logger
loghelper.init_logger("ether_import", stream=True)
logger = loghelper.get_logger("ether_import")

SOURCE = 13100


def main():
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    items = list(mongo.fa.ether.find({"processStatus":{"$exists": False}}).sort("_id",1))
    for item in items:
        logger.info(item)
        process(item, conn)
        mongo.fa.ether.update({"_id":item["_id"]},{"$set":{"processStatus":1}})
        # exit(0)
    mongo.close()
    conn.close()


def find_company_fa(item, conn):
    uniqueId = item.get("uniqueId")
    if uniqueId is not None:
        uniqueId = str(uniqueId)
        item["uniqueId"] = uniqueId
        fa = conn.get(" select * from company_fa where source=%s and sourceId2=%s and round=%s"
                      " and (active is null or active='Y')"
                      " order by publishDate desc limit 1",
                      SOURCE, uniqueId, item["round"])
        if fa is not None:
            return fa

    f = conn.get(" select * from company_fa where source=%s and sourceId=%s and round=%s"
                 " order by publishDate desc limit 1",
        SOURCE, item["sourceId"], item["round"])
    return f


def get_round(str_round):
    invest_round = None
    if str_round == u"天使" or str_round == "1":
        invest_round = 1011
    elif str_round == u"Pre-A" or str_round == "2":
        invest_round = 1020
    elif str_round == u"A轮" or str_round == "3":
        invest_round = 1030
    elif str_round == u"B轮" or str_round == "4":
        invest_round = 1040
    elif str_round == u"C轮" or str_round == "5":
        invest_round = 1050
    elif str_round == u"D轮" or str_round == "6":
        invest_round = 1060
    elif str_round == u"D轮以上" or str_round == "16":
        invest_round = 1090
    return invest_round


def process(item, conn):
    source_id = None
    if item["fullName"] != "":
        source_id = item["fullName"]
    elif item["name"] != "":
        source_id = item["name"]
    if source_id is None:
        logger.info("have no name or fullName!")
        return

    item["sourceId"] = source_id
    currency = None
    if item["currency"] == "1":
        currency = 3020  # RMB
    elif item["currency"] == "2":
        currency = 3010  # USD
    item["currency"] = currency


    item["round"] = get_round(item["round"])
    if item["investmentMin"] < 1000000:
        item["investmentMin"] = item["investmentMin"] * 10000
    if item["investmentMax"] < 1000000:
        item["investmentMax"] = item["investmentMax"] * 10000

    item["comments"] = item["fullName"] + "\n\n" + item["abstract"]

    if item["endDate"] == 0 and item["publishDate"] != 0:
        # 上架
        # f = conn.get("select * from company_fa where source=%s and sourceId=%s and round=%s order by publishDate desc limit 1",
        #              SOURCE, source_id, item["round"])
        f = find_company_fa(item, conn)
        candidate_companies = endorse_util.find_company_candidate(item["name"], item["fullName"], conn)
        if f is None:
            save_new(item, candidate_companies, conn)
        else:
            # 有更新的记录
            update(item, f["id"], candidate_companies, conn)
    elif item["endDate"] != 0:
        # 下架
        # f = conn.get("select * from company_fa where source=%s and sourceId=%s and round=%s order by publishDate desc limit 1",
        #              SOURCE, source_id, item["round"])
        f = find_company_fa(item, conn)
        # 最新一条记录
        if f is not None:
            if f["endDate"] is None and item["endDate"] > f["publishDate"]:
                conn.update("update company_fa set endDate=%s where id=%s", item["endDate"], f["id"])


def save_new(data, candidate_companies, conn):
    highlights = data.get("highlights")
    highlights_str = None
    if highlights is not None:
        highlights_str = json.dumps(highlights)

    advisor_vendor_name = data.get("advisor_vendor_name")
    fa_id = 1
    if advisor_vendor_name is not None:
        fa = conn.get("select * from fa where name=%s and (active is null or active='Y') limit 1", advisor_vendor_name)
        if fa is None:
            fa_id = conn.insert("insert fa(name,active,createTime,modifyTime) values(%s,'Y', now(),now())", advisor_vendor_name)
        else:
            fa_id = fa["id"]

    company_fa_id = conn.insert("insert company_fa("
                                "name,source,sourceId,publishDate,"
                                "round,currency,investmentMin,investmentMax,"
                                "processStatus,createTime, modifyTime, comments, faId, sourceId2, highlights"
                                ") values("
                                "%s,%s,%s,%s,"
                                "%s,%s,%s,%s,"
                                "%s,now(),now(),%s,%s,%s,%s)",
                                data["name"], SOURCE, data["sourceId"], data["publishDate"],
                                data["round"], data["currency"], data["investmentMin"], data["investmentMax"],
                                0, data["comments"], fa_id, data.get("uniqueId"), highlights_str
                                )
    # company_fa_candidate
    for c in candidate_companies:
        conn.insert("insert company_fa_candidate(companyFaId, companyId) values(%s,%s)",
                    company_fa_id, c["id"])

    # fa_advisor
    if data["advisor_name"] is not None and data["advisor_name"].strip() != "":
        advisor = conn.get("select * from fa_advisor "
                           " where faId=%s and name=%s and (active is null or active='Y') limit 1",
                           fa_id, data["advisor_name"])
        if advisor is None:
            fa_advisor_id = conn.insert("insert fa_advisor(source,name,phone,wechat,email,createtime,modifyTime, faId) "
                                        "values(%s,%s,%s,%s,%s,now(),now(),%s)",
                                        SOURCE, data["advisor_name"], data["advisor_phone"], data["advisor_wechat"],
                                        data["advisor_email"], fa_id)
        else:
            fa_advisor_id = advisor["id"]
        conn.insert("insert company_fa_advisor_rel(companyFaId, faAdvisorId,createTime) values(%s,%s,now())",
                    company_fa_id, fa_advisor_id)


def update(data, company_fa_id, candidate_companies, conn):
    highlights = data.get("highlights")
    highlights_str = None
    if highlights is not None:
        highlights_str = json.dumps(highlights)

    advisor_vendor_name = data.get("advisor_vendor_name")
    fa_id = 1
    if advisor_vendor_name is not None:
        fa = conn.get("select * from fa where name=%s and (active is null or active='Y') limit 1", advisor_vendor_name)
        if fa is None:
            fa_id = conn.insert("insert fa(name,active,createTime,modifyTime) values(%s,'Y', now(),now())",
                                advisor_vendor_name)
        else:
            fa_id = fa["id"]

    conn.update("update company_fa set "
                                "name=%s,source=%s,sourceId=%s,publishDate=%s,endDate=null,"
                                "round=%s,currency=%s,investmentMin=%s,investmentMax=%s,"
                                "processStatus=%s, modifyTime=now(), comments=%s, faId=%s, highlights=%s "
                                "where id=%s",
                                data["name"], SOURCE, data["sourceId"], data["publishDate"],
                                data["round"], data["currency"], data["investmentMin"], data["investmentMax"],
                                0, data["comments"], fa_id, highlights_str,
                                company_fa_id
                                )
    # company_fa_candidate
    conn.execute("delete from company_fa_candidate where companyFaId=%s", company_fa_id)
    for c in candidate_companies:
        conn.insert("insert company_fa_candidate(companyFaId, companyId) values(%s,%s)",
                    company_fa_id, c["id"])

    # fa_advisor
    conn.execute("delete from company_fa_advisor_rel where companyFaId=%s", company_fa_id)
    if data["advisor_name"] is not None and data["advisor_name"].strip() != "":
        advisor = conn.get("select * from fa_advisor "
                           " where faId=%s and name=%s and (active is null or active='Y') limit 1",
                           fa_id, data["advisor_name"])
        if advisor is None:
            fa_advisor_id = conn.insert("insert fa_advisor(source,name,phone,wechat,email,createtime,modifyTime,faId) "
                                        "values(%s,%s,%s,%s,%s,now(),now(),%s)",
                                        SOURCE, data["advisor_name"], data["advisor_phone"], data["advisor_wechat"],
                                        data["advisor_email"], fa_id)
        else:
            fa_advisor_id = advisor["id"]
        conn.insert("insert company_fa_advisor_rel(companyFaId, faAdvisorId,createTime) values(%s,%s,now())",
                    company_fa_id, fa_advisor_id)


def patch_round():
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    items = conn.query("select * from company_fa where round is null and source=%s "
                       "and (active is null or active='Y') order by id desc", SOURCE)
    for item in items:
        fas = list(mongo.fa.ether.find({"name":item["name"]}).sort([("_id",-1)]))
        if len(fas) > 0:
            fa = fas[0]
            round = get_round(fa["round"])
            if round is not None:
                logger.info("%s, %s, %s", fa["_id"], fa["name"], round)
                conn.update("update company_fa set round=%s where id=%s", round, item["id"])
                # exit(0)
    mongo.close()
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        while True:
            logger.info("Start...")
            main()
            logger.info("End.")
            time.sleep(60)
    else:
        if sys.argv[1] == "patch":
            patch_round()