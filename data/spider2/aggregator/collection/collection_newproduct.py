# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("collection_newproduct", stream=True)
logger = loghelper.get_logger("collection_newproduct")

def process():
    logger.info("Process collection new product")
    conn = db.connect_torndb()
    cs = conn.query("select * from company where (active is null or active='Y') and type=41020")
    for c in cs:
        rel = conn.get("select * from collection_company_rel where (active is null or active='Y') and collectionId=21 and companyId=%s", c["id"])
        if rel is None:
            conn.insert("insert collection_company_rel(collectionId,companyId,verify,active,createTime) \
                        values(%s,%s,'Y','Y',%s)",
                        21, c["id"],c["createTime"])

    collection_new = conn.get("select * from collection where id=21")
    r = conn.get("select count(*) as cnt from collection_company_rel where (active is null or active='Y') and collectionId=21 and createTime >=%s",
                 collection_new["modifyTime"])
    if r["cnt"] > 0:
        conn.update("update collection set mark='Y', modifyTime=now() where id=21")

    conn.close()
    logger.info("End process collection new product")


def get_top_new_products():
    sources=[13021, 13031, 13110, 13111]
    tops = []
    conn = db.connect_torndb()
    for source in sources:
        logger.info("source=%s",source)
        cs = conn.query("select ccr.* from collection_company_rel ccr \
                   join source_company sc \
                   on (ccr.active is null or ccr.active='Y') and ccr.companyId=sc.companyId and sc.source=%s\
                   join source_company_score scs \
                   on sc.id=scs.sourceCompanyid \
                    where ccr.collectionId=21 and ccr.createTime >=curdate() \
                   order by scs.score desc limit 3",
                   source)
        for c in cs:
            tops.append(c)
            logger.info("collectionCompanyId=%s", c["id"])

    conn.close()

    return tops

if __name__ == '__main__':
    process()

