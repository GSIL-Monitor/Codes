# -*- coding: utf-8 -*-
# 处理funding表 investor和 funding_investor_rel不一致的情况
import os, sys
import json
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("funding_patch", stream=True)
logger = loghelper.get_logger("funding_patch")


def main():
    num = 0
    conn = db.connect_torndb()
    fundings = conn.query("select * from funding where investors is not null and (active is null or active='Y')")
    for funding in fundings:
        str_investor = funding["investors"]
        if str_investor.strip() == "":
            continue
        data = json.loads(str_investor)
        # logger.info(data)
        investors1 = []
        investors2 = []
        for item in data:
            if item["type"] == "investor":
                investor_id = item["id"]
                investors1.append(investor_id)
        rels = conn.query("select * from funding_investor_rel where fundingId=%s and (active is null or active='Y')", funding["id"])
        for rel in rels:
            investors2.append(rel["investorId"])

        diff = set(investors1) - set(investors2)
        if len(diff) > 0:
            company = conn.get("select * from company where id=%s", funding["companyId"])
            if company["active"] == 'N':
                continue
            num += 1
            logger.info("Check! companyId: %s, code: %s, fundingId: %s, round: %s", funding["companyId"], company["code"], funding["id"], funding["fundingDate"])
            logger.info(investors1)
            investor_names1 = []
            for id in investors1:
                investor = conn.get("select * from investor where id=%s", id)
                investor_names1.append(investor["name"])
                logger.info("%s, %s", investor["name"], investor["active"])
            logger.info(investors2)
            investor_names2 = []
            for id in investors2:
                investor = conn.get("select * from investor where id=%s", id)
                investor_names2.append(investor["name"])
                logger.info("%s, %s", investor["name"], investor["active"])
            break

    conn.close()
    logger.info("total: %s", num)


def revise_investorraw():
    conn = db.connect_torndb()
    fundings = conn.query("select * from funding where active is null or active='Y'")
    for f in fundings:
        investorsRaw = f["investorsRaw"]
        investors = f["investors"]
        if investorsRaw is not None and "\n" in investorsRaw:
            logger.info("fundingId: %s, investorsRaw: %s", f["id"], investorsRaw)
            investorsRaw = investorsRaw.replace("\n", " ")
            conn.update("update funding set investorsRaw=%s where id=%s", investorsRaw, f["id"])
        if investors is not None and "\n" in investors:
            investors = investors.replace("\n", " ")
            conn.update("update funding set investors=%s where id=%s", investors, f["id"])

    conn.close()

if __name__ == "__main__":
    # main()
    revise_investorraw()