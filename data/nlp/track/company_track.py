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
from basic_track import CompanyTracker

import json
from copy import deepcopy
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from difflib import ndiff


class CompanyNewsTracker(CompanyTracker):

    """
    track dimension 1
    """

    def __init__(self):

        CompanyTracker.__init__(self)
        self.default_check_period = 2

    def feed(self, cid, nid=None):

        if nid:
            records = list(self.mongo.article.news.find({'_id': ObjectId(nid)}))
        else:
            check_point = datetime.utcnow() - timedelta(hours=self.default_check_period)
            records = list(self.mongo.article.news.find({'modifyTime': {'$gte': check_point}, 'companyIds': cid}))

        # update_1001 = [item for item in self.feed_1001_1003_4tasks(records) if item]
        #
        # return update_1001

    def feed_1001_4tasks(self, records):

        for record in records:
            news_record = list(self.mongo.article.news.find({'_id': ObjectId(record['news_id'])}))[0]
            if news_record.get('date') and news_record['date'] < (datetime.now()-timedelta(days=self.news_timeliness)):
                continue
            # msg = ' '.join([item['content'] for item in news_record.get('contents', [])
            #                 if item.get('content', '').strip()])[:100]
            for cid in record.get('companyIds', []):
                if 578349 in record.get('categories', []):
                    continue
                else:
                    yield dbutil.update_company_message(self.db, cid, news_record.get('title', ''),
                                                        1001, 10, str(record['news_id'])), 'cm'
            for iid in record.get('investorIds', []):
                if 578350 in record.get('categories', []):
                    yield dbutil.update_investor_message(self.db, iid, news_record.get('title', ''),
                                                         1004, 10, record['news_id'], active='Y'), 'im'
                elif 578351 in record.get('categories', []):
                    yield dbutil.update_investor_message(self.db, iid, news_record.get('title', ''),
                                                         1005, 10, record['news_id'], active='Y'), 'im'
                else:
                    yield dbutil.update_investor_message(self.db, iid, news_record.get('title', ''),
                                                         1001, 10, record['news_id'], active='Y'), 'im'


