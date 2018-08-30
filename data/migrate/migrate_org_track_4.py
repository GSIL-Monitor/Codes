# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("migrate", stream=True)
logger = loghelper.get_logger("migrate")

conn = db.connect_torndb()


def main(org_id):
    fp = open("100partners.txt")
    for code in fp:
        code = code.strip()
        if code == "":
            continue
        company = conn.get("select * from company where code=%s", code)
        companies = conn.query("select * from company where corporateId=%s and (active is null or active='Y')",
                               company["corporateId"])
        for company in companies:
            if company["active"] is not None and company["active"] != 'Y':
                continue
            logger.info("%s: %s", company["id"], company["name"])
            rel = conn.get("select * from org_track_company where orgId=%s and companyId=%s",
                           org_id, company["id"])
            if rel is None:
                conn.insert("insert org_track_company(orgId,companyId,createTime,modifyTime) values("
                            "%s,%s,now(),now())",
                            org_id, company["id"])


if __name__ == "__main__":
    main(2814)