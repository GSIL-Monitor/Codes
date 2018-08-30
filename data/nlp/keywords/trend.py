import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../search'))

import db as dbcon
import config as tsbconfig
import loghelper
from common import dbutil
from news_search.news_client import NewsSearchClient

import pandas as pd
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch


loghelper.init_logger("tt", stream=True)
logger_tt = loghelper.get_logger('tt')


class TagTrend(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        host, port = tsbconfig.get_es_config_2()
        es = Elasticsearch([{'host': host, 'port': port}])
        self.search_client = NewsSearchClient(es)

        self.news_read_url = '/api-gen-service/api2/service/x_service/system_news/get_news_details_by_id'

    def memorize(self, tid, today=None):

        global logger_tt
        if not today:
            today = datetime.today()
        yesterday = today - timedelta(days=1)
        today_int = int(today.strftime('%Y%m%d'))
        tag = dbutil.get_tag_info(self.db, tid, 'name')

        logger_tt.info('Start to process %s' % tid)
        # relevant companies
        cids = dbutil.get_company_from_tags(self.db, [tid])
        codes = [dbutil.get_company_code(self.db, cid) for cid in cids]
        visits = self.mongo.log.user_log.find({'time': {'$gt': today - timedelta(hours=32),
                                                        '$lte': today - timedelta(hours=8)},
                                               'requestURL': "/xiniudata-api/api2/service/company/basic",
                                               'jsonRequest.payload.code': {'$in': codes}})
        # visits = list(visits)
        # visits = [visit['jsonRequest']['payload']['code'] in codes for visit in visits]
        self.mongo.keywords.trend_statistc.update({'tag': tid, 'date': datetime.fromordinal(today.date().toordinal()),
                                                   'subtype': 'company_visit'},
                                                  {'$set': {'type': 'company', 'weight': len(list(visits))}}, True)
        subscriptions = dbutil.get_company_subscription_details(self.db, yesterday.strftime('%Y-%m-%d'),
                                                                today.strftime('%Y-%m-%d'), *cids)
        self.mongo.keywords.trend_statistc.update({'tag': tid, 'date': datetime.fromordinal(today.date().toordinal()),
                                                   'subtype': 'company_subscribe'},
                                                  {'$set': {'type': 'company', 'weight': len(subscriptions)}}, True)
        # logger_tt.info('Company done')

        # relevant news
        news = self.search_client.search('general', input=tag, filters={'date': today_int}, size=500).get('news', {})
        news = list(news.get('data', []))
        self.mongo.keywords.trend_statistc.update({'tag': tid, 'date': datetime.fromordinal(today.date().toordinal()),
                                                   'subtype': 'news_relevant'},
                                                  {'$set': {'type': 'news', 'weight': len(news)}}, True)
        # logger_tt.info('News searched')
        news_read = self.mongo.log.user_log.find({'time': {'$gt': today - timedelta(hours=32),
                                                           '$lte': today - timedelta(hours=8)},
                                                  'requestURL': self.news_read_url,
                                                  'jsonRequest.payload.newsId': {'$in': news}})
        self.mongo.keywords.trend_statistc.update({'tag': tid, 'date': datetime.fromordinal(today.date().toordinal()),
                                                   'subtype': 'news_read'},
                                                  {'$set': {'type': 'news', 'weight': len(list(news_read))}}, True)
        # logger_tt.info('News done')

        # search
        search = self.mongo.log.search.find({'time': {'$gt': today - timedelta(hours=32),
                                                      '$lte': today - timedelta(hours=8)},
                                             'query.input': tag, 'userId': {'$ne': None}})
        self.mongo.keywords.trend_statistc.update({'tag': tid, 'date': datetime.fromordinal(today.date().toordinal()),
                                                   'subtype': 'search_precise'},
                                                  {'$set': {'type': 'search', 'weight': len(list(search))}}, True)
        # logger_tt.info('Search done')

    def identify(self, today=None):

        if not today:
            today = datetime.today()
        # growth yesterday
        start = datetime.fromordinal((today - timedelta(days=2)).date().toordinal())
        df = pd.DataFrame(list(self.mongo.keywords.trend_statistc.find({'date': {'$gte': start}})))
        df = df.groupby(['tag', 'subtype'])['weight'].\
            agg({'growth': lambda weight: (max(weight)-min(weight)+1)/(min(weight)+1)})
        df.reset_index(inplace=True)
        df['rank'] = df.groupby('subtype')['growth'].rank(ascending=0, method='first')
        df['name'] = df.apply(lambda x: dbutil.get_tag_info(self.db, x[0], 'name'), 1)
        df = df.loc[(df['rank'] < 5) & (df['growth'] > 1)]
        for _, row in df.iterrows():
            row = dict(row)
            if len(list(self.mongo.task.tag.find({'type': 'trend', 'id': row.get('tag'), 'processStatus': 0}))) > 0:
                self.mongo.task.tag.update({'type': 'trend', 'id': row.get('tag'), 'processStatus': 0},
                                           {'$set': {'modifyTime': datetime.utcnow()}})
            else:
                self.mongo.task.tag.insert({'type': 'trend', 'id': row.get('tag'), 'processStatus': 0,
                                            'name': row.get('name'), 'createTime': datetime.utcnow(),
                                            'modifyTime': datetime.utcnow(), 'reason': row.get('subtype')})


def memorize_important():

    tt = TagTrend()
    t = datetime.today()
    # tt.memorize(426)
    db = dbcon.connect_torndb()
    for tag in dbutil.get_tags_by_type(db, (11000, 11010, 11011, 11012, 11013, 11050, 11051, 11052, 11053)):
        try:
            tt.memorize(int(tag.id), t)
        except Exception, e:
            logger_tt.exception('Fail to process tag %s, %s' % (tag.id, e))
    tt.identify()


if __name__ == '__main__':

    print __file__
    if sys.argv[1] == 'identify':
        tt = TagTrend()
        tt.identify()
    elif sys.argv[1] == 'memorize':
        memorize_important()
