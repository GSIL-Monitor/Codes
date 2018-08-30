# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("init_user_collection", stream=True)
logger = loghelper.get_logger("init_user_collection")

def process():
    logger.info("Init user collection")
    cids = []
    conn = db.connect_torndb()
    cs = conn.query("select * from collection where (active is null or active='Y') and type=39010")
    for c in cs:
        cids.append(c["id"])

    users = conn.query("select * from user where active is null or active='Y'")
    for user in users:
        for cid in cids:
            r = conn.get("select * from collection_user_rel where collectionId=%s and userId=%s", cid, user["id"])
            if r is None:
                conn.insert("insert collection_user_rel(collectionId,userId,verify,active,createTime) \
                            values(%s,%s,'Y','Y',now())",
                            cid,user["id"])
    conn.close()

    logger.info("End init user collection")

if __name__ == '__main__':
    process()
