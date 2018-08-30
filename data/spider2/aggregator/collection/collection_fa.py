# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("collection_fa", stream=True)
logger = loghelper.get_logger("collection_fa")

def process():
    logger.info("Process collection FA")
    conn = db.connect_torndb()
    # cs = conn.query("select c.id as companyId, sc.createTime as createTime from company c join source_company sc on sc.companyId=c.id \
    #                 where (c.active is null or c.active='Y') and sc.source >=13100 and sc.source <=13109 and sc.source!=13105 and (c.description is not null and c.description !='')")
    cs = conn.query("select c.id as companyId, sc.createTime as createTime, sc.publishDate as publishDate "
                    "from company c join company_fa sc on sc.companyId=c.id "
                    "where (c.active is null or c.active='Y') and (sc.active is null or sc.active='Y') "
                    "and sc.source >=13100 and sc.source <=13109"
                    " order by sc.publishDate")
    for c in cs:
        if c["publishDate"] is None:
            continue

        rel = conn.get("select * from collection_company_rel where "
                       "(active is null or active='Y') and collectionId=20 and companyId=%s",
                       c["companyId"])
        if rel is None:
            conn.insert("insert collection_company_rel(collectionId,companyId,verify,active,createTime) \
                        values(%s,%s,'Y','Y',%s)",
                        20, c["companyId"],c["publishDate"])
        else:
            if c["publishDate"] > rel["createTime"]:
                conn.execute("delete from collection_company_rel where id=%s",rel["id"])
                conn.insert("insert collection_company_rel(collectionId,companyId,verify,active,createTime) \
                        values(%s,%s,'Y','Y',%s)",
                        20, c["companyId"],c["publishDate"])

    collection_fa = conn.get("select * from collection where id=20")
    r = conn.get("select count(*) as cnt from collection_company_rel where (active is null or active='Y') and collectionId=20 and createTime >=%s",
                 collection_fa["modifyTime"])
    if r["cnt"] > 0:
        conn.update("update collection set mark='Y', modifyTime=now() where id=20")

    conn.close()

    logger.info("End process collection FA")


def delete_no_fa():
    logger.info("Delete not FA")
    conn = db.connect_torndb()
    rels = conn.query("select * from collection_company_rel where collectionId=20")
    for rel in rels:
        company_fa = conn.get("select * from company_fa f join company c on c.id=f.companyId "
                              "where (c.active is null or c.active='Y') and (f.active is null or f.active='Y') "
                              "and f.source >=13100 and f.source <=13109 and c.id=%s limit 1",
                              rel["companyId"])
        if company_fa is None:
            logger.info("delete: %s, companyId: %s", rel["id"], rel["companyId"])
            conn.execute("delete from collection_company_rel where id=%s", rel["id"])
    conn.close()
    logger.info("End delete not FA")


if __name__ == '__main__':
    process()
    delete_no_fa()
