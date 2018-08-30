# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
import config as tsbconfig
from common import dbutil
from common.feed import Feeder
from common.dsutil import FixLenList
from common.zhtools.segment import Segmenter
from common.zhtools import stopword, word_filter
from common.feed import Filter

import datetime
import fcntl
import json
import codecs
import logging
from random import randint, sample
from pymongo import DESCENDING
from kafka import KafkaConsumer, KafkaClient, SimpleProducer
from gensim import corpora, models, similarities


cach_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'cach')
stopwords = stopword.get_standard_stopwords()
simi_threshold = 0.25
complete_threshold = 0.25
description_len_threshold = 20
df_threshold_lower = 100
df_threshold_upper = 4000

# logging
logging.getLogger('comps').handlers = []
logger_nlp = logging.getLogger('comps')
logger_nlp.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_nlp.addHandler(stream_handler)


class Companies(object):

    def __init__(self):

        self.segmenter = Segmenter()
        self.feeder = Feeder()
        self.mapping_id2in = {}
        self.mapping_in2id = {}
        self.max_id = 0
        self.default_filter = word_filter.get_default_filter()

    def __iter__(self):

        global description_len_threshold, complete_threshold
        db = dbcon.connect_torndb()
        index = 0
        for cid in iter(dbutil.get_all_company_id(db)):
            contents = self.feeder.feed_string(cid)
            score = dbutil.get_company_score(db, cid)
            if not (score and score > complete_threshold):
                continue
            if int(cid) > self.max_id:
                self.max_id = int(cid)
            words = list(self.segmenter.cut(contents))
            if not words:
                continue
            words = self.default_filter(words)
            if len(words) < description_len_threshold:
                continue

            self.mapping_id2in[cid] = index
            self.mapping_in2id[index] = cid
            index += 1
            yield [word.lower() for word in words]
        db.close()

    def get_mapping_id2in(self):
        return self.mapping_id2in

    def get_mapping_in2id(self):
        return self.mapping_in2id


class CompaniesVector(Companies):

    def __init__(self, dictionary):

        Companies.__init__(self)
        self.dictionary = dictionary

    def __iter__(self):

        for doc in super(CompaniesVector, self).__iter__():
            yield self.dictionary.doc2bow(doc)


class DocumentsSimilarity(object):

    """
    tfidf model based document similarity
    """

    def __init__(self):

        self.life_period = 1000
        self.num_candidates = 800
        self.min_similarity_threshold = 0.05
        self.establish_discount = 0.75

        self.dictionary = self.get_dict()
        self.id2in, self.in2id, self.corpus, self.max_id = self.get_corpus(self.dictionary)
        self.model, self.simi = self.train_model()

        self.segmenter = Segmenter()
        self.filter = Filter()
        self.feeder = Feeder()
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

    def train_model(self):

        global cach_dir
        if not os.path.exists(cach_dir):
            os.mkdir(cach_dir)
        tfidf = models.TfidfModel(self.corpus)
        index = similarities.MatrixSimilarity(tfidf[self.corpus], num_best=self.num_candidates)
        return tfidf, index

    @classmethod
    def get_corpus(cls, dictionary):

        global logger_nlp, cach_dir
        companies = CompaniesVector(dictionary)
        fname = os.path.join(cach_dir, '%s.%s.corpus' % (datetime.datetime.now().strftime('%Y%m%d'), randint(0, 3600)))
        corpora.MmCorpus.serialize(fname, companies)
        logger_nlp.info('Corpus serialized')
        return companies.get_mapping_id2in(), companies.get_mapping_in2id(), corpora.MmCorpus(fname), companies.max_id

    @classmethod
    def get_dict(cls):

        global stopwords, df_threshold_lower, df_threshold_upper, logger_nlp, cach_dir
        dates = datetime.datetime.now().strftime('%Y%m%d')
        if os.path.exists(os.path.join(cach_dir, '%s.%s.dict' % (dates, randint(0, 3600)))):
            try:
                dictionary = corpora.Dictionary.load(os.path.join(cach_dir, '%s.%s.dict' % (dates, randint(0, 3600))))
                logger_nlp.info('Found dictionary file, loaded')
                return dictionary
            except:
                logger_nlp.error('Found dictionary file, fail to load, try to rebuild')
                pass
        companies = Companies()
        dictionary = corpora.Dictionary(company for company in companies)
        stop_ids = [dictionary.token2id[word] for word in stopwords if word in dictionary.token2id]
        low_df = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq <= df_threshold_lower]
        high_df = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq > df_threshold_upper]
        dictionary.filter_tokens(stop_ids + low_df + high_df)
        dictionary.compactify()
        dictionary.save(os.path.join(cach_dir, '%s.%s.dict' % (dates, randint(0, 3600))))
        logger_nlp.info('Dictionary constructed, size %s' % len(dictionary.token2id))
        return dictionary

    def get_similar(self, cid):

        global simi_threshold, complete_threshold

        # pooling
        if cid in self.id2in:
            vec = self.model[self.corpus[self.id2in[cid]]]
            simis = sorted(self.simi[vec], key=lambda x: -x[1])[1:self.num_candidates]
            simis = map(lambda x: (self.in2id[x[0]], round(x[1], 2)), simis)
        else:
            simis = self.get_similar4new(cid)

        # discount
        establish = dbutil.get_company_establish_date(self.db, cid).year
        simis = [(cid2, weight*self.__discount_year(establish, cid2)) for (cid2, weight) in simis]

        # sort and filter
        simis = sorted(simis, key=lambda x: -x[1])
        simis = filter(lambda x:
                       dbutil.get_company_score(self.db, x[0]) > complete_threshold
                       and x[1] > self.min_similarity_threshold, simis)

        # dump and exit
        self.mongo.comps.candidates.update({'company': cid}, {'$set': {'candidates': simis,
                                                                       'modifyTime': datetime.datetime.now()}}, True)
        return simis

    def get_similar4new(self, cid):

        global logger_nlp
        # reload the model when life period goes down to 0, which means, reload after processing 200 new companies
        if int(cid) > self.max_id:
            self.life_period -= 1
        if self.life_period == 0:
            logger_nlp.info('Reload recommend program')
            self.__init__()

        content = self.feeder.feed_string(cid)
        words = self.filter.filtermany(self.segmenter.cut(content))
        vec = self.model[self.dictionary.doc2bow(words, allow_update=True)]
        simis = sorted(self.simi[vec], key=lambda x: -x[1])[1:self.num_candidates]
        simis = map(lambda x: (self.in2id[x[0]], round(x[1], 2)), simis)
        return simis

    def __discount_year(self, establish, cid2):

        diff = abs(dbutil.get_company_establish_date(self.db, cid2).year - establish)
        return self.establish_discount if diff > 5 else 1

    def dump_full(self):

        global logger_nlp
        db = dbcon.connect_torndb()
        for cid in iter(dbutil.get_all_company_id(db)):
            try:
                self.get_similar(cid)
                logger_nlp.info('%s processed' % cid)
            except Exception, e:
                logger_nlp.exception('%s failed, %s' % (cid, e))
        db.close()


