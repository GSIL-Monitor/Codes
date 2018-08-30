# -*- coding: utf-8 -*-
__author__ = 'arthur'
#老的FA是通过source_company来标记的

import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("set_endorse_tag_patch", stream=True)
logger = loghelper.get_logger("set_endorse_tag_patch")


if __name__ == "__main__":
    logger.info("Start...")
    conn = db.connect_torndb()
    cs = conn.query("select * from source_company where source in "
                    "(13100,13101,13102,13103,13104,13300,13301,13800) order by id")
    for c in cs:
        source = c["source"]
        dict = conn.get("select * from dictionary where value=%s", source)
        tag_id = None
        if dict["subTypeValue"] == 1301:
            #FA
            tag_id = 479289
        elif dict["subTypeValue"] == 1302:
            #孵化器
            tag_id = 479291
        elif dict["subTypeValue"] == 1303:
            #媒体
            tag_id = 479290

        if tag_id:
            rel = conn.get("select * from company_tag_rel where companyId=%s and tagId=%s limit 1",
                           c["companyId"], tag_id)
            if rel is None:
                logger.info("companyId:%s, tagId:%s", c["companyId"], tag_id)
                conn.insert("insert company_tag_rel(companyId,tagId,verify,createTime,confidence) "
                            "values(%s,%s,'Y',now(),0.5)",
                            c["companyId"], tag_id)
    conn.close()
    logger.info("End.")

