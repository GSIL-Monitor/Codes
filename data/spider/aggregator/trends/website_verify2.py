# -*- coding: utf-8 -*-
import sys, os
import datetime, time
import json, re
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config
import loghelper
import requests
from pyquery import PyQuery as pq


#logger
loghelper.init_logger("artifact_verify2", stream=True)
logger = loghelper.get_logger("artifact_verify2")

cnt = 0

def get_website(websites):
    global cnt
    for website in websites:
        try:
            r = requests.get(website['link'], timeout= 10)
            if r.status_code != 200:
                delete(website)
            else:
                r.encoding = r.apparent_encoding
                html = r.text
                doc = pq(html)
                metas = doc('meta')
                description = None
                keywords = None
                for meta in metas:
                    name =  pq(meta).attr('name')
                    content =  pq(meta).attr('content')
                    if name == 'keywords':
                        keywords = content
                    if name == 'description':
                        description = content

                update(description, keywords, website)
        except:
            delete(website)

    cnt += 1000
    begin()


def update(description, keywords, website):
    logger.info("updating ...  id=%s", website['id'])
    if keywords is not None:
        if len(keywords) > 200:
            keywords = keywords[:199]

    logger.info(description)
    logger.info(keywords)

    conn = db.connect_torndb()
    if description is None and keywords is None:
        update_sql = "update artifact set active='Y' where id=%s"
        conn.update(update_sql, website['id'])
    else:
        if website['description'] is not None:
            update_sql = "update artifact set tags=%s, active='Y' where id=%s"
            conn.update(update_sql, keywords, website['id'])
        else:
            update_sql = "update artifact set description=%s, tags=%s, active='Y' where id=%s"
            conn.update(update_sql, description, keywords, website['id'])
    conn.close()



def delete(website):
    logger.info("deleting ...  id=%s", website['id'])
    conn = db.connect_torndb()
    update_sql = "update artifact set verify = 'N', active='N' where id=%s"
    conn.update(update_sql, website['id'])
    conn.close()


def begin():
    global cnt
    conn = db.connect_torndb()

    websites = conn.query("select * from artifact where type = 4010 and active='Y' and rank > 1000000 limit %s,1000", cnt)
    logger.info('Done count = %s', cnt)
    if len(websites) == 0:
        logger.info("Finish.")
        exit()
    get_website(websites)
    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    begin()
