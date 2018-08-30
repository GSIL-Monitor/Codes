# -*- encoding=utf-8 -*-
__author__ = "kailu"


import os
import sys
import logging
from datetime import datetime, timedelta
from collections import Counter

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from weixin_log_helper import WeChator
from common import dbutil

logging.getLogger('media_hot').handlers = []
logger_media = logging.getLogger('media_hot')
logger_media.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_media.addHandler(stream_handler)


mongo = dbcon.connect_mongo()
db = dbcon.connect_torndb()


# t1, t2 datetime type
def get_news_cr(mongo, t1, t2):
    cr = mongo.article.news.find({"companyIds":{"$exists":True}, "date":{"$gt":t1, "$lt":t2}, "type":{"$ne": 61000}})
    return cr

def company_score(db, cid):
    r = db.query("select score from company_scores where type=37010 and companyid=%s;", cid)
    if r:
        return r[0]["score"]
    return -1.0

def company_info(db, cid):
    r = db.query("select code, name from company where (active is null or active='Y') and id = %s;", cid)
    if r:
        return r[0]
    return 0

def count_company_news(db, mongo, t1, t2):
    cr = get_news_cr(mongo, t1, t2)
    ci_list = []
    for row in cr:
        ci_list.extend(row['companyIds'])
    ct = Counter(ci_list)
    return ct


def get_hot_list(start_date, end_date, default_percentage=5):
    ct = count_company_news(db, mongo, start_date, end_date)
    amount = len(ct) * default_percentage / 100 + 1
    hot_list = []
    for key, value in ct.most_common(amount):
        d = company_info(db, key)
        if not d:
            continue
        score = company_score(db, key)
        if score >= 0.4:
            hot_list.append(key)
    return hot_list


def do():
    end_date= datetime.today()
    start_date = end_date - timedelta(30)
    hot_list = get_hot_list(start_date, end_date)
    # 媒体热议 tagid
    db.execute("delete from company_tag_rel where tagId=573515 and (verify is null or verify = 'N');")

    # 媒体热议检测列表 collectionid 1822
    db.execute("delete from collection_company_rel where collectionid = 1822;")
    for cid in hot_list:
        r = dbutil.update_company_tag(db, cid, 573515, 9.0001)
        logger_media.info('Hot_media: %s insert' % cid)

        if r:
            db.execute("insert into collection_company_rel(collectionid, companyid, active, createuser, createtime) values (1822, %s, 'Y', 139, now());", cid)


if __name__ == "__main__":
    do()

    # try:
    #     wechat_instance = WeChator()
    #     msg = "Media hot company has been updated, check the list on http://www.xiniudata.com/#/custom/1822"
    #     username = wechat_instance.get_chatroom_username("xiniu")
    #     wechat_instance.send_msg(msg, username)
    # except Exception as e:
    #     print e
