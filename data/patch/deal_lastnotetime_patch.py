# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("deal_lastnotetime_patch", stream=True)
logger = loghelper.get_logger("deal_lastnotetime_patch")

def process():
    conn = db.connect_torndb()
    last_deal_id = 0
    while True:
        deals = conn.query("select * from deal where id>%s order by id limit 1000", last_deal_id)
        if len(deals) == 0:
            break

        for deal in deals:
            last_deal_id = deal["id"]
            logger.info("id: %s, name: %s", last_deal_id, deal["name"])
            note = conn.get("select * from deal_note where dealId=%s order by modifyTime desc limit 1", last_deal_id)
            if note is None:
                conn.update("update deal set lastNoteTime=createTime where id=%s", last_deal_id)
            else:
                conn.update("update deal set lastNoteTime=%s where id=%s", note["createTime"], last_deal_id)
    conn.close()

if __name__ == "__main__":
    process()
