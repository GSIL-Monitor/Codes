# -*- coding: utf-8 -*-
import os, sys, datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper

#logger
loghelper.init_logger("manual_insert_comps", stream=True)
logger = loghelper.get_logger("manual_insert_comps")

# def get_company(code):
#     conn = db.connect_torndb()
#     company = conn.get("select * from company where code=%s", code)
#     conn.close()
#     if company:
#         return company["id"]
#     else:
#         print "%s not found!" % code
#     return None


# def insert_comps(codes):
#     company_ids = []
#     for code in codes:
#         company_id = get_company(code)
#         if company_id is None:
#             return
#         company_ids.append(company_id)
#
#     for company_id1 in company_ids:
#         conn = db.connect_torndb()
#         conn.execute("delete from companies_rel where companyId=%s and verify='Y'",
#                      company_id1)
#         distance = 11.0
#         for company_id2 in company_ids:
#             if company_id1 == company_id2:
#                 continue
#
#             rel = conn.get("select * from companies_rel where (active is null or active='Y') and "
#                            "companyId=%s and company2Id=%s", company_id1, company_id2)
#             if rel:
#                 conn.update("update companies_rel set distance=%s,verify='Y',active='Y'"
#                             " where id=%s",
#                             distance,rel["id"])
#             else:
#                 conn.insert("insert companies_rel(companyId,company2Id,distance,verify,active,createTime,createUser) "
#                             "values(%s,%s,%s,'Y','Y',now(),1)",
#                             company_id1, company_id2, distance)
#             distance -= 0.001
#         conn.close()
#
#     print "Ok."

def insert_comps(company_id):
    conn.execute("delete from companies_rel where companyId=%s and verify='Y'", company_id)
    cs = conn.query("select compsId from comps_company_rel where companyId=%s", company_id)
    for c in cs:
        comps_id = c["compsId"]
        rs = conn.query("select * from comps_company_rel where compsId=%s order by sort",
                              comps_id)
        distance = 11.0
        for r in rs:
            if company_id == r["companyId"]:
                continue
            e = conn.get("select * from companies_rel where (active is null or active='Y') and "
                            "companyId=%s and company2Id=%s", company_id, r["companyId"])
            if e:
                conn.update("update companies_rel set distance=%s,verify='Y',active='Y'"
                            " where id=%s",
                            distance,e["id"])
            else:
                conn.insert("insert companies_rel(companyId,company2Id,distance,verify,active,createTime,createUser) "
                            "values(%s,%s,%s,'Y','Y',now(),1)",
                            company_id, r["companyId"], distance)
                distance -= 0.001
    logger.info("Ok")

if __name__ == "__main__":
    while True:
        conn = db.connect_torndb()
        comps = conn.query("select * from comps where processStatus=1 and (active is null or active='Y')")
        for comp in comps:
            logger.info(comp["name"])
            rels = conn.query("select * from comps_company_rel where compsId=%s order by sort",
                              comp["id"])
            for rel in rels:
                insert_comps(rel["companyId"])
            conn.update("update comps set processStatus=2 where id=%s", comp["id"])
        conn.close()

        time.sleep(60)
