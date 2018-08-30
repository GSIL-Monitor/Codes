# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil
from keywords.key import Extractor
from recommend.push import SourcingPusher

import time
import logging
from itertools import chain
from pymongo import DESCENDING
from bson.objectid import ObjectId
from datetime import datetime, timedelta

# logging
logging.getLogger('soucing').handlers = []
loggers = logging.getLogger('soucing')
loggers.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
loggers.addHandler(stream_handler)


def source_yuanma():

    global loggers
    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    day_seven = today - timedelta(days=7)

    # clear undone tasks
    # if today.weekday() == 0:
    #     dbutil.mark_sourcing_done(db)

    # news
    try:
        __source_news(db, mongo, today, yesterday)
        loggers.info('News source ready')
    except Exception, e:
        loggers.info('News source failed, due to, %s' % e)

    # database
    try:
        __source_database(db, mongo, yesterday, day_seven)
        loggers.info('Database source ready')
    except Exception, e:
        loggers.info('Database source failed, due to, %s' % e)

    # gongshang
    try:
        __source_gongshang(db, mongo, yesterday)
        loggers.info('Gongshang source ready')
    except Exception, e:
        loggers.info('Gongshang source failed, due to, %s' % e)

    # funding
    try:
        __source_funding(db, yesterday)
        loggers.info('Funding source ready')
    except Exception, e:
        loggers.info('Funding source failed, due to, %s' % e)

    # update regular sourcing company, no dup recommend for 7 days
    for ces in db.query('select distinct companyId from company_extract_source where createTime>=%s;', today):
        dbutil.update_sourcing_company(db, ces.companyId, day_seven)
    loggers.info('Regular Sourcing company ready')
    # update custom sourcing company
    try:
        __source_module_71001(db, mongo, yesterday, day_seven)
        loggers.info('71001 custom sourcing company ready')
    except Exception, e:
        loggers.exception('71001 failed, due to, %s' % e)
    dbutil.clear_sourcing_company(db)
    loggers.info('Invalid sourcing company cleared')

    # progress
    process_progress(db)
    loggers.info('Progress processed')

    # push to 214, 215 and 1091 to check
    sp = SourcingPusher()
    sp.push_sb(214)
    sp.push_sb(215)
    sp.push_sb(6936)
    sp.push_sb(12474)
    sp.push_sb(12122)
    loggers.info('Pre check generated')

    # push to others
    time.sleep(3600)
    dbutil.clear_sourcing_company(db)
    sp = SourcingPusher()
    for oid in dbutil.get_sourcing_organizations(db):
        try:
            sp.push(oid)
        except Exception, e:
            loggers.exception('Fail to push for %s, due to %s' % (oid, e))
    loggers.info('Push Done')


def process_progress(db):

    mongo = dbcon.connect_mongo()
    for c in db.query('select * from sourcing_company_user_rel where (active is null or active="Y") '
                      'order by id desc limit 10000;'):
        db.execute('update sourcing_company_user_rel '
                   'set newsProgress=null, gongshangProgress=null, fundingProgress=null where id=%s;', c.id)
        for progress in db.query('select * from company_message where trackDimension in (1001, 5001, 5002) '
                                 'and (active is null or active="Y") and companyId=%s and publishTime>%s;',
                                 c.companyId, c.createTime + timedelta(days=60)):
            if progress.trackDimension / 1000 == 1:
                publish = mongo.article.news.find_one({'_id': ObjectId(progress.relateId)}).get('date')
                if publish and publish < (c.createTime + timedelta(days=60)):
                    continue
                db.execute('update sourcing_company_user_rel set newsProgress="Y" where id=%s;', c.id)
            elif progress.trackDimension / 1000 == 5:
                full = dbutil.get_company_corporate_name(db, progress.companyId, False)
                if full:
                    change = (mongo.info.gongshang.find_one({'name': full}) or {}).get('changeInfo', [])
                    change = [cg for cg in change if cg.get('id') == int(progress.detailId)]
                    if change and len(change) > 0:
                        change_time = change[0].get('changeTime')
                        day60 = c.createTime + timedelta(days=60)
                        if change_time and datetime.strptime(change_time, '%Y-%m-%d') > day60:
                            db.execute('update sourcing_company_user_rel set gongshangProgress="Y" where id=%s;', c.id)
        if db.get('select count(*) c from funding where companyId=%s and fundingDate>%s and '
                  '(active is null or active="Y");', c.companyId, c.createTime + timedelta(days=60)).c > 0:
            db.execute('update sourcing_company_user_rel set fundingProgress="Y" where id=%s;', c.id)


def __source_news(db, mongo, today, yesterday):

    bad_news = [r.get('companyIds', []) for r in mongo.article.news.find({'createTime': {'$gt': yesterday,
                                                                                         '$lt': today},
                                                                          'processStatus': 1, 'type': 60001,
                                                                          'features': {'$ne': 578362},
                                                                          'modifyUser': {'$ne': 139}})]
    bad_news = set(chain(*bad_news))
    for record in mongo.article.news.find({'createTime': {'$gt': yesterday, '$lt': today}, 'processStatus': 1,
                                           'type': 60001, 'features': {'$ne': 578362}, 'modifyUser': {'$ne': 139}}):
        for cid in record.get('companyIds', []):
            if cid == 449316 or cid == 416649:
                dbutil.update_extract_source_company(db, 67002, record['source'], cid, record['_id'], False)
            if cid in bad_news:
                continue
            if dbutil.get_company_round(db, cid) > 1040:
                continue
            if dbutil.get_company_establish_date(db, cid).year < 2010:
                continue
            dbutil.update_extract_source_company(db, 67002, record['source'], cid, record['_id'], False)


