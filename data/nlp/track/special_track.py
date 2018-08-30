# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
import config as tsbconfig
from common import dbutil, dicts

import re
import logging
import json
import socket
import pymongo
from abc import abstractmethod
from bson.objectid import ObjectId
from itertools import chain
from datetime import datetime, timedelta

from kafka import KafkaConsumer, KafkaClient, SimpleProducer
from kafka.errors import FailedPayloadsError

consumer_strack, producer_strack = None, None

# logging
logging.getLogger('special_track').handlers = []
logger_track = logging.getLogger('special_track')
logger_track.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_track.addHandler(stream_handler)

round_desc = {

    1000: '未融资',
    1010: '种子轮',
    1011: '天使轮',
    1020: 'Pre-A轮',
    1030: 'A轮',
    1031: 'A+轮',
    1039: 'Pre-B轮',
    1040: 'B轮',
    1041: 'B+轮',
    1050: 'C轮',
    1060: 'D轮',
    1070: 'E轮',
    1080: 'F轮',
    1090: '后期阶段',
    1100: 'Pre-IPO',
    1105: '新三板',
    1106: '新三板定增',
    1110: 'IPO',
    1120: '被收购',
    1130: '战略投资',
    1140: '私有化',
    1150: '债权融资',
    1160: '股权转让',
}


def init_kafka():

    global consumer_strack, producer_strack

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_strack = SimpleProducer(kafka)
    consumer_strack = KafkaConsumer("track_message", group_id="funding_track",
                                    bootstrap_servers=[url], auto_offset_reset='smallest')


def send_msg(mid, m_type):

    global producer_strack
    if not producer_strack:
        init_kafka()
    try:
        producer_strack.send_messages("track_message_v2",
                                      json.dumps({'id': mid, 'type': m_type, 'action': 'create', 'from': 'nlp'}))
    except FailedPayloadsError, fpe:
        init_kafka()
        producer_strack.send_messages("track_message_v2",
                                      json.dumps({'id': mid, 'type': m_type, 'action': 'create', 'from': 'nlp'}))


def send_customed_msg(topic, msg):

    global producer_strack
    if not producer_strack:
        init_kafka()
    try:
        producer_strack.send_messages(topic, msg)
    except FailedPayloadsError, fpe:
        init_kafka()
        producer_strack.send_messages(topic, msg)


def funding_relevant_track():

    global logger_track, consumer_strack, producer_strack
    socket.setdefaulttimeout(0.5)
    init_kafka()
    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    logger_track.info('Incremental generate track topic message of company')

    for message in consumer_strack:
        try:
            logger_track.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                             message.offset, message.key, message.value))
            ttype, topic = json.loads(message.value).get('type'), json.loads(message.value).get('topic_id')
            if not (ttype == 'track' and topic == 3):
                continue
            fid = json.loads(message.value).get('funding_id')
            funding = dbutil.get_funding(db, fid)
            if funding.active and funding.active == 'N':
                continue
            if not funding.get('publishDate', False):
                continue
            if funding.get('publishDate') < (datetime.now() - timedelta(days=7)):
                continue
            try:
                __topic_11(db, mongo, funding)
            except Exception, e:
                logger_track.exception('Topic 11 failed of %s, %s' % (funding.id, e))
            try:
                __topic_26(db, funding)
            except Exception, e:
                logger_track.exception('Topic 26 failed of %s, %s' % (funding.id, e))
            try:
                __topic_27(db, funding)
            except Exception, e:
                logger_track.exception('Topic 27 failed of %s, %s' % (funding.id, e))
            try:
                __topic_28(db, funding)
            except Exception, e:
                logger_track.exception('Topic 28 failed of %s, %s' %
                                       (funding.id, e))
            try:
                __topic_29(db, funding)
            except Exception, e:
                logger_track.exception('Topic 29 failed of %s, %s' % (funding.id, e))
            logger_track.info('Processsed %s, %s' % (json.loads(message.value).get('id'), fid))
        except Exception, e:
            logger_track.exception(e)


def __topic_11(db, mongo, funding):

    """
    独角兽，大额融资(超过10000w RMB)
    """

    global logger_track

    if not funding.newsId:
        return

    if funding.precise == 'Y':
        investment = {
            3010: 6.5,
            3020: 1,
            3030: 5,
            3040: 7,
            3050: 8,
            3070: 0.8
        }.get(funding['currency'], 0) * (funding.get('investment', 0) or 0)
    else:
        investment = funding.get('investment', 0)
    if investment >= 100000000:
        active = 'Y' if dbutil.get_topic_auto_pubilsh_status(db, 11) == 'Y' else 'P'
        title = list(mongo.article.news.find({'_id': ObjectId(funding.newsId)}))[0].get('title', '')
        tpm = dbutil.update_topic_message(db, 11, title, active, 10, funding.newsId)
        # if active == 'Y':
        if tpm:
            send_msg(tpm, 'topic_message')
            # for cid in dbutil.get_corporate_companies(db, funding.corporateId):
            tpc = dbutil.update_topic_company(db, 11, funding.companyId, active)
            if tpc:
                dbutil.update_topic_message_company(db, tpm, tpc)
            # if active == 'Y':
            send_msg(tpc, 'topic_company')
        logger_track.info('11 for %s, add tpm %s' % (funding.id, tpm))


