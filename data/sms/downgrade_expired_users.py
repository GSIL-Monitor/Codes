# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("downgrade_expired_users", stream=True)
logger = loghelper.get_logger("downgrade_expired_users")



def check():
    conn = db.connect_torndb()
    # expired
    logger.info("expired")
    # rs = conn.query("select r.* from organization o join user_organization_rel r on o.id=r.organizationId "
    #                   "where (r.active is null or r.active='Y') and "
    #                   "grade=33010 and o.trial='Y' and serviceEndDate is not null and date_add(serviceEndDate, interval %s day)<now()",
    #                   5
    #                   )

    orgs = conn.query("select o.* from organization o "
                    "where "
                    "serviceType=80002 and serviceStatus='Y' and serviceEndDate is not null and date_add(serviceEndDate, interval %s day)<now()",
                    5)

    for org in orgs:
        logger.info("downgrade: %s", org["name"])
        conn.update("update organization set serviceStatus='N', modifyTime=now(), modifyUser=221 where id=%s",
                    org["id"])

        rs = conn.query("select r.* from user_organization_rel r "
                        "where (r.active is null or r.active='Y') and "
                        "r.organizationid=%s",
                        org["id"]
                        )
        for r in rs:
            user_id = r["userId"]
            logger.info("downgrade: %s , userId: %s", org["name"], user_id)
            #if user_id != 221:
            #    continue

            # person_org_r = conn.get("select r.* from organization o join user_organization_rel r on o.id=r.organizationId "
            #                       "where grade=33020 and r.userId=%s",user_id)
            # if person_org_r is None:
            #     person_org_id = conn.insert("insert organization(name,type,status,grade,createTime,createUser) values(%s,17010,31010,33020,now(),139)",
            #                 org["name"])
            #     conn.insert("insert user_organization_rel(organizationId,userId,createTime,active) values(%s,%s,now(),'Y')",
            #                 person_org_id, user_id)
            # else:
            #     conn.update("update user_organization_rel set active='Y' where id=%s", person_org_r["id"])

            conn.update("update user_organization_rel set active='N', trial='Y' where id=%s", r["id"])
    conn.close()


if __name__ == "__main__":
    while True:
        try:
            logger.info("Begin check...")
            check()
            logger.info("End check.")
            time.sleep(3600*8)  # 8 hours
        except KeyboardInterrupt:
            exit(0)