def candidates_full():

    global logger_nlp
    logger_nlp.info('Full Comps Candidates Processing Starts')
    docsim = DocumentsSimilarity()
    logger_nlp.info('Comps Candidates ')
    docsim.dump_full()


def candidates_incremental():

    global logger_nlp
    url = tsbconfig.get_kafka_config()
    consumer_rec = KafkaConsumer("keyword_v2", group_id="company candidates generate", session_timeout_ms=100000,
                                 bootstrap_servers=[url], auto_offset_reset='smallest')
    producer = SimpleProducer(KafkaClient(url))

    logger_nlp.info('Start to process incremental comps candidates')
    docsim = DocumentsSimilarity()
    db = dbcon.connect_torndb()
    cach = FixLenList(50)
    logger_nlp.info('Candidates model inited')
    for message in consumer_rec:
        cid = json.loads(message.value).get('id')
        try:
            if cid in set(cach):
                logger_nlp.info('Company %s in cach' % cid)
                consumer_rec.commit()
                continue
            updates = docsim.get_similar(cid)
            if updates:
                cach.append(cid)
            logger_nlp.info('Candidates for %s processed' % cid)
            if dbutil.get_company_create_date(db, cid) > (datetime.datetime.now() - datetime.timedelta(days=7)):
                producer.send_messages("keyword_v2", json.dumps({{"id": cid, 'action': 'create'}}))
            consumer_rec.commit()
        except Exception, e:
            logger_nlp.exception('Fail to process %s, due to %s' % (cid, e))


def candidate_list():

    global logger_nlp
    docsim = DocumentsSimilarity()
    for cid in open('files/sample'):
        try:
            docsim.get_similar(int(cid.strip()))
            logger_nlp.info('Processed, %s' % cid.strip())
        except Exception, e:
            logger_nlp.exception('Failed, %s, %s' % (cid.strip(), e))


def company_sample():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    cids = mongo.task.company.find({'types': 'visit_local'}).sort('_id', DESCENDING).limit(500)
    cids = sample([r.get('companyId') for r in cids], 100)
    with codecs.open('files/sample', 'w', 'utf-8') as fo:
        fo.write('\n'.join([str(cid) for cid in cids]))
    with codecs.open('files/sample.old', 'w', 'utf-8') as fo:
        for cid in cids:
            fo.write('%s#%s\n' % (cid, ','.join([str(cid2) for cid2 in dbutil.get_company_comps(db, cid)])))


if __name__ == '__main__':

    print __file__

    if sys.argv[1] == 'full' or sys.argv[1] == 'all':
        candidates_full()
    elif sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        candidates_incremental()
    elif sys.argv[1] == 'list':
        company_sample()
        candidate_list()
