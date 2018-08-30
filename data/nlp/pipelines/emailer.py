# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
import config as tsbconfig
from common import dbutil
from common.zhtools.ner import SimpleNER
from common.zhtools import hants
from recommend.assign import ColdcallAssigner
from search.client import SearchClient

import re
import json
import logging
from kafka import KafkaClient, SimpleProducer, KafkaConsumer

false_nl = re.compile(r'(>[^\n]+?)\n([^>])')
dup_space = re.compile(r'>\s+([^\s])')

title_split = re.compile(u'[：|【】！!，。,\.（）\s\(\)·—"“”『』_-—]')

consumer_coldcall = None
producer_coldcall = None

# logging
logging.getLogger('coldcall').handlers = []
logger_coldcall = logging.getLogger('coldcall')
logger_coldcall.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_coldcall.addHandler(stream_handler)


class EmailLinker(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.ner = SimpleNER()
        # self.ner.train()
        self.sc = SearchClient()
        self.assigner = ColdcallAssigner()

    def link(self, ccid):

        """
        given a coldcall id, return possible company ids
        """
        infos = dbutil.get_coldcall_infos(self.db, ccid)
        if not infos:
            return

        oid, name, content = infos.organizationId, infos.name, infos.content
        email = Email(name, content)
        # return email.link2company(self.db, self.ner, self.sc)
        self.__record2db(ccid, email)

    def __record2db(self, ccid, email):

        """
        record extracted email into database
        """

        candidates = email.link2company(self.db, self.ner, self.sc)
        if not candidates:
            self.assigner.assign(ccid)
            dbutil.mark_coldcall_processed(self.db, ccid)
            return

        # update = dbutil.exist_coldcall_link(self.db, cid)  # true for update, false for insert
        for candidate in candidates:
            cid, confidence = candidate.get('cid'), candidate.get('confidence', 0.5)
            scid = dbutil.insert_source_company(self.db, email.title, email.extract().get('description', ''))
            dbutil.insert_coldcall_sc_link(self.db, ccid, scid)
            dbutil.insert_company_candidate(self.db, scid, cid, confidence)

        # assign cold call to person
        self.assigner.assign(ccid)
        dbutil.mark_coldcall_processed(self.db, ccid)


class Email(object):

    def __init__(self, title, original):

        self.title = title
        self.original = original
        self.lines = []
        # self.preprocess()

    def preprocess(self):

        self.__pipeline_linesplit()

    def link2company(self, db, ner, sc):

        results = {}
        candidates = self.__resolve_title(ner, sc)
        candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        z = sum(map(lambda x: x[1], candidates))
        for candidate in candidates:
            cids = dbutil.get_company_id(db, candidate[0])
            for cid in cids:
                results[cid] = results.get(cid, 0) + round(candidate[1]/z, 3)
        return sorted([{'cid': k, 'confidence': v} for k, v in results.items()],
                      key=lambda x: x.get('confidence', 0), reverse=True)[:5]

    def __resolve_title(self, ner, sc):

        global title_split
        title = ner.chunk(self.title)
        weight = lambda x: 2**len(x)-len(x)*(len(x)-1)/2
        candidates = {x.word.strip(): weight(x) for x in title if x.flag == 'cn'}
        titles = filter(lambda x: x.strip(), title_split.sub('-', self.title).split('-'))
        for title in titles:
            if (hants.all_eng(title) or title.isdigit()) and len(title) > 1:
                candidates = self.__extend_candidates_search(candidates, title, sc)
            else:
                for pace in xrange(2, min(5, len(title)+1)):
                    for i in xrange(len(title)-pace+1):
                        name = title[i: i+pace]
                        candidates = self.__extend_candidates_search(candidates, name, sc)
        return candidates

    def __extend_candidates_search(self, candidates, title, sc):

        results = sc.search('completion', **{'key': title.strip(), 'field': 'name'}).get('name', [])
        if 0 < len(set([result.get('_code') for result in results])) < 3:
            # print title, len(results), results
            for index, result in enumerate(results):
                candidates[result.get('_name')] = candidates.get(result.get('_name'), 0) + 1.0/(index+1)
        return candidates

    def __pipeline_linesplit(self):

        """
        split whole content into lines
        """
        global false_nl, dup_space
        content = false_nl.sub(r'\1\2', self.original)
        content = dup_space.sub(r'>\1', content)
        for line in content.split('\n'):
            if not line.replace('>', '').strip():
                continue
            self.lines.append(line)

    def record(self, fo):

        fo.write('\n'.join(self.lines))

    def extract(self):

        return {
            'description': '\n'.join(self.lines)
        }


def init_kafka():

    global producer_coldcall
    global consumer_coldcall

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_coldcall = SimpleProducer(kafka)
    consumer_coldcall = KafkaConsumer("coldcall", group_id="coldcall incremental",
                                      metadata_broker_list=[url], auto_offset_reset='smallest')


def link_all():

    el = EmailLinker()
    for ccid in dbutil.get_all_coldcall(el.db):
        el.link(ccid)


def link_incremental():

    global consumer_coldcall, producer_coldcall, logger_coldcall
    el = EmailLinker()
    init_kafka()
    while True:
        logger_coldcall.info('Start to incrementally process coldcall')
        try:
            for message in consumer_coldcall:
                try:
                    logger_coldcall.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                        message.offset, message.key,
                                                                        message.value))
                    ccid = json.loads(message.value).get('id') or json.loads(message.value).get('_id')
                    el.link(ccid)
                    logger_coldcall.info('Cold call %s processed' % ccid)
                    consumer_coldcall.task_done(message)
                    consumer_coldcall.commit()
                except Exception, e:
                    logger_coldcall.exception('Failed cold call %s # %s' % (ccid, e))
        except Exception, e:
            logger_coldcall.exception('Outside error')


if __name__ == '__main__':

    print __file__

    if sys.argv[1] == 'full':
        link_all()
    elif sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        link_incremental()
    elif sys.argv[1] == 'test':
        el = EmailLinker()
        el.link(sys.argv[2])