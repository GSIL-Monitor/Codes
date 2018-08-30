# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("revise_user_organization_rel_trial", stream=True)
logger = loghelper.get_logger("revise_user_organization_rel_trial")


def run():
    mongo = db.connect_mongo()
    items = mongo.log.api_log.find({"requestURL": '/api/user/upgrade/upgrade'})
    mongo.close()

    conn = db.connect_torndb()
    for item in items:
        user_id = item["userId"]
        r = conn.get("select r.* from user_organization_rel r join organization o on r.organizationId=o.id "
                     "where userId=%s and o.type=17020", user_id)
        if r and r["trial"] != 'Y':
            logger.info("%s", user_id)
            conn.update("update user_organization_rel set trial='Y' where id=%s", r["id"])
    conn.close()


if __name__ == '__main__':
    run()