# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("email_domain_patch", stream=True)
logger = loghelper.get_logger("email_domain_patch")

#grade
#33010				全功能
#33020				部分

#type
#17010	person			个人
#17020	organization	组织

if __name__ == "__main__":
    conn = db.connect_torndb()
    conn.execute("set autocommit=0")
    #orgs = conn.query("select * from organization where grade=33020 and type=17020 order by id")
    orgs = conn.query("select * from organization where id in (48,317)")
    #所有非企业版机构
    for org in orgs:
        logger.info("org name: %s", org["name"])
        users = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                           "where r.organizationId=%s",
                           org["id"])
        #为每个用户生成个人org
        for user in users:
            logger.info(user["username"])
            #关闭原org关系
            conn.update("update user_organization_rel set active='N' where userId=%s and organizationId=%s",
                        user["id"], org["id"])
            person_org = conn.get("select o.* from user_organization_rel r join organization o on r.organizationId=o.id "
                                  "where r.userId=%s and o.type=17010", user["id"])
            if person_org is None:
                #建立自己的关系
                person_org_id = conn.insert("insert organization(name,type,grade,createTime) values(%s,17010,33020,now())",
                            org["name"])
                conn.insert("insert user_organization_rel(organizationId,userId,createTime,active) "
                            "values(%s,%s,now(),'Y')",
                            person_org_id, user["id"])

        #deal 迁移
        deals = conn.query("select * from deal where organizationId=%s", org["id"])
        for deal in deals:
            assignee = conn.get("select * from deal_assignee where dealId=%s order by id limit 1", deal["id"])
            if assignee:
                #logger.info("%s, %s: %s", assignee["userId"], deal["id"], deal["name"])
                person_org = conn.get("select o.* from user_organization_rel r join organization o on r.organizationId=o.id "
                                  "where r.userId=%s and o.type=17010", assignee["userId"])
                if person_org:
                    logger.info("***%s, %s: %s", assignee["userId"], deal["id"], deal["name"])
                    conn.update("update deal set organizationId=%s where id=%s",person_org["id"], deal["id"])
                    # TODO user_deal_panel 要处理!!!

        conn.update("update organization set grade=33010, trial='Y' where id=%s", org["id"])


        conn.execute("commit")
    conn.close()