def __source_database(db, mongo, yesterday, day_seven):

    aggregates = [item.get('newCorporateIds', [])
                  for item in mongo.task.corporate_decompose.find({'modifyTime': {'$gt': day_seven}})]
    aggregates = set(chain(*aggregates))
    for c in db.query('select company.id id, source_company.source source from company, source_company '
                      'where company.createTime>%s and company.modifyTime>%s and company.id=source_company.companyId '
                      'and (company.active is null or company.active="Y") and '
                      '(source_company.active is null or source_company.active="Y");', day_seven, yesterday):
        if dbutil.get_company_round(db, c.id) > 1040:
            continue
        if dbutil.get_company_establish_date(db, c.id).year < 2016:
            continue
        if dbutil.get_company_corporate_id(db, c.id) in aggregates:
            continue
        if dbutil.get_company_source(db, c.id) == set([13050]):
            continue
        dbutil.update_extract_source_company(db, 67001, c.source, c.id, only_insert=False)


def __source_gongshang(db, mongo, yesterday):

    global loggers
    known_vcs = dbutil.get_investor_alias_with_ids(db, *dbutil.get_famous_investors(db))
    for tpc in db.query('select * from topic_company where topicId=44 and (active is null or active="Y") '
                        'and publishTime>%s', yesterday):
        gongshang = db.get('select relateId, detailId from company_message where trackDimension=5001 and companyId=%s '
                           'order by publishTime desc limit 1', tpc.companyId)
        try:
            changes = {}
            ginfo = mongo.info.gongshang.find_one({'_id': ObjectId(gongshang.relateId)}).get('changeInfo', [])
            change = filter(lambda x: x.get('id', -1) == int(gongshang.detailId), ginfo)[0]
            for iid, vc in known_vcs:
                if vc in change.get('contentAfter', '') and vc not in change.get('contentBefore', ''):
                    changes.setdefault(tpc.companyId, []).append(iid)
            for cid, iids in changes.items():
                inames = ','.join([dbutil.get_investor_name(db, iid) for iid in set(iids)])
                dbutil.update_extract_source_company(db, 67003, None, cid, gongshang.relateId, True, inames)
        except Exception, e:
            loggers.exception('Failed gongshang, %s, %s' % (tpc.companyId, e))


def __source_funding(db, yesterday):

    for c in db.query('select company.id cid, relateId from company, funding, topic_message '
                      'where topicId=26 and topic_message.publishTime>%s and topic_message.active="Y" and '
                      'company.corporateId=funding.corporateId and funding.id=topic_message.relateId and '
                      '(company.active is null or company.active="Y") and funding.round not in (1105, 1106, 1110, 1120)'
                      ' and (funding.active is null or funding.active="Y");', yesterday):
        dbutil.update_extract_source_company(db, 67004, None, c.cid, c.relateId, only_insert=False)


# def __source_module_71001(db, mongo, yesterday, day_seven):
#
#     aggregates = [item.get('newCorporateIds', [])
#                   for item in mongo.task.corporate_decompose.find({'modifyTime': {'$gt': day_seven}})]
#     aggregates = set(chain(*aggregates))
#     ke = Extractor()
#     for c in db.query('select distinct company.id id, source_company.source source from company, source_company '
#                       'where company.createTime>%s and company.id=source_company.companyId '
#                       'and source=13050 and (source_company.active is null or source_company.active="Y") '
#                       'and source_company.roundDesc in ("A轮", "天使轮", "Pre-A", "尚未获投", "未融资") '
#                       'and source_company.description is not null;', yesterday):
#         # if dbutil.get_company_round(db, c.id) > 1040:
#         #     continue
#         # if dbutil.get_company_establish_date(db, c.id).year < 2016:
#         #     continue
#         if dbutil.get_company_corporate_id(db, c.id) in aggregates:
#             continue
#         if dbutil.get_company_score(db, c.id, 37040) < 4:
#             continue
#         if dbutil.get_company_source(db, c.id) == {13050}:
#             ke.extract(c.id)
#             dbutil.update_extract_source_company(db, 67001, c.source, c.id, only_insert=False, allow_no_publish=True)
#             dbutil.update_custom_sourcing_company(db, c.id, 71001, day_seven)


def __source_module_71001(db, mongo, yesterday, day_seven):

    aggregates = [item.get('newCorporateIds', [])
                  for item in mongo.task.corporate_decompose.find({'modifyTime': {'$gt': day_seven}})]
    aggregates = set(chain(*aggregates))
    # for c in db.query('select company.id id, source_company.source source from company, source_company '
    #                   'where company.createTime>%s and company.modifyTime>%s and company.id=source_company.companyId '
    #                   'and (company.active is null or company.active="Y") and '
    #                   '(source_company.active is null or source_company.active="Y");', day_seven, yesterday):
    for tc in mongo.task.company.find({'finishTime': {'$gte': yesterday}, 'processStatus': 1, 'types': 'company_job'}):
        cid = tc.get('companyId')
        if dbutil.get_company_active(db, cid) == 'Y':
            if dbutil.get_company_round(db, cid) > 1040:
                continue
            # if dbutil.get_company_establish_date(db, cid).year < 2000:
            #     continue
            # if dbutil.get_company_corporate_id(db, cid) in aggregates:
            #     continue
            if dbutil.get_company_source(db, cid) == {13050}:
                dbutil.update_extract_source_company(db, 67001, 13050, cid, only_insert=False)
                dbutil.update_custom_sourcing_company(db, cid, 71001, day_seven)


def test():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    __source_gongshang(db, mongo, yesterday)


if __name__ == '__main__':

    print __file__
    # db = dbcon.connect_torndb()
    # process_progress(db)
    source_yuanma()
