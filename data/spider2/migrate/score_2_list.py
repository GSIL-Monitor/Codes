# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config
import db

#logger
loghelper.init_logger("score_2_list", stream=True)
logger = loghelper.get_logger("score_2_list")

def process(score, name):
    scores = conn.query("select * from deal_user_score where userId=%s and score=%s", user_id, score)
    if len(scores) > 0:
        mylist = conn.get("select * from mylist  where createUser=%s and name=%s",user_id, name)
        if mylist is None:
            mylistId = conn.insert("insert mylist(name,isPublic,active,createTime,createUser) values(%s,'N','Y',now(),%s)", name, user_id)
        else:
            mylistId = mylist["id"]
        umr = conn.get("select * from user_mylist_rel where userId=%s and mylistId=%s", user_id, mylistId)
        if umr is None:
            conn.insert("insert user_mylist_rel(userId,mylistId,createTime,createUser) values(%s,%s,now(),%s)",user_id,mylistId,user_id)

        for score in scores:
            dealId = score["dealId"]
            deal = conn.get("select * from deal where id=%s", dealId)
            companyId = deal["companyId"]
            company = conn.get("select * from company where id=%s", companyId)
            if company["active"] != 'N':
                r = conn.get("select * from mylist_company_rel where mylistId=%s and companyId=%s", mylistId, companyId)
                if r is None:
                    conn.insert("insert mylist_company_rel(mylistId,companyId,createTime) values(%s,%s,now())",mylistId, companyId)

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    #users = conn.query("select * from user where active!='D'")
    users = conn.query("select * from user where id=327")
    for user in users:
        user_id = user["id"]
        logger.info("userId: %s", user_id)
        #随便聊聊
        #process(3,'随便聊聊')
        #process(2,'太烂了')
        process(4,'默认收藏夹(旧)')
        process(1,'我不关心的(旧)')
    conn.close()
    logger.info("End.")