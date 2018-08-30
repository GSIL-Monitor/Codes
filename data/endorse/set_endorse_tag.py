# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("set_endorse_tag", stream=True)
logger = loghelper.get_logger("set_endorse_tag")


def delete_no_fa(subTypeValue):
    logger.info("delete_no_fa begin...")
    if subTypeValue == 1301:
        #FA
        tag_id = 479289
    elif subTypeValue == 1302:
        #孵化器
        tag_id = 479291
    else:
        return


    conn = db.connect_torndb()
    rels = conn.query("select * from company_tag_rel where tagId=%s", tag_id)
    for rel in rels:
        company_id = rel["companyId"]
        cf = conn.get("select * from company_fa f join dictionary d on f.source=d.value "
                      "where companyId=%s and subTypeValue=%s limit 1",
                      company_id, subTypeValue)
        if cf is None:
            logger.info("delete  tag %s from company %s", tag_id, company_id)
            conn.execute("delete from company_tag_rel where id=%s", rel["id"])
        else:
            #logger.info("keep  tag %s from company %s", tag_id, company_id)
            pass
    conn.close()
    logger.info("delete_no_fa end...")

if __name__ == "__main__":
    start = 0
    while True:
        logger.info("Start...")
        conn = db.connect_torndb()
        cs = conn.query("select * from company_fa where id>%s order by id limit 1000", start)
        for c in cs:
            start = c["id"]
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

            if tag_id and c["companyId"] is not None:
                rel = conn.get("select * from company_tag_rel where companyId=%s and tagId=%s limit 1",
                               c["companyId"], tag_id)
                if rel is None:
                    logger.info("companyId:%s, tagId:%s", c["companyId"], tag_id)
                    conn.insert("insert company_tag_rel(companyId,tagId,verify,createTime,confidence) "
                                "values(%s,%s,'Y',now(),0.5)",
                                c["companyId"], tag_id)
        conn.close()
        logger.info("End.")

        delete_no_fa(1301)
        delete_no_fa(1302)

        if len(cs) == 0:
            start = 0
            time.sleep(600)