# -*- coding: utf-8 -*-
import os, sys, re, json
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util
import db

#logger
loghelper.init_logger("remove_dup_member", stream=True)
logger = loghelper.get_logger("remove_dup_member")



if __name__ == "__main__":
    start = 0
    num = 0
    cid = 0
    while True:
        conn = db.connect_torndb()
        members = list(conn.query("select * from member where (active is null or active='Y')"))
        if len(members) == 0:
            break

        for member in members:
            if member["description"] is not None and member["description"].find("未收录相关信息")>=0:
                logger.info("wrong desc: %s",member["description"])
                desc = member["description"].replace("未收录相关信息","").strip()
                logger.info("new desc: %s", desc)
                if desc=="": conn.update("update member set description=null where id=%s", member["id"])
                else: conn.update("update member set description=%s where id=%s", desc, member["id"])

        conn.close()
        break


