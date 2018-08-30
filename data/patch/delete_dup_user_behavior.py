# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("delete_dup_user_behavior", stream=True)
logger = loghelper.get_logger("delete_dup_user_behavior")


def patch():
    conn = db.connect_torndb()
    users = conn.query("select distinct userId from user_behavior");
    for u in users:
        items = conn.query("select * from user_behavior where userId=%s order by id desc", u["userId"])
        logger.info("keep: %s", items[0]["id"])
        for item in items[1:]:
            logger.info("delete: %s", item["id"])
            conn.execute("delete from user_behavior where id=%s", item["id"])
    conn.close()


if __name__ == "__main__":
    patch()