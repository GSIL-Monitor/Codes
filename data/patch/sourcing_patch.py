# -*- coding: utf-8 -*-
import os, sys
import json
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("sourcing_patch", stream=True)
logger = loghelper.get_logger("sourcing_patch")


def main():
    conn = db.connect_torndb()
    items = conn.query("select * from user_company_follow")
    for item in items:
        ss = conn.query("select * from sourcing_company_user_rel where userId=%s and companyId=%s",
                        item["userId"], item["companyId"])
        for s in ss:
            if item["followType"] != s["followType"] and s["followType"]==1040:
                logger.info("user_company_follow: %s, userId: %s, companyId: %s, followType: %s",
                            item["id"], item["userId"], item["companyId"], item["followType"])
                logger.info("sourcing_company_user_rel: %s, userId: %s, companyId: %s, followType: %s",
                            s["id"], s["userId"], s["companyId"], s["followType"])
                conn.update("update sourcing_company_user_rel set "
                            "modifyUser=%s,modifyTime=%s,followType=%s where id=%s",
                            s["userId"], item["modifyTime"], item["followType"], s["id"])
                logger.info("--------------------------------------")
                # exit()
    conn.close()


if __name__ == "__main__":
    main()