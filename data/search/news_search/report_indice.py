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
from datetime import datetime, timedelta

import config as tsbconfig
import db as dbcon
import mappings
from nlp.common import dbutil
from nlp.common.zhtools.segment import Segmenter
from nlp.common.zhtools import stopword

logging.basicConfig(level=logging.INFO, format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
logger_index = logging.getLogger('index')


class ReportIndexCreator(object):

    def __init__(self, es=None):

        global logging_index
        self.logger = logger_index

        if es:
            self.es = es
        else:
            host, port = tsbconfig.get_es_config()
            self.es = Elasticsearch([{'host': host, 'port': port}])

        self.logger.info('Search client initiated')

        self.stopwords = stopword.get_stopwords('chinese', 'english')
        self.seg = Segmenter()
        self.mongo = dbcon.connect_mongo()

    def __check(self):

        if not self.es.indices.exists(["xiniudata2"]):
            self.logger.info('Creating index xiniudata2')
            self.es.indices.create("xiniudata2")
            self.logger.info('Created')
        self.es.indices.put_mapping('report', mappings.get_report_mapping(), 'xiniudata2')
        self.logger.info('Report mapping created')

    def create_single_record(self, record):

        report = {}
        if not record.get('title'):
            self.logger.exception('Report %s has no title' % record['_id'])
            return
        title = filter(lambda x: x not in self.stopwords and len(x) > 1, self.seg.cut4search(record.get('title', '')))
        report['title'] = ' '.join(title).lower().decode('utf-8').encode('utf-8')
        filename = filter(lambda x: x not in self.stopwords and len(x) > 1, self.seg.cut4search(record.get('filename')))
        report['filename'] = ' '.join(filename).lower().decode('utf-8').encode('utf-8')
        if not record.get('description'):
            report['description'] = ''
        else:
            desc = filter(lambda x: x not in self.stopwords and len(x) > 1,
                          self.seg.cut4search(record.get('description')))
            report['description'] = ' '.join(desc).lower().decode('utf-8').encode('utf-8')
        # report['description'] = '%s %s' % (report.get('description', ''), record.get('source', ''))
        report['domain'] = record.get('source')
        report['fileId'] = record.get('fieldId')
        report['md5'] = record.get('md5')
        report['filesize'] = record.get('size', 0)
        report['pages'] = record.get('pages', 0)
        report['status'] = record.get('processStatus', 0)
        report['createTime'] = int(record.get('createTime', datetime(1993, 4, 30)).strftime('%y%m%d%H%M'))
        report['modifyTime'] = int(record.get('modifyTime', datetime(1993, 4, 30)).strftime('%y%m%d%H%M'))
        date = record.get('pdfCreationDate')
        report['date'] = int(date.strftime('%y%m%d%H%M')) if date else report['createTime']
        report['reportType'] = record.get('type', 0)
        report['marketSource'] = record.get('marketSource')
        report['marketSymbol'] = record.get('marketSymbol')

        self.es.index(index='xiniudata2', doc_type='report', id=str(record['_id']), body=report)

    def create_index(self, limit=100):

        self.__check()
        for record in self.mongo.article.report.find().sort([('_id', -1)]).limit(limit):
            try:
                logger_index.info('Processing %s' % record['_id'])
                self.create_single_record(record)
            except Exception, e:
                self.logger.exception('Fail to process %s, due to %s' % (record['_id'], e))


def test():

    ric = ReportIndexCreator()
    mongo = dbcon.connect_mongo()
    record = mongo.article.report.find_one({'title': u'2018年Q1中国水饮B2C电商市场分析报告'})
    ric.create_single_record(record)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        if not sys.argv[1]:
            ric = ReportIndexCreator()
        elif int(sys.argv[1]) == 1:
            host, port = tsbconfig.get_es_config_1()
            ric = ReportIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        elif int(sys.argv[1]) == 2:
            host, port = tsbconfig.get_es_config_2()
            ric = ReportIndexCreator(Elasticsearch([{'host': host, 'port': port}]))
        else:
            ric = ReportIndexCreator()
    else:
        ric = ReportIndexCreator()
    ric.create_index(10000)
