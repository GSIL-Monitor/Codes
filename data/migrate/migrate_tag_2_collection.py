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

tags = [
    (593289, "2017寻找中国创客45强"),
    (592646, "2017上海科创资金立项"),
    (591758, "微链2017新品牌100榜单"),
    (595296, "清科2017新芽榜50强"),
    (595297, "清科2017风云榜50强")
]


def main():
    for tag_id, name in tags:
        collection_id = get_collection(name)
        cs = get_companies(tag_id)
        save_in_collection(collection_id, cs)


def get_collection(name):
    c = conn.get("select * from collection where "
                 "type=39020 and subtype=39120 and "
                 "name=%s", name)
    if c is not None:
        return c["id"]

    c_id = conn.insert("insert collection(name,type,subtype,sort,active,createTime,modifyTime) "
                       "values(%s,39020,39120,0,'Y',now(),now())",
                       name)
    return c_id


def get_companies(tag_id):
    rels = conn.query("select companyId from company_tag_rel r "
                    "join company c on r.companyId=c.id "
                    "where tagId=%s and "
                    "(c.active is null or c.active='Y') and "
                    "(r.active is null or r.active='Y')",
                    tag_id)
    return [r["companyId"] for r in rels]


def save_in_collection(collection_id, cs):
    for company_id in cs:
        r = conn.get("select * from collection_company_rel where "
                     "collectionId=%s and companyId=%s",
                     collection_id, company_id)
        if r is None:
            conn.insert("insert collection_company_rel(collectionId,companyId,active,createTime,modifyTime) "
                        "values(%s,%s,'Y',now(),now())",
                        collection_id, company_id)


if __name__ == "__main__":
    main()