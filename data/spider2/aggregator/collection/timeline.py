# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

import collection_newproduct

#logger
loghelper.init_logger("timeline", stream=True)
logger = loghelper.get_logger("timeline")

def process():
    logger.info("Process timeline")
    tops = collection_newproduct.get_top_new_products()

    conn = db.connect_torndb()
    users = conn.query("select * from user")
    for user in users:
        cs = conn.query("select * from collection_user_rel where userId=%s and active='Y'",user["id"])
        for c in cs:
            collectionId=c["collectionId"]
            if collectionId==21:    #每日新产品,特殊处理
                ts = conn.query("select ct.* from collection_timeline ct \
                            join collection_company_rel ccr \
                                on ct.collectionCompanyId=ccr.id and ccr.collectionId=21 \
                            where userId=%s", user["id"])
                for t in ts:
                    conn.execute("delete from collection_timeline where id=%s", t["id"])
                for t in tops:
                    conn.insert("insert collection_timeline(userId,collectionCompanyId,time) values(%s,%s,%s)",
                                user["id"], t["id"], t["createTime"])
            else:
                ps = conn.query("select ccr.* from  \
                            collection_company_rel ccr \
                            left join collection_timeline ct \
                                on ccr.id=ct.collectionCompanyId and ct.userId=%s \
                            where collectionId=%s and ct.userId is null",
                                user["id"], collectionId)
                for p in ps:
                    conn.insert("insert collection_timeline(userId,collectionCompanyId,time) values(%s,%s,%s)",
                                user["id"], p["id"], p["createTime"])
    conn.close()

    logger.info("End process timeline")

if __name__ == '__main__':
    process()
