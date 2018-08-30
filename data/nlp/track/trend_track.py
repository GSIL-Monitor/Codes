# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from basic_track import CompanyTracker
from common import dbutil, dicts
from score.downloads import summary_android_all

import json
import codecs
import logging
from datetime import datetime, timedelta

# logging
logging.getLogger('track').handlers = []
logger_track = logging.getLogger('track')
logger_track.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_track.addHandler(stream_handler)


class AndroidUpdateCompanyTracker(CompanyTracker):

    """
    update every day
        check whether there is big version update of android app
    """

    def __init__(self):

        CompanyTracker.__init__(self)

    def feed(self, cid, today=None):

        today = datetime.today() if not today else today
        for apk in dbutil.get_artifact_from_cid(self.db, cid, 4050):
            if apk.domain and self.__feeda(apk.domain, today):
                self.mongo.track.track.insert({
                    'topic': 4,
                    'companyId': cid,
                    'abstract': u'%s旗下Android产品有大的版本更新' % dbutil.get_company_name(self.db, cid),
                    'createTime': today
                })

    def __feeda(self, apkname, today):

        results = self.mongo.market.android.find({'updateDate': {'$gt': (today - timedelta(hours=24)), '$lte': today},
                                                  'apkname': apkname, 'histories': {'$ne': None}})
        for result in results:
            new_version = int(result.get('version', '').split('.')[0] or -1)
            old_version = max([
                int(history.get('version', '').split('.')[0] or -1) for history in result.get('history', [])
            ])
            if new_version and old_version and new_version > old_version:
                return new_version
        return False


class AndroidOperationCompanyTracker(CompanyTracker):

    """
    update every 7 days
    """

    def __init__(self):

        CompanyTracker.__init__(self)
        self.abstract = u'与同类产品相比，%s Android数据表现 %s'

    def update_all(self, today=None):

        global logger_track
        today = datetime.today() if not today else today
        for cid, update in summary_android_all():
            try:
                abstract = self.abstract % (dbutil.get_company_name(self.db, cid), self.__judge(update))
                self.mongo.track.track.insert({'topic_id': 5,
                                               'company_id': cid,
                                               'abstract': abstract,
                                               'createTime': today})
            except Exception, e:
                logger_track.exception('%s c5.1 exception, %s' % (cid, e))

    def __judge(self, update):

        score = update[1] - update[0]
        if score >= 30:
            return u'大幅下降'
        elif score > 0:
            return u'略有下降'
        elif score >= -40:
            return u'略有提升'
        else:
            return u'显著提升'