class CompanyProductTracker(CompanyTracker):

    """
    track dimension 2
    """

    def __init__(self):

        CompanyTracker.__init__(self)
        self.max_2001_release_gap = 14

    def feed(self, cid, artifact_type='iOS', artifact_id=None):

        return

    def track_2001(self, logger=None):

        """
        update every day
        """
        yesterday = datetime.now() - timedelta(days=1)
        # day_gap = (datetime.now() - timedelta(days=self.max_2001_release_gap)).strftime('%Y-%m-%dT%H:%M:%SZ')
        day_gap = datetime.now() - timedelta(days=self.max_2001_release_gap)
        for aid, cid, atype, domain in dbutil.get_artifacts_by_date(self.db, yesterday):
            if logger:
                logger.info('Processing, aid %s, cid %s, type %s, domain %s' % (aid, cid, atype, domain))
            if not self.__valid_artifact_release_date(atype, domain, day_gap):
                return
            aname = dbutil.get_artifact_name(self.db, aid)
            msg = u'%s发现了一款新的%s应用 %s' % \
                  (dbutil.get_company_name(self.db, cid), dbutil.get_artifact_type(self.db, aid, string=True),
                   self.normalize_artifact_name(aname))
            feed_back = dbutil.update_daily_company_message(self.db, cid, msg, 2001, 20, aid, yesterday, comments=aname)
            if feed_back:
                self.send_company_message_msg(feed_back)
            if logger:
                logger.info('2001, %s, mysql: %s, check date %s' % (cid, feed_back, yesterday))

    def __valid_artifact_release_date(self, atype, domain, day_gap):

        if atype == 4040:
            release = self.mongo.market.itunes.find_one({'trackId': int(domain)}).get('releaseDate')
            cmp_date = day_gap.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            release = self.mongo.market.android.find_one({'apkname': domain}).get('updateDate')
            cmp_date = day_gap
        if release and release < cmp_date:
            return False
        return True

    def track_2002_2003(self, logger=None):

        """
        update every day
        """
        yesterday = datetime.now() - timedelta(days=1)

        # android
        # for record in list(self.mongo.market.android.find({'updateDate': {'$gt': yesterday, '$lte': datetime.now()},
        #                                                    'histories': {'$ne': None}})):
        for record in list(self.mongo.market.android.find({'modifyTime': {'$gt': yesterday, '$lte': datetime.now()},
                                                           'createTime': {'$lt': yesterday},
                                                           'histories': {'$ne': None}})):
            try:
                new_version = record.get('version')
                old_versions = [history.get('version') for history in record.get('histories', [])
                                if history.get('version')]
                for aid in dbutil.get_artifacts_from_apk(self.db, record['apkname']):
                    self.__process_artifact_2002_2003(aid, new_version, old_versions, yesterday, logger, u'Android')
            except Exception, e:
                if logger:
                    logger.exception('%s, %s' % (record['_id'], e))

        # iOS
        for record in list(self.mongo.market.itunes.find({'modifyTime': {'$gt': yesterday, '$lte': datetime.now()},
                                                          'createTime': {'$lt': yesterday},
                                                          'histories': {'$ne': None}})):
            try:
                new_version = record.get('version')
                old_versions = [history.get('version') for history in record.get('histories', [])
                                if history.get('version')]
                for aid in dbutil.get_artifacts_from_iOS(self.db, record['trackId']):
                    self.__process_artifact_2002_2003(aid, new_version, old_versions, yesterday, logger, u'iOS')
            except Exception, e:
                if logger:
                    logger.exception('%s, %s' % (record['_id'], e))

    def __process_artifact_2002_2003(self, aid, new_version, old_versions, yesterday, logger, market):

        cid = dbutil.get_artifact_company(self.db, aid)
        aname = dbutil.get_artifact_name(self.db, aid)
        if self.__import_update(new_version, old_versions):
            msg = u'%s的一款%s应用%s有重大版本%s更新' % \
                  (dbutil.get_company_name(self.db, cid), market, self.normalize_artifact_name(aname), new_version)
            feed_back = dbutil.update_detail_company_message(self.db, cid, msg, 2002, 20, aid, new_version,
                                                             comments='version: %s, %s' % (new_version, aname))
        else:
            msg = u'%s的一款%s应用%s发布了新版本%s' % \
                  (dbutil.get_company_name(self.db, cid), market, self.normalize_artifact_name(aname), new_version)
            feed_back = dbutil.update_detail_company_message(self.db, cid, msg, 2003, 20, aid, new_version,
                                                             comments='version: %s, %s' % (new_version, aname))
        if feed_back:
            self.send_company_message_msg(feed_back)
        if logger:
            logger.info('2002/2003, %s, mysql: %s' % (cid, feed_back))

    def __import_update(self, new_version, old_versions):

        try:
            if new_version and old_versions:
                new_version = int(str(new_version).split('.')[0] or -1)
                old_version = max([int(str(old_version).split('.')[0] or -1) for old_version in old_versions])
                if new_version and old_version and new_version > old_version:
                    return new_version
        except Exception, e:
            return False
        return False

    def track_2004(self, logger=None):

        """
        update every day
        """

        yesterday = datetime.now() - timedelta(days=1)
        for record in list(self.mongo.market.itunes.find({'offline_itunes': 'Y',
                                                          'offlineitunesDetectTime': {'$gt': yesterday}})):
            for aid in dbutil.get_artifacts_from_iOS(self.db, record['trackId']):
                cid = dbutil.get_artifact_company(self.db, aid)
                aname = dbutil.get_artifact_name(self.db, aid)
                msg = u'%s的一款iOS应用%s下架' % \
                      (dbutil.get_company_name(self.db, cid), self.normalize_artifact_name(aname))
                feed_back = dbutil.update_daily_company_message(self.db, cid, msg, 2004, 20, aid,
                                                                yesterday, comments=aname)
                if feed_back:
                    self.send_company_message_msg(feed_back)
                if logger:
                    logger.info('2004, %s, mysql: %s' % (cid, feed_back))

    def track_2005(self, logger=None):

        """
        推荐产品长期无更新
        update every day
        """

        ninety, ninety1 = datetime.now() - timedelta(days=90), datetime.now() - timedelta(days=91)
        yesterday = datetime.now() - timedelta(days=1)
        # android
        for record in self.mongo.market.android.find({'updateDate': {'$gt': ninety1, '$lt': ninety}}):
            for aid in dbutil.get_recommend_artifacts_from_domain(self.db, record['apkname']):
                self.__process_artifact_2005(aid, yesterday, logger)
        # iOS
        for record in self.mongo.market.itunes.find({'releaseDate': {'$gt': ninety1.strftime('%Y-%m-%d'),
                                                                     '$lt': ninety.strftime('%Y-%m-%d')}}):
            for aid in dbutil.get_recommend_artifacts_from_domain(self.db, record['trackId']):
                self.__process_artifact_2005(aid, yesterday, logger)

    def __process_artifact_2005(self, aid, yesterday, logger):

        cid = dbutil.get_artifact_company(self.db, aid)
        aname = dbutil.get_artifact_name(self.db, aid)
        msg = u'%s的一款%s应用%s超过90天未更新' % \
              (dbutil.get_company_name(self.db, cid), dbutil.get_artifact_type(self.db, aid, True),
               self.normalize_artifact_name(aname))
        feed_back = dbutil.update_daily_company_message(self.db, cid, msg, 2005, 20, aid, yesterday, comments=aname)
        if feed_back:
            self.send_company_message_msg(feed_back)
        if logger:
            logger.info('2005, %s, mysql: %s' % (cid, feed_back))


