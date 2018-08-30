# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("patch_corporate_alias", stream=True)
logger = loghelper.get_logger("patch_corporate_alias")

def process_corporate():
    id = -1
    conn = db.connect_torndb()
    while True:
        cs = conn.query("select * from corporate where id>%s order by id limit 1000", id)
        if len(cs) == 0:
            break
        for c in cs:
            corporate_id =c["id"]
            fullname = c["fullName"]
            if fullname is None or fullname.strip() == "":
                continue
            fullname = fullname.strip()
            chinese, iscompany = name_helper.name_check(fullname)
            if chinese is False or iscompany is False:
                continue
            # logger.info(c["fullname"])
            if corporate_id > id:
                id = corporate_id

            alias = conn.get("select * from corporate_alias where corporateId=%s and name=%s",
                             corporate_id, fullname)
            if alias is None:
                logger.info(fullname)
                conn.insert("insert corporate_alias(corporateId,name,type,createTime,modifyTime) values(%s,%s,12010,now(),now())",
                            corporate_id, fullname)

    conn.close()


def process_corporate_alias():
    id = -1
    conn = db.connect_torndb()
    while True:
        cs = conn.query("select * from corporate_alias where id>%s and (type=12020 or type is null) order by id limit 1000", id)
        if len(cs) == 0:
            break
        for c in cs:
            if c["id"] > id:
                id = c["id"]
            name = c["name"].strip()
            if len(name)<6:
                continue
            chinese, iscompany = name_helper.name_check(name)
            if chinese is False or iscompany is False:
                continue
            logger.info("%s, %s", c["createTime"], name)
            conn.update("update corporate_alias set type=12010 where id=%s", c["id"])
    conn.close()


def process_fullname():
    conn = db.connect_torndb()
    items = conn.query('select * from corporate where (fullname is null or fullname="") and (active is null or active!="N")')
    for item in items:
        aliass = conn.query("select * from corporate_alias where (active is null or active='Y') and "
                            "corporateId=%s and type=12010", item["id"])
        if len(aliass) == 1:
            logger.info("corporateId: %s, %s", item["id"], aliass[0]["name"])
            conn.update("update corporate set fullname=%s where id=%s", aliass[0]["name"].strip(), item["id"])
        elif len(aliass) > 1:
            logger.info("corporateId: %s, cnt: %s", item["id"], len(aliass))

    conn.close()

if __name__ == "__main__":
    # process_corporate()
    # process_corporate_alias()
    process_fullname()