class AppStoreRankCompanyTracker(CompanyTracker):

    """
    update every day at 21:00
    """

    def __init__(self):

        CompanyTracker.__init__(self)
        self.abstract = u'%s iOS榜单入围'
        self.rank_category = self.__load_rank_names()
        self.rank_catlog = {
            'free': u'免费榜',
            'grossing': u'畅销榜',
            'charge': u'收费榜'
        }

    def update_app_rank(self, today=None):

        global logger_track
        today = datetime.today() if not today else today
        logger_track.info('Start to process app rank track for %s' % str(today))
        todays = list(self.mongo.trend.appstore_rank.find({'date': {'$gt': (today-timedelta(days=1)), '$lte': today},
                                                           'rank': {'$lte': 100}}))
        # data of today is not ready
        if len(filter(lambda x: x.get('rank', 0) == 1, todays)) < 120:
            logger_track.info('Data of today is not ready yet')
            return
        yesterdays = list(self.mongo.trend.appstore_rank.find({'date': {'$gt': (today-timedelta(days=2)),
                                                                        '$lt': (today-timedelta(days=1))},
                                                               'rank': {'$lte': 100}}))
        # add 11110 tag
        self.update_tag_11110(todays)

        if len(todays) == 0 or len(yesterdays) == 0:
            logger_track.info('Data fetch error, with today %s, yesterday %s' % (len(todays), len(yesterdays)))
        return {3107: list(self.update_3107(todays, yesterdays, today)),
                3108: list(self.update_3108(todays, yesterdays, today))}

        # self.update_3107(todays, yesterdays, today)

    def update_tag_11110(self, todays):

        dbutil.clear_label(self.db, 579409, 579410)
        for item in todays:
            if item.get('rank', 10000) < 51:
                tid = 579409 if item.get('genre') is None else 579410
                for aid in dbutil.get_artifacts_from_iOS(self.db, item['trackId']):
                    cid = dbutil.get_artifact_company(self.db, aid)
                    dbutil.update_company_tag(self.db, cid, tid, 0, active='H')
                    detailid = '%s,%s' % (item['genre'], item['type'])
                    dbutil.update_company_tag_comment(self.db, cid, tid, 30, aid, detailid)
                    self.send_topic_company_msg(cid, False)

    def update_3107(self, todays, yesterdays, today):

        global logger_track
        newin = {}
        yesterdays = set(item['trackId'] for item in yesterdays)
        day_thirday = today - timedelta(days=30)
        for item in filter(lambda x: x['trackId'] not in yesterdays, todays):
            self.mongo.temp.appstore.insert_one({'type': 3017, 'createTime': today, 'item': item})
            for aid in dbutil.get_artifacts_from_iOS(self.db, item['trackId']):
                newin[aid] = item
        for aid, item in newin.items():
            cid = dbutil.get_artifact_company(self.db, aid)
            msg = u'%s旗下 %s入围iOS榜单，位列%s第%s名' % \
                  (dbutil.get_company_name(self.db, cid),
                   self.__normalize_iOS_name(dbutil.get_artifact_name(self.db, aid)),
                   self.__get_rank_name(item['genre'], item['type']), item['rank'])
            detail = '%s,%s' % (item['genre'], item['type'])
            comments = dbutil.get_artifact_name(self.db, aid)
            yield dbutil.update_daily_company_message(self.db, cid, msg, 3107, 30, aid, day_thirday, detail, comments)
            logger_track.info('3107, %s, %s' % (cid, aid))

    def update_3108(self, todays, yesterdays, today):

        global logger_track
        newout = {}
        todays = set(item['trackId'] for item in todays)
        day_thirday = today - timedelta(days=30)
        for item in filter(lambda x: x['trackId'] not in todays, yesterdays):
            self.mongo.temp.appstore.insert_one({'type': 3108, 'createTime': today, 'item': item})
            for aid in dbutil.get_artifacts_from_iOS(self.db, item['trackId']):
                newout[aid] = item
        for aid, item in newout.items():
            cid = dbutil.get_artifact_company(self.db, aid)
            msg = u'%s旗下 %s跌出iOS%s前100名' % \
                  (dbutil.get_company_name(self.db, cid),
                   self.__normalize_iOS_name(dbutil.get_artifact_name(self.db, aid)),
                   self.__get_rank_name(item['genre'], item['type']))
            detail = '%s,%s' % (item['genre'], item['type'])
            comments = dbutil.get_artifact_name(self.db, aid)
            yield dbutil.update_daily_company_message(self.db, cid, msg, 3108, 30, aid, day_thirday, detail, comments)
            logger_track.info('3108, %s, %s' % (cid, aid))

    def update_3109(self, today=None):

        global logger_track
        today = today or datetime.today()
        one_week_before, three_month_before = today - timedelta(days=8), today - timedelta(days=90)
        types = ['free', 'charge', 'grossing']
        genres = self.__get_genres()
        for t in types:
            for g in genres:
                outstanding_apps_candidates = [item['_id'] for item in list(self.mongo.trend.appstore_rank.aggregate([
                    {'$match': {'date': {'$gt': one_week_before, '$lte': today}, 'rank': {'$lte': 10}, 'type': t,
                                'genre': g}},
                    {'$group': {'_id': '$trackId', 'times': {'$sum': 1}}},
                    {'$match': {'times': {'$gte': 7}}}]))]
                
                def previous_perform_poorly(track_id):
                    top_rank = list(self.mongo.trend.appstore_rank.find({'trackId': track_id, 'type': t, 'genre': g,
                                                                         'date': {'$gt': three_month_before,
                                                                                  '$lte': one_week_before}}
                                                                        ).sort([('rank', 1)]).limit(10))
                    return top_rank[-1]['rank'] > 30 if top_rank else True

                outstanding_apps = filter(previous_perform_poorly, outstanding_apps_candidates)
                for track_id in outstanding_apps:
                    for aid in dbutil.get_artifacts_from_iOS(self.db, track_id):
                        cid = dbutil.get_artifact_company(self.db, aid)
                        corp_round = dbutil.get_company_round(self.db, cid)
                        if corp_round < 1060:
                            msg = u'%s旗下 %s 近期在AppStore%s排名表现突出' % \
                                  (dbutil.get_company_name(self.db, cid),
                                   self.__normalize_iOS_name(dbutil.get_artifact_name(self.db, aid)),
                                   self.__get_rank_name(g, t))
                            detail = '%s,%s' % (g, t)
                            dbutil.update_continuous_company_message(self.db, cid, msg, 3109, 30, aid, 7, detail)
                            logger_track.info('3109, %s, %s, %s, %s' % (cid, aid, t, g))

    def makeup_msg(self):

        for msg in dbutil.get_all_company_messages(self.db, 3107):
            # genre, catelog = msg.detailId.split(',')
            # replacement = u'跌出iOS%s' % self.__get_rank_name(genre, catelog)
            if msg.message.endswith(u'。'):
                message = msg.message.replace(u'。', u'')
                self.db.execute('update company_message set message=%s where id=%s;', message, msg.id)

    def __normalize_iOS_name(self, aname):

        return aname.replace(u'–', u'-').replace(u'－', u'-').replace(u'——', u'-').split(u'-')[0].strip()

    def __get_rank_name(self, genre, catelog):

        genre = u'总榜' if (genre is None or genre == u'None') else u'%s分类' % self.rank_category.get(int(genre))
        if genre == u'None分类':
            return self.rank_catlog.get(catelog)
        return u'%s%s' % (self.rank_catlog.get(catelog), genre)

    def __get_genres(self):

        genres = [None]
        for line in codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'files/ios_rank')):
            genres.append(json.loads(line.strip()).get('id'))
        return genres

    def __load_rank_names(self):

        rank_category = {}
        for line in codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'files/ios_rank'),
                                encoding='utf-8'):
            line = json.loads(line.strip())
            rank_category[line.get('id')] = line.get('name')
        return rank_category


if __name__ == "__main__":

    print __file__
    asrt = AppStoreRankCompanyTracker()
    asrt.makeup_msg()

