# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("pencilnews_postprocess", stream=True)
logger = loghelper.get_logger("pencilnews_postprocess")

SOURCE = 13800

if __name__ == "__main__":
    while True:
        logger.info("Start...")
        conn = db.connect_torndb()
        cs = conn.query("select * from company_fa where source=13800 and processStatus=1")
        for c in cs:
            logger.info("id: %s, name: %s", c["id"], c["name"])
            str_member_name = c["founder"].strip()
            str_member_background = c["founderDesc"].strip()

            members = str_member_name.replace('、', "###").split("###")
            backgrounds = str_member_background.split('###')
            if len(members) != len(backgrounds):
                logger.info("Member error: %s", c["id"])
                conn.update("update company_fa set processStatus=2 where id=%s", c["id"])
                continue

            rels = conn.query("select m.name from company_member_rel r join member m on r.memberId=m.id where companyId=%s", c['companyId'])
            exist_member_names = []
            for r in rels:
                exist_member_names.append(r["name"])
                logger.info(r["name"])
            for i in range(0,len(members)):
                member_name = members[0]
                member_desc = backgrounds[0]
                if member_name not in exist_member_names:
                    logger.info("new member: %s", member_name)
                    member_id = conn.insert("insert member(name,description,createTime) values(%s,%s,now())",
                                            member_name, member_desc)
                    conn.insert("insert company_member_rel(companyId,memberId,position,type,createTime) "
                                "values(%s,%s,'创始人',5010,now())",
                                c["companyId"], member_id)
            conn.update("update company_fa set processStatus=2 where id=%s", c["id"])
            #exit()
        conn.close()
        logger.info("End.")
        if len(cs) == 0:
            time.sleep(600)