# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("revise_user_start_trial_orgid", stream=True)
logger = loghelper.get_logger("revise_user_start_trial_orgid")


def run():
    conn = db.connect_torndb()
    items = conn.query("select * from user_start_trial")
    for item in items:
        org_id = item["orgId"]
        org = conn.get("select * from organization where id=%s", org_id)
        if org["type"] == 17010:
            org1 = conn.get("select o.* from user_organization_rel r join organization o "
                            "on r.organizationId=o.id "
                            "where userId=%s and o.type=17020", item["userId"])
            if org1:
                logger.info("%s: %s", item["id"], org1["id"])
                conn.update("update user_start_trial set orgId=%s where id=%s",
                            org1["id"], item["id"])
    conn.close()


if __name__ == '__main__':
    run()