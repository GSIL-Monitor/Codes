# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("user_deal_panel_patch", stream=True)
logger = loghelper.get_logger("user_deal_panel_patch")


if __name__ == "__main__":
    conn = db.connect_torndb()
    ps = conn.query("select * from user_deal_panel")
    for p in ps:
        deal_id = p["dealId"]
        org_id = p["orgId"]
        deal = conn.get("select * from deal where id=%s", deal_id)
        if org_id != deal["organizationId"]:
            logger.info("deal %s not belong this panel %s", deal_id, p["id"])
            conn.execute("delete from user_deal_panel where id=%s", p["id"])
    conn.close()