def __topic_26(db, funding):

    """
    每日投融资速递
    """

    global logger_track, round_desc
    active = 'Y' if dbutil.get_topic_auto_pubilsh_status(db, 26) == 'Y' else 'P'
    # cid = dbutil.get_corporate_companies(db, funding.corporateId)[0]
    cid = funding.companyId
    if funding.round in (1105, 1110):
        msg = u'%s, %s%s上市' % \
              (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid), round_desc.get(funding.round))
    elif funding.round == 1120:
        msg = u'%s, %s%s' % \
              (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid), round_desc.get(funding.round))
    elif funding.round in (1106, 1130, 1140, 1150, 1160):
        msg = u'%s, %s完成了%s' % \
              (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid), round_desc.get(funding.round))
    elif funding.round == 0:
        msg = u'%s, %s完成了新一轮融资' % (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid))
    elif funding.round == 1111:
        msg = u'%s, %s完成了新一轮融资' % (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid))
    elif funding.round == 1131:
        msg = u'%s, %s完成了战略合并' % (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid))
    else:
        msg = u'%s, %s完成了%s融资' % \
              (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid), round_desc.get(funding.round))
    tpm = dbutil.update_topic_message(db, 26, msg, active, 70, funding.id)
    if tpm:
        send_msg(tpm, 'topic_message')
        tpc = dbutil.update_topic_company(db, 26, cid, active)
        if tpc:
            dbutil.update_topic_message_company(db, tpm, tpc)
        # if active == 'Y':
        send_msg(tpc, 'topic_company')
    logger_track.info('26 for %s, add tpm %s' % (funding.id, tpm))


def __topic_27(db, funding):

    """
    每日退出事件
    """

    global logger_track
    if funding.round and (funding.round == 1110 or funding.round == 1120):
        active = 'Y' if dbutil.get_topic_auto_pubilsh_status(db, 27) == 'Y' else 'P'
        # cid = dbutil.get_corporate_companies(db, funding.corporateId)[0]
        cid = funding.companyId
        if funding.round == 1120:
            msg = u'%s,%s被%s收购' % \
                  (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid), funding.investorsRaw)
        else:
            msg = u'%s,%s完成上市' % \
                  (dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid))
        tpm = dbutil.update_topic_message(db, 27, msg, active, 70, funding.id)
        if tpm:
            send_msg(tpm, 'topic_message')
            # for cid in dbutil.get_corporate_companies(db, funding.corporateId):
            tpc = dbutil.update_topic_company(db, 27, cid, active)
            # if active == 'Y':
            if tpc:
                dbutil.update_topic_message_company(db, tpm, tpc)
            send_msg(tpc, 'topic_company')
        logger_track.info('27 for %s, add tpm %s' % (funding.id, tpm))
    else:
        logger_track.info('27 not for %s' % funding.id)


def __topic_28(db, funding):

    """
    红杉真格经纬IDG
    114, 122, 125, 109
    """

    investors = set(dbutil.get_funding_investor_ids(db, funding.id)) & {114, 122, 125, 109}
    if investors:
        active = 'Y' if dbutil.get_topic_auto_pubilsh_status(db, 28) == 'Y' else 'P'
        # cid = dbutil.get_corporate_companies(db, funding.corporateId)[0]
        cid = funding.companyId
        investors = ','.join([dbutil.get_investor_name(db, iid) for iid in investors])
        msg = u'%s投资了%s,%s' % \
              (investors, dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid))
        tpm = dbutil.update_topic_message(db, 28, msg, active, 70, funding.id)
        # if active == 'Y':
        if tpm:
            send_msg(tpm, 'topic_message')
            # for cid in dbutil.get_corporate_companies(db, funding.corporateId):
            tpc = dbutil.update_topic_company(db, 28, cid, active)
            # if active == 'Y':
            if tpc:
                dbutil.update_topic_message_company(db, tpm, tpc)
            send_msg(tpc, 'topic_company')
        logger_track.info('28 for %s, add tpm %s' % (funding.id, tpm))
    else:
        logger_track.info('28 not for %s' % funding.id)


def __topic_29(db, funding):

    """
    BAT又在这些领域出手了
    187, 217, 117
    """

    investors = set(dbutil.get_funding_investor_ids(db, funding.id)) & {187, 217, 117}
    if investors:
        active = 'Y' if dbutil.get_topic_auto_pubilsh_status(db, 29) == 'Y' else 'P'
        cid = funding.companyId
        investors = ','.join([dbutil.get_investor_name(db, iid) for iid in investors])
        msg = u'%s投资了%s,%s' % \
              (investors, dbutil.get_company_brief(db, cid), dbutil.get_company_name(db, cid))
        tpm = dbutil.update_topic_message(db, 29, msg, active, 70, funding.id)
        # if active == 'Y':
        if tpm:
            send_msg(tpm, 'topic_message')
            tpc = dbutil.update_topic_company(db, 29, cid, active)
            if tpc:
                dbutil.update_topic_message_company(db, tpm, tpc)
            send_msg(tpc, 'topic_company')
        logger_track.info('29 for %s, add tpm %s' % (funding.id, tpm))
    else:
        logger_track.info('29 not for %s' % funding.id)


def company_news_track():

    # topic 9, gangs 779, 9, 218, round 579089
    # topic 10, gangs 579319, 290564
    global logger_track
    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    earlier = set(dbutil.get_company_from_tag(db, 579089))
    bats = [cid for cid in dbutil.get_company_from_tags(db, [779, 9, 218]) if cid in earlier]
    logger_track.info('Total bat %s' % len(bats))
    __update_company_news(db, mongo, bats, 9)
    logger_track.info('Topic 9, bats, done')
    pts = [cid for cid in dbutil.get_company_from_tags(db, [579319, 290564]) if cid in earlier]
    logger_track.info('Total pku thu %s' % len(pts))
    __update_company_news(db, mongo, pts, 10)
    logger_track.info('Topic 10, bats, done')


def __update_company_news(db, mongo, cids, tpid, content=u'发现一家公司', fund_extract=-5, detail_id=None, comments=None):

    for cid in cids:
        existed = dbutil.exist_topic_company(db, tpid, cid)
        tpc = dbutil.update_topic_company(db, tpid, cid, 'P')
        if tpc and not existed:
            nid = mongo.article.news.insert({
                'date': datetime.utcnow(),
                'createTime': datetime.utcnow(),
                'modifyTime': datetime.utcnow(),
                'title': dbutil.get_company_name(db, cid),
                'contents': [{
                    'content': content,
                    'rank': 1
                }],
                'type': 61000,
                'createUser': 139,
                'fund_extract': fund_extract,
                'processStatus': 2,
                'companyIds': [int(cid)],
                'companyCodes': [dbutil.get_company_code(db, cid)],
                'topic_id': tpid
            })
            send_msg(tpc, 'topic_company')
            tpm = dbutil.update_topic_message(db, tpid, dbutil.get_company_name(db, cid), 'P', 10,
                                              str(nid), detail_id, comments)
            dbutil.update_topic_message_company(db, tpm, tpc)
            send_msg(tpm, 'topic_message')


def gongshang_relevant_track():

    global logger_track
    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    init_kafka()
    yesterday = datetime.today() - timedelta(days=1)
    last_year = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    # topic 44, known vcs equals to online vcs
    online_vcs = dbutil.get_investor_gongshang_with_ids(db, *list(set(dbutil.get_online_investors(db))))
    # online_vcs.extend([(iid, dbutil.get_investor_name(db, iid)) for iid in set(dbutil.get_online_investors(db))])
    logger_track.info('Start to track gongshang for 44')
    for gongshang in db.query('select companyId, relateId, detailId, comments, message from company_message '
                              'where trackDimension=5001 and createTime>%s;', yesterday):
        # skip new detected old changes
        if gongshang.get('comments') and cmp(gongshang.get('comments'), last_year) < 1:
            continue
        ginfo = mongo.info.gongshang.find_one({'_id': ObjectId(gongshang.relateId)}).get('changeInfo', [])
        change = filter(lambda x: x.get('id', -1) == int(gongshang.detailId), ginfo)[0]
        for vcid, vc in online_vcs:
            if vc in change.get('contentAfter', '') and vc not in change.get('contentBefore', ''):
                msg = u'%s近期新增股东%s(%s)，推测其完成了新一轮融资' % \
                      (dbutil.get_company_name(db, gongshang.companyId), dbutil.get_investor_name(db, vcid), vc)
                __update_company_news(db, mongo, [gongshang.companyId], 44, msg, None,
                                      comments=change.get('changeTime'))

    # task company, verified gongshang change
    for gongshang in db.query('select companyId, relateId, detailId, comments, message from company_message '
                              'where trackDimension=5001 and createTime>%s;', yesterday):
        if gongshang.get('comments') and cmp(gongshang.get('comments'), last_year) < 1:
            continue
        diff = re.sub(u'减少了.*', u'', gongshang.get('message', ''))
        posting_time = datetime.now().strftime('%Y-%m-%d:%H:%M:%S')
        for vcid, vc in online_vcs:
            if vc in diff:
                send_customed_msg('task_company', json.dumps({'source': 'gongshang_verified_online',
                                                              'id': int(gongshang.get('companyId')),
                                                              'posting_time': posting_time,
                                                              'detail': diff}))
                logger_track.info('gongshang_verified_online, %s' % gongshang.get('companyId'))
                break
        else:
            if u'投资' in diff or u'基金' in diff:
                send_customed_msg('task_company', json.dumps({'source': 'gongshang_verified_offline',
                                                              'id': int(gongshang.get('companyId')),
                                                              'posting_time': posting_time, 'detail': diff}))
                logger_track.info('gongshang_verified_offline, %s' % gongshang.get('companyId'))


def fa_relevant_track():

    # topic52
    global logger_track
    db = dbcon.connect_torndb()
    day7 = datetime.now() - timedelta(days=7)
    for cid in dbutil.get_all_fund_raising(db):
        logger_track.info('Processing %s' % cid)
        brief = dbutil.get_company_brief(db, cid)
        msg = u'%s, %s开启了新一轮融资' % (brief, dbutil.get_company_name(db, cid))
        active = 'Y' if (dbutil.get_company_verify(db, cid) == 'Y' and brief) else 'P'
        tpm = dbutil.update_topic_message_withoutdup(db, 52, msg, active, 80,
                                                     dbutil.get_company_latest_fa(db, cid, day7), detail_id=cid)
        tpc = dbutil.update_topic_company(db, 52, cid, active)
        if tpm:
            dbutil.update_topic_message_company(db, tpm, tpc)
            send_msg(tpm, 'topic_message')
            send_msg(tpc, 'topic_company')
            logger_track.info('Updated %s' % cid)
    dbutil.update_last_message_time(db, 52)


def news_relevant_track():

    # topic 21(579435), 42(580641), 43(580642)
    global logger_track
    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    tag_topic_rel = {
        579435: 21,
        580641: 42,
        580642: 43
    }
    yesterday = datetime.today() - timedelta(days=60)
    for tag, topic in tag_topic_rel.iteritems():
        for news in mongo.article.news.find({'features': tag, 'createTime': {'$gt': yesterday}}):
            dbutil.update_topic_message(db, topic, news['title'], 'P', 10, news['_id'])
    db.close()


def test():

    global logger_track
    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    init_kafka()
    yesterday = datetime.today() - timedelta(days=2)
    last_year = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    # topic 44, known vcs equals to online vcs
    online_vcs = dbutil.get_investor_gongshang_with_ids(db, *list(set(dbutil.get_online_investors(db))))
    online_vcs.extend([(iid, dbutil.get_investor_name(db, iid)) for iid in set(dbutil.get_online_investors(db))])

    # task company, verified gongshang change
    for gongshang in db.query('select companyId, relateId, detailId, comments, message from company_message '
                              'where trackDimension=5001 and createTime>%s;', yesterday):
        if gongshang.companyId != 250061:
            continue
        else:
            print gongshang
        if gongshang.get('comments') and cmp(gongshang.get('comments'), last_year) < 1:
            print 'old'
            continue
        diff = re.sub(u'减少了.*', u'', gongshang.get('message', ''))
        print diff
        posting_time = datetime.now().strftime('%Y-%m-%d:%H:%M:%S')
        for vcid, vc in online_vcs:
            if vc in diff:
                print vc, vcid
                # send_customed_msg('task_company', json.dumps({'source': 'gongshang_verified_online',
                #                                               'id': int(gongshang.get('companyId')),
                #                                               'posting_time': posting_time}))
                # logger_track.info('gongshang_verified_online, %s' % gongshang.get('companyId'))
                break
        else:
            if u'投资' in diff or u'基金' in diff:
                print u'投资'
                # send_customed_msg('task_company', json.dumps({'source': 'gongshang_verified_offline',
                #                                               'id': int(gongshang.get('companyId')),
                #                                               'posting_time': posting_time}))
                # logger_track.info('gongshang_verified_offline, %s' % gongshang.get('companyId'))
                break


if __name__ == '__main__':

    if sys.argv[1] == 'funding':
        funding_relevant_track()
    if sys.argv[1] == 'company':
        init_kafka()
        company_news_track()
    if sys.argv[1] == 'gongshang':
        gongshang_relevant_track()
    if sys.argv[1] == 'fundraising':
        fa_relevant_track()
    if sys.argv[1] == 'news':
        news_relevant_track()
    if sys.argv[1] == 'test':
        test()