class CompanyRecruitTracker(CompanyTracker):

    """
    trak dimension 4
    update every week
    """

    def __init__(self):

        CompanyTracker.__init__(self)
        self.recruit_management = [title.lower() for title in dicts.get_recruit_managment()]

    def __load_jobs(self, cid):

        recruits = dbutil.get_company_recruitments(self.db, cid)
        if recruits:
            return list(self.mongo.job.job.find({'recruit_company_id': {'$in': recruits}}))
        return []

    def __load_recent_jobs(self, cid, period):

        check_date = datetime.today() - timedelta(days=period)
        recruits = dbutil.get_company_recruitments(self.db, cid)
        if recruits:
            return list(self.mongo.job.job.find({'recruit_company_id': {'$in': recruits},
                                                 'updateDate': {'$gt': check_date}}))
        return []

    def feed(self, cid, today=None):

        today = datetime.today() if not today else today

    def feed_4002(self, cid, today):

        """
        update everyday
        """

        jobs = self.__load_jobs(cid)
        if jobs:
            latest = max([job.get('updateDate') for job in jobs])
            if latest and latest < (today - timedelta(days=90)):
                msg = u'90天未发布新的招聘职位，最后招聘如下'
                job_ids = ','.join([str(job['_id']) for job in sorted(jobs,
                                                                      key=lambda x: x['updateDate'], reverse=True)[:3]])
                return dbutil.update_company_message(self.db, cid, msg, 4002, 40, job_ids)

    def feed_4004(self, cid, today):

        for job in self.__load_recent_jobs(cid, 1):
            if job.get('position', '').lower() in self.recruit_management:
                msg = u'%s正在招聘核心职位%s' % (dbutil.get_company_name(self.db, cid), job.get('position', ''))
                yield dbutil.update_company_message(self.db, cid, msg, 4004, 40, job['_id'])


