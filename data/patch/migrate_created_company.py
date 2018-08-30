# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("migrate_created_company", stream=True)
logger = loghelper.get_logger("migrate_created_company")

LISTNAME='我创建的公司'

if __name__ == "__main__":
    conn = db.connect_torndb()
    users = conn.query("select createUser,count(*) from company where createUser > 0 group by createuser")
    for user in users:
        user_id = user["createUser"]
        logger.info("userId: %s", user_id)
        rel = conn.get("select * from mylist l join user_mylist_rel r on l.id=r.mylistId "
                       "where r.userId=%s and l.name=%s",
                       user_id, LISTNAME)
        if rel is None:
            mylistid = conn.insert("insert mylist(name,isPublic,active,createTime,createUser) values(%s,'N','Y',now(),%s)", LISTNAME, user_id)
            conn.insert("insert user_mylist_rel(userId, mylistId,createTime,createUser) values(%s,%s,now(),%s)", user_id, mylistid, user_id)
        else:
            mylistid = rel["mylistId"]

        cs = conn.query("select * from company where createUser=%s and (active is null or active='Y')", user_id)
        for c in cs:
            logger.info(c["name"])
            company_id = c["id"]
            r = conn.get("select * from mylist_company_rel where mylistId=%s and companyId=%s",mylistid, company_id)
            if r is None:
                conn.insert("insert mylist_company_rel(mylistId,companyId,createTime) values(%s,%s,now())",
                            mylistid, company_id)
        #break
    conn.close()