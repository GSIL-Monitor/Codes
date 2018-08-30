# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../support'))
import loghelper
import db

#logger
loghelper.init_logger("collection_fa_migrate", stream=True)
logger = loghelper.get_logger("collection_fa_migrate")

def process1():
    logger.info("Process collection FA Migrate")
    conn = db.connect_torndb()
    cs = conn.query("select c.id as companyId, sc.createTime as createTime, sc.source as source, c.code as code from company c join source_company sc on sc.companyId=c.id \
                     where (c.active is null or c.active='Y') and sc.source >=13100 and sc.source <=13109 and sc.source!=13105 and (c.description is not null and c.description !='')")

    for c in cs:
        fa = conn.get("select * from company_fa where companyId=%s and source=%s and publishDate=%s",
                      c["companyId"],c["source"],c["createTime"])
        if fa is None:
            logger.info("code: %s", c["code"])
            conn.insert("insert company_fa(companyId,source,publishDate) values(%s,%s,%s)",
                        c["companyId"], c["source"], c["createTime"])
            #exit()
    conn.close()

    logger.info("End process collection FA Migrate")

def process2():
    logger.info("Process collection FA Migrate")
    conn = db.connect_torndb()
    cs = conn.query("select c.id as companyId, sc.createTime as createTime, sc.source as source, c.code as code from company c join source_company sc on sc.companyId=c.id \
                     where (c.active is null or c.active='Y') and sc.source >=13300 and sc.source <=13309 and (c.description is not null and c.description !='')")

    for c in cs:
        #logger.info(c)
        fa = conn.get("select * from company_fa where companyId=%s and source=%s and publishDate=%s",
                      c["companyId"],c["source"],c["createTime"])
        if fa is None:
            logger.info("code: %s", c["code"])
            conn.insert("insert company_fa(companyId,source,publishDate) values(%s,%s,%s)",
                        c["companyId"], c["source"], c["createTime"])
            #exit()
    conn.close()

    logger.info("End process collection FA Migrate")

if __name__ == '__main__':
    process2()