class CompanyGongshangTracker(CompanyTracker):

    """
    track dimension 5
    """

    def __init__(self):

        CompanyTracker.__init__(self)
        self.default_last_check = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.alias = {alias: dbutil.get_investor_name(self.db, iid)
                      for iid, alias in dbutil.get_investor_gongshang_with_ids(self.db,
                                                                               *dbutil.get_online_investors(self.db))}
        self.online_vcs = dbutil.get_investor_gongshang_with_ids(self.db,
                                                                 *list(set(dbutil.get_online_investors(self.db))))

    def feed(self, cid, logger=None):

        mids, updates = [], []
        gongshangs = dbutil.get_company_gongshang_name(self.db, cid, True)
        gsv, gsnv = [gs[0] for gs in gongshangs if gs[1]], [gs[0] for gs in gongshangs if not gs[1]]
        # verified gongshang, track their changes
        if gsv:
            for record in self.mongo.info.gongshang.find({'name': {'$in': gsv},
                                                          'changeInfo': {'$ne': None}}):
                mids.extend([mid for mid in self.__feed_change(cid, record, True) if mid])
            for mid in mids:
                if logger:
                    logger.info('Track gongshang change, cid: %s, mid: %s' % (cid, mid))
                self.send_company_message_msg(mid)
        # not verified gongshang, generate gongshang task company
        if gsnv:
            for record in self.mongo.info.gongshang.find({'name': {'$in': gsnv}, 'changeInfo': {'$ne': None}}):
                updates.extend([update for update in self.__feed_change(cid, record, False) if update])
            if updates:
                if logger:
                    logger.info('Track gongshang change without name verify, cid: %s' % cid)
                diff = ','.join([u[1] for u in updates])
                comments = u'name: %s, index: %s' % \
                           (','.join(set([u[0] for u in updates])), diff)
                logger.info('Diff %s' % diff)
                flag_offline = True
                posting_time = datetime.now().strftime('%Y-%m-%d:%H:%M:%S')
                for vcid, alias in self.online_vcs:
                    if not flag_offline:
                        break
                    if alias in diff:
                        self.send_msg('task_company', json.dumps({'source': 'gongshang_unverified_online', 'id': cid,
                                                                  'detail': comments, 'posting_time': posting_time}))
                        flag_offline = False
                if flag_offline and (u'投资' in diff or u'基金' in diff):
                    self.send_msg('task_company',
                                  json.dumps({'source': 'gongshang_unverified_offline', 'id': cid, 'detail': comments,
                                              'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')}))

    def __feed_change(self, cid, record, direct_update=True):

        # no gongshang change
        if not record.get('changeInfo', False):
            return
        # has not calculate diff
        if not record.get('diffChecked', False):
            return

        # new gongshang without last check/ with old last check
        if (not record.get('lastCheckChange', False)) or \
                (cmp(self.default_last_check, record.get('lastCheckChange')) > 0):
            self.mongo.info.gongshang.update({'_id': record['_id']},
                                             {'$set': {'lastCheckChange': self.default_last_check}})

        if record.get('lastCheckChange', False) and record.get('changeInfo', False):
            cach = set()
            for change in [item for item in record.get('changeInfo', [])
                           if cmp(item.get('changeTime'), record.get('lastCheckChange')) >= 0]:
                # check if there are duplicated items
                change_copy = deepcopy(change)
                change_copy['id'] = 0
                change_copy = json.dumps(change_copy)
                if change_copy in cach:
                    continue
                cach.add(change_copy)
                holder_change = []
                if change.get('diffAfter', []):
                    diff_after = [(self.alias.get(diff, None) or diff) for diff in change.get('diffAfter', [])]
                    holder_change.append(u'增加了%s' % ', '.join(diff_after))
                if change.get('diffBefore', []):
                    holder_change.append(u'减少了%s' % ', '.join(change.get('diffBefore', [])))
                if holder_change:
                    if direct_update:
                        msg = ', '.join(holder_change)
                        yield dbutil.update_detail_company_message(self.db, cid, msg, 5001, 50, record['_id'],
                                                                   change.get('id', 0), change.get('changeTime'))
                    else:
                        yield record['name'], ','.join(change.get('diffAfter', []))
                try:
                    if u'注册资本' in change.get('changeItem', u''):
                        if direct_update:
                            msg = u'由%s变更为%s' % (change.get('contentBefore', ''), change.get('contentAfter', ''))
                            yield dbutil.update_detail_company_message(self.db, cid, msg, 5002, 50, record['_id'],
                                                                       change.get('id', 0), change.get('changeTime'))
                    # elif not direct_update:
                    #     yield record['name'], change.get('id', 0)
                except Exception, e:
                    print e

        # update last check change
        if direct_update:
            last_check_change = max([item.get('changeTime') for item in record.get('changeInfo', [])])
            self.mongo.info.gongshang.update({'_id': record['_id']}, {'$set': {'lastCheckChange': last_check_change}})

    def feed_invests(self):

        """
        check investors' new invests companies
        """
        vcs = {vc: iid
               for iid, vc in dbutil.get_investor_gongshang_with_ids(self.db, *dbutil.get_famous_investors(self.db))}
        for gongshang in self.mongo.info.gongshang.find({'name': {'$in': vcs.keys()}, 'invests': {'$ne': []}}):
            diffs = [i.get('name') for i in gongshang.get('invests', []) if i.get('new')]
            for diff in diffs:
                cids = dbutil.get_cid_from_gongshang(self.db, diff)
                # found one with gongshang change
                if cids:
                    self.send_msg('gongshang_detect', json.dumps({
                        'name': diff,
                        'type': 'update',
                        'investor_name': gongshang['name'],
                        'investor_id': vcs.get(gongshang['name']),
                        'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')
                    }))
                else:
                    self.send_msg('gongshang_detect', json.dumps({
                        'name': diff,
                        'type': 'new',
                        'investor_name': gongshang['name'],
                        'investor_id': vcs.get(gongshang['name']),
                        'posting_time': datetime.now().strftime('%Y-%m-%d:%H:%M:%S')
                    }))
                self.mongo.info.gongshang.update({'_id': gongshang['_id'], 'invests': {'$elemMatch': {'new': True}}},
                                                 {'$set': {'invests.$.new': False}}, False, True)


class CompanyCompsTracker(CompanyTracker):

    """
    track dimension 6, integrated into comps module
    """


class CompanyFundingTracker(CompanyTracker):

    def __init__(self):

        """
        track dimension 7
        :return:
        """
        CompanyTracker.__init__(self)

    def feed(self, cid, fid=None):

        pass


if __name__ == '__main__':

    print __file__
    gst = CompanyGongshangTracker()
    gst.feed_invests()
