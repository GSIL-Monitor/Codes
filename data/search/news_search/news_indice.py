# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import logging

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from bson.objectid import ObjectId
from itertools import chain
from datetime import datetime, timedelta

import config as tsbconfig
import db as dbcon
import mappings
from nlp.common import dbutil
from nlp.common.zhtools.segment import Segmenter
from nlp.common.zhtools import stopword

logging.basicConfig(level=logging.INFO, format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
logger_index = logging.getLogger('index')


class NewsIndexCreator(object):

    def __init__(self, es=None):

        global logging_index
        self.logger = logger_index

        if es:
            self.es = es
        else:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])

        self.logger.info('Search client initiated')

        self.stopwords = stopword.get_standard_stopwords()
        self.seg = Segmenter()
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

    def __check(self):

        if not self.es.indices.exists(["xiniudata2"]):
            self.logger.info('Creating index xiniudata2')
            self.es.indices.create("xiniudata2")
            self.logger.info('Created')
        self.es.indices.put_mapping('news', mappings.get_news_mapping(), 'xiniudata2')
        self.logger.info('News mapping created')

    def create_single_record(self, record):

        if not record:
            self.logger.exception('News id not found')
            return
        news = {}

        title = filter(lambda x: x not in self.stopwords and len(x) > 1, self.seg.cut4search(record.get('title', '')))
        news['title'] = ' '.join(title).lower().decode('utf-8').encode('utf-8')
        content = [filter(lambda x: x not in self.stopwords and len(x) > 1,
                          self.seg.cut4search(content.get('content', ''))) for content in record.get('contents', [])]
        content.extend(title)
        news['content'] = ' '.join(chain(*content)).lower().decode('utf-8').encode('utf-8')
        news['domain'] = record.get('domain')
        news['link'] = record.get('link')
        news['type'] = record.get('type', 0)
        news['status'] = record.get('processStatus', 0)
        # tag id integer
        news['features'] = list(set(record.get('sectors', [])) | set(record.get('features', [])))
        # tag name string
        news['tags'] = [dbutil.get_tag_name(self.db, tid) for tid in news['features']
                        if dbutil.get_tag_name(self.db, tid)]
        news['date'] = int(record.get('createTime', datetime(1993, 4, 30)).strftime('%y%m%d%H%M')) if news['type'] == 60002\
            else int(record.get('date', datetime(1993, 4, 30)).strftime('%y%m%d%H%M'))

        self.es.index(index='xiniudata2', doc_type='news', id=str(record['_id']), body=news)

    def create_index(self, period=3):

        self.__check()
        for record in self.mongo.article.news.find({'createTime': {'$gt': datetime.now() - timedelta(days=period)}}):
            try:
                self.create_single_record(record)
                logger_index.info('Process %s' % record['_id'])
            except Exception, e:
                logger_index.exception('Fail to process %s, due to %s' % (record['_id'], e))


if __name__ == '__main__':

    print __file__
    if len(sys.argv) > 1:
        if not sys.argv[1]:
            nic = NewsIndexCreator()
        elif int(sys.argv[1]) == 1:
            host, port = tsbconfig.get_es_config_1()
            nic = NewsIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        elif int(sys.argv[1]) == 2:
            host, port = tsbconfig.get_es_config_2()
            nic = NewsIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        else:
            nic = NewsIndexCreator()
    else:
        nic = NewsIndexCreator()
    nic.create_index(2)
