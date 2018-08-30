# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("artifact_correct", stream=True)
logger = loghelper.get_logger("artifact_correct")


def weibo():
    id = -1
    conn = db.connect_torndb()
    while True:
        ars = conn.query("select * from artifact where type=4030 and verify is null and id>%s order by id limit 1000", id)
        if len(ars) == 0:
            break
        for a in ars:
            artifact_id = a["id"]
            # logger.info(a["link"])
            if artifact_id > id:
                id = artifact_id
            link = a["link"]
            if link is None:
                continue
            new_link = link.replace("：","").replace("http://http://","http://").replace("www.weibo.com","weibo.com")
            new_link = new_link.replace("http://weibo.cn/","http://weibo.com/")
            if "http://weibo.com/" not in new_link:
                new_link = ""
            pos = new_link.find("?")
            if pos >= 0:
                new_link = new_link[0:pos]
            if new_link.endswith("/home"):
                new_link = new_link[:-5]
            if new_link != link and new_link != "":
                logger.info("%s -> %s", link, new_link)
                conn.update("update artifact set link=%s where id=%s", new_link, artifact_id)
    conn.close()


def wechat():
    id = -1
    conn = db.connect_torndb()
    while True:
        ars = conn.query("select * from artifact where type=4020 and verify is null and id>%s order by id limit 1000", id)
        if len(ars) == 0:
            break
        for a in ars:
            artifact_id = a["id"]
            # logger.info(a["link"])
            if artifact_id > id:
                id = artifact_id
            domain = a["domain"]
            link = a["link"]
            if domain is None and link is not None and "http://" not in link:
                logger.info(link)
                conn.update("update artifact set domain=%s where id=%s", link, artifact_id)
            # if domain is not None and "http://" in domain:
            #     logger.info(domain)
            #     conn.update("update artifact set domain=null where id=%s", artifact_id)
    conn.close()

if __name__ == "__main__":
    # weibo()
    wechat()