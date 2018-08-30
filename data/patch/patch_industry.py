# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_industry", stream=True)
logger = loghelper.get_logger("patch_industry")


def patch_lastmessagetime():
    conn = db.connect_torndb()
    industries = conn.query("select * from industry")
    for industry in industries:
        logger.info("industryId: %s", industry["id"])
        last_message_time = industry["modifyTime"]
        if last_message_time is None:
            last_message_time = industry["createTime"]
        item = conn.get("select * from industry_news where industryId=%s order by publishTime desc limit 1", industry["id"])
        if item is not None and item["createTime"] > last_message_time:
            last_message_time = item["createTime"]
        item = conn.get("select * from industry_company where industryId=%s order by publishTime desc limit 1", industry["id"])
        if item is not None and item["createTime"] > last_message_time:
            last_message_time = item["createTime"]

        conn.update("update industry set lastMessageTime=%s where id=%s",
                    last_message_time, industry["id"])
    conn.close()


if __name__ == "__main__":
    patch_lastmessagetime()
