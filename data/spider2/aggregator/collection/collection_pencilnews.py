# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("collection_pencilnews", stream=True)
logger = loghelper.get_logger("collection_pencilnews")

COLLECTION_ID = 844
def process():
    logger.info("Process collection pencilnews")
    conn = db.connect_torndb()
    cs = conn.query("select c.id as companyId, sc.createTime as createTime from company c join company_fa sc on sc.companyId=c.id "
                    "where (c.active is null or c.active='Y') and (sc.active is null or sc.active='Y') "
                    "and sc.source=13800 "
                    "order by sc.publishDate")
    for c in cs:
        rel = conn.get("select * from collection_company_rel where (active is null or active='Y') and collectionId=%s and companyId=%s", COLLECTION_ID, c["companyId"])
        if rel is None:
            conn.insert("insert collection_company_rel(collectionId,companyId,verify,active,createTime) \
                        values(%s,%s,'Y','Y',%s)",
                        COLLECTION_ID, c["companyId"],c["createTime"])

    collection_fa = conn.get("select * from collection where id=%s", COLLECTION_ID)
    r = conn.get("select count(*) as cnt from collection_company_rel where (active is null or active='Y') and collectionId=%s and createTime >=%s",
                 COLLECTION_ID, collection_fa["modifyTime"])
    if r["cnt"] > 0:
        conn.update("update collection set mark='Y', modifyTime=now() where id=%s", COLLECTION_ID)

    conn.close()

    logger.info("End process collection pencilnews")

if __name__ == '__main__':
    process()
