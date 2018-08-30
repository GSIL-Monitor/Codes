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
from common.zhtools.segment import Segmenter
from common.zhtools import word_filter
from common.feed import NewsFeeder
from mentioned import CompanyLinker

import time
import logging
import pymongo
import fasttext
from datetime import datetime, timedelta

viptag_model = os.path.join(os.path.split(os.path.realpath(__file__))[0], '../keywords/models/20180319.bin')

# logging
logging.getLogger('news_pip').handlers = []
logger_news_pip = logging.getLogger('news_pip')
logger_news_pip.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_news_pip.addHandler(stream_handler)


class NewsPipeline(object):

    def __init__(self):

        global viptag_model, logger_news_pip
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.seg = Segmenter(tag=True)
        self.wfilter = word_filter.get_default_filter()
        self.feeder = NewsFeeder()

        self.viptag_clf = fasttext.load_model(viptag_model)

        self.life_circle_linker = 100
        self.life_circle_linker_max = 100
        self.linker = CompanyLinker()

        logger_news_pip.info('Model inited')

    def process_piece_news(self, record):

        # dump news from 36kr old source
        if record.get('source', 0) == 13022:
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': -4}})
            return

        # process sector
        try:
            if record.get('sectors', False):
                pass
            else:
                desc = ' '.join(self.feeder.feed(record))
                if desc and len(desc) > 20:
                    classifier_vips = {int(tag.replace(u'__label__', '')): weight for (tag, weight) in
                                       self.viptag_clf.predict_proba([desc], 2)[0]}
                    if max(classifier_vips.values()) < 0.25:
                        sectors = [(999, 0)]
                    elif max(classifier_vips.values()) - min(classifier_vips.values()) < 0.15:
                        sectors = [(dbutil.get_sector_from_tag(self.db, tid), confidence)
                                   for (tid, confidence) in sorted(classifier_vips.iteritems(), key=lambda x: -x[1])]
                    else:
                        sectors = [(dbutil.get_sector_from_tag(self.db, tid), confidence)
                                   for (tid, confidence) in sorted(classifier_vips.iteritems(), key=lambda x: -x[1])]
                        sectors = [sectors[0]]
                else:
                    sectors = [(999, 0)]
                sids = [sid for (sid, _) in sectors]
                if 7 in sids and u'区块链' in desc and 20006 not in sids:
                    sids.remove(7)
                    sids.append(20006)
                    confidences = []
                else:
                    confidences = [confidence for (_, confidence) in sectors]
                if False in sids:
                    logger_news_pip.exception('Sector mappping failed, %s, %s' % (record['_id'], classifier_vips))
                else:
                    tags = [dbutil.get_tag_from_sector(self.db, sid) for sid in sids]
                    self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'sectors': sids,
                                                                                     'sector_confidence': confidences}})
        except Exception, e:
            logger_news_pip.exception('sector failed, %s, %s' % (record['_id'], e))
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': -1}})
            return

        # process mentioned company
        # if record.get('date', False) and (record.get('date') < datetime.now() - timedelta(days=30)) \
        #         and not record.get('companyIds'):
        #     try:
        #         if self.life_circle_linker <= 0:
        #             self.linker = CompanyLinker()
        #             self.life_circle_linker = self.life_circle_linker_max
        #         mentioned = list(self.linker.find(record['_id']))
        #         if record.get('companyId', False) and record.get('companyId') not in [x[0] for x in mentioned]:
        #             mentioned.append((record['companyId'], 1))
        #         if mentioned:
        #             cids, confs = [x[0] for x in mentioned], [x[1] for x in mentioned]
        #             self.mongo.article.news.update({'_id': record['_id']},
        #                                       {'$set': {'companyIds': cids, 'mention_confidence': confs}})
        #         else:
        #             cids = [0]
        #         logger_news_pip.info('mentioned processed %s, found %s' % (record['_id'], str(cids)))
        #         self.life_circle_linker -= 1
        #     except Exception, e:
        #         logger_news_pip.exception('mentioned failed, %s, %s' % (record['_id'], e))
        #         self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': -2}})
        #         return

        # load categories from task news
        # try:
        #     if (record.get('categories', None) is None) and (record.get('type', 0) == 60001):
        #         tn = self.mongo.task.news.find_one({'news_id': str(record['_id']), 'section': 'step1'})
        #         if not tn:
        #             time.sleep(0.5)
        #             tn = self.mongo.task.news.find_one({'news_id': str(record['_id']), 'section': 'step1'})
        #         if tn:
        #             categories = tn.get('categories', [])
        #             category = self.__map_category(categories)
        #         else:
        #             categories = [578359]
        #             category = None
        #         self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'categories': categories,
        #                                                                          'category': category}})
        # except Exception, e:
        #     logger_news_pip.exception('category failed, %s, %s' % (record['_id'], e))
        #     self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': -3}})

        # mark done
        try:
            self.mongo.article.news.update({'_id': record['_id']}, {'$set': {'processStatus': 1, 'modifyUser': 139}})
            logger_news_pip.info('All Done, %s' % record['_id'])
        except Exception, e:
            logger_news_pip.exception('Fail to insert, %s, %s' % (record['_id'], e))

    def __map_category(self, categories):

        if 578349 in categories:
            return 60101
        elif 578351 in categories or 578350 in categories or 605265 in categories:
            return 60104
        elif 578354 in categories:
            return 60105
        elif 578352 in categories or 578356 in categories or 578357 in categories:
            return 60107
        elif 128 in categories or 578353 in categories:
            return 60102
        elif 605264 in categories:
            return 60103
        return None

    def process_news(self):

        global logger_news_pip

        logger_news_pip.info('start to process pending news')
        while True:
            for record in list(self.mongo.article.news.find({'type': {'$in': [60001, 60002, 60003]},
                                                             'processStatus': 0}).sort('date', pymongo.DESCENDING)):
                try:
                    self.process_piece_news(record)
                except Exception, e:
                    logger_news_pip.exception('Fail to process %s, due to %s' % (record['_id'], e))
            time.sleep(600)


if __name__ == '__main__':

    np = NewsPipeline()
    np.process_news()
