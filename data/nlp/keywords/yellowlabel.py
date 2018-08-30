# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
import config as tsbconfig
from common import dbutil, dicts
from score.downloads import black_android_all
from score.person import FounderScorer
from score.job import summary_recruit_all
from score.android import recent_android_increase_rapidly_all

import json
import logging
from kafka import KafkaClient, SimpleProducer
from kafka.errors import FailedPayloadsError

"""
assigin yellow label tag to companies, including
1. android black horse
2. recruit black horse
3. outstanding team/founders
4. famous angel fund
5. popular sector
"""

# logging
logging.getLogger('yl').handlers = []
logger_yl = logging.getLogger('yl')
logger_yl.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_yl.addHandler(stream_handler)


producer_tag = None


def init_kafka():

    global producer_tag
    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_tag = SimpleProducer(kafka)


def classify_android_black():

    global logger_yl, producer_tag
    init_kafka()
    db = dbcon.connect_torndb()
    # for cid, score in black_android_all().iteritems():
    # for cid, aid, score in recent_android_increase_rapidly_all():
    for cid, aid, score, source in dbutil.get_android_explosion(db):
        if dbutil.get_company_establish_date(db, cid).year < 2006:
            continue
        try:
            # 309126 下载激增
            dbutil.update_company_tag(db, cid, 309126, score, "Y")
            dbutil.mark_android_explosion(db, aid)
            dbutil.update_company_tag_comment(db, cid, 309126, 30, aid, source)
            msg = u'%s旗下Android产品近期下载量激增' % dbutil.get_company_name(db, cid)
            dbutil.update_continuous_company_message(db, cid, msg, 3201, 30, aid, 14, source)
            producer_msg = {"id": cid}
            producer_tag.send_messages("keyword_v2", json.dumps(producer_msg))
            logger_yl.info('Android Explosion Artifact: company %s, artifact %s' % (cid, aid))
        except Exception, e:
            logger_yl.exception('Failed Android Explosion Artifact: company %s, artifact %s ' % (cid, aid))
    db.close()


def classify_artifact_fast_iter():

    # 644378, 产品迭代快
    global logger_yl
    db = dbcon.connect_torndb()
    for (cid, score) in dbutil.get_fast_iter_artifact(db):
        try:
            dbutil.update_company_tag(db, cid, 644378, score, 'P', 'N')
            logger_yl.info('Artifact iter fast: company %s' % cid)
        except Exception, e:
            logger_yl.exception('Failed Artifact fast iteration, company %s' % cid)
    db.close()


def classify_recuit_black():

    global logger_yl
    db = dbcon.connect_torndb()
    for cid, score in summary_recruit_all():
        try:
            # 309127 招聘活跃
            dbutil.update_company_tag(db, cid, 309127, score, "Y")
            logger_yl.info('Black recruit: %s insert' % cid)
        except Exception, e:
            logger_yl.exception('Black recruit: %s failed # %s' % (cid, e))
    db.close()


def classify_founder():

    global logger_yl
    db = dbcon.connect_torndb()
    fs = FounderScorer()
    for cid in iter(dbutil.get_all_company_id(db)):
        score = fs.score(cid)
        if score >= 0.5:
            # 309128 团队优秀
            dbutil.update_company_tag(db, cid, 309128, score, "Y")
            logger_yl.info('Outstanding team: %s insert' % cid)
        # if fs.has_QBFJ(cid):
        #     # 清北复交团队
        #     logger_yl.info('Has QBFJ: %s insert' % cid)
        # if fs.has_overseas(cid):
        #     # 海归团队
        #     logger_yl.info('Has overseas: %s insert' % cid)
        # if fs.has_serial_entrepreneur(cid):
        #     # 连续创业者
        #     logger_yl.info('Has serial entrepreneur' % cid)
    db.close()


def classify_angel():

    global logger_yl
    db = dbcon.connect_torndb()
    known_angels = dicts.get_known_angels()
    dbutil.clear_tag(db, 309129)
    for cid in dbutil.get_companies_from_investors(db, *known_angels):
        # 309129 知名风投
        dbutil.update_company_tag(db, cid, 309129, 1, "Y")
        logger_yl.info('Known angel: %s insert' % cid)
    db.close()


def classify_known_media_full():

    global logger_yl
    db = dbcon.connect_torndb()


if __name__ == '__main__':

    if sys.argv[1] == 'all' or sys.argv[1] == '0':
        db = dbcon.connect_torndb()
        dbutil.clear_yellow_label(db)
        logger_yl.info('Old yellow cleared')
        db.close()
        classify_founder()
        classify_recuit_black()
        classify_android_black()
        classify_angel()
    elif sys.argv[1] == 'android' or sys.argv[1] == '1':
        classify_android_black()
    elif sys.argv[1] == 'recruit' or sys.argv[1] == '2':
        classify_recuit_black()
    elif sys.argv[1] == 'founder' or sys.argv[1] == '3':
        classify_founder()
    elif sys.argv[1] == 'angel' or sys.argv[1] == '4':
        classify_angel()
    elif sys.argv[1] == 'iteration' or sys.argv[1] == '5':
        classify_artifact_fast_iter()
