# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../search'))

import db as dbcon
import config as tsbconfig
from common import dicts, dbutil
from common.zhtools import word_filter, hants
from common.zhtools.postagger import Tagger
from common.zhtools.segment import Segmenter
from common.feed import Feeder
from common.dsutil import UndirectWeightedGraph, FixLenList
from general import GeneralTagger
from gangtag import GangTag
from client import SearchClient
from templates import generate_rule_based_query

import socket
import fcntl
import json
import random
import logging
import collections
import fasttext
import numpy as np
import pandas as pd
from math import ceil, floor
from datetime import datetime, timedelta
from itertools import chain
from gensim.models import Word2Vec
from sklearn.externals import joblib
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from kafka.errors import FailedPayloadsError


# logging
logging.getLogger('tag').handlers = []
logger_tag = logging.getLogger('tag')
logger_tag.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_tag.addHandler(stream_handler)


# word2vec_model = os.path.join(os.path.split(os.path.realpath(__file__))[0],
#                               '../embedding/models/s400w4min20.binary.w2vmodel')
word2vec_model = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                              '../embedding/models/s400w3min20_yitai.binary.w2vmodel')
viptag_setting = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'thesaurus/11012')
# viptag_model = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models/viptag.bin')
viptag_model_20171221 = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models/20171221.bin')
viptag_model_traditional = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models/traditional.model')
textrank_window_size = 2
textrank_threshold = 0.4

# kafka
producer_tag = None
consumer_tag = None


class Extractor(object):

    def __init__(self):

        global word2vec_model, viptag_model_20171221, viptag_model_traditional, logger_tag
        logger_tag.info('Extractor model initing')

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.feeder = Feeder()
        self.tagger = Tagger(itags=True)
        self.seg = Segmenter(itags=True)
        self.wfilter = word_filter.get_default_filter()

        self.gang = GangTag()

        self.w2v = Word2Vec.load(word2vec_model)
        self.similarity_threshold = 0.4
        self.chain_simi_threshold = 0.25

        self.vip_tags = {t.name: t.id for t in dbutil.get_sectored_tags(self.db, 1)}
        self.vip_classifier = fasttext.load_model(viptag_model_20171221)
        self.traditional_classifier = fasttext.load_model(viptag_model_traditional)
        self.trained_tag_clfs = self.__load_trained_clfs()

        self.important_lower = 0.1
        self.important_threshold = 0.2
        self.relevant_threshold = 0.4
        self.vip_lower = 0.3
        self.vip_threshold = 0.25
        self.important_max_num = 5
        self.max_contents_length = 20

        self.yellows = dbutil.get_yellow_tags(self.db)
        self.importants = set(t.name.lower() for t in dbutil.get_tags_by_type(self.db, [11011, 11013]))
        self.thesaurus = self.__load_weighted_tags()
        self.thesaurus_ids = self.__load_weighted_tags(tid=True)
        self.junk_terms = self.__load_junk_tags()
        self.replacements = {r['source']: r['replacement'] for r in self.mongo.keywords.replacement.find()}

        self.trusted_sources = dicts.get_known_company_source()

        self.general_tagger = GeneralTagger()

        logger_tag.info('Extractor model inited')

    def __load_trained_clfs(self):

        model_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models')
        return {175747: joblib.load(os.path.join(model_dir, '175747.20180311.model'))}

    def __extract_source_tag(self, cid):

        tags = dbutil.get_source_company_tags(self.db, cid, self.trusted_sources)
        if tags:
            return set(chain(*[dbutil.analyze_source_tag(self.db, tname, self.replacements)
                               for tname in tags if tname and tname.strip()]))
        return set([])

    def __extract_important(self, contents, source_tags=None):

        # candidates generation
        candidates = {} if not source_tags else {}.fromkeys(source_tags, 1)
        for content, weight in contents:
            for tag in [x[0] for x in self.tagger.tag(content) if x[1] == 'itag' or x[0] in self.importants]:
                candidates[tag] = candidates.get(tag, 0) + weight
        if len(candidates) < 1:
            return {}

        # support assignment
        content_length = 0
        supports = {}
        for index, (content, dweight) in enumerate(contents):
            for word in self.wfilter([x[0] for x in self.tagger.tag(content)]):
                if word not in self.w2v:
                    continue
                content_length += 1
                for candidate in candidates.keys():
                    if candidate not in self.w2v:
                        continue
                    similarity = self.w2v.similarity(candidate, word)
                    if similarity > self.similarity_threshold:
                        supports.setdefault(candidate, []).append((index, dweight, similarity))
        # for k, v in supports.iteritems():
        #     print k, v

        # support selection
        results = {}
        csize = len(candidates)
        for candidate, v in supports.iteritems():
            # if (csize >= 2) and \
            #         (sum([y[1] for y in set([(x[0], x[1]) for x in v])]) < min(6, ceil(float(len(contents))/3))):
            #     continue
            support = sum([round(item[1]*item[2], 2) for item in v])
            if csize >= 2 and sum([round(item[2], 2) for item in v]) < content_length / 20:
                continue
            results[candidate] = support * self.thesaurus.get(candidate, 1)
        if len(results) == 0:
            return results

        # normalization
        normalizer = max(results.values())
        for k, v in results.items():
            # if round(v/normalizer, 2) < self.important_lower:
            #     continue
            results[k] = round(v/normalizer, 2)

        # narrow down results size
        if len(results) < 4:
            pass
        else:
            results = dict(filter(lambda x: x[1] > self.important_threshold, results.iteritems()))
            if len(results) > self.important_max_num:
                size = min(10, max(int(ceil(len(results)/2.0)), self.important_max_num))
                results = dict(sorted(results.iteritems(), key=lambda x: -x[1])[:size])

        return results

    def __extract_vectorrank(self, contents):

        pass

    def __extract_textrank(self, contents, topn=15):

        """
        weighted textrank, weights use tags' novelties
        """

        global textrank_window_size, textrank_threshold

        candidates = []
        for content, _ in contents:
            candidates.extend([x[0] for x in self.tagger.tag(content)])
        # filter
        candidates = self.wfilter(candidates)
        # print ' '.join(candidates)
        if len(candidates) < 5:
            return

        graph = UndirectWeightedGraph()
        weights = collections.defaultdict(int)

        for i in xrange(len(candidates)):
            for j in xrange(i+1, i+textrank_window_size):
                if j >= len(candidates):
                    break
                weights[(candidates[i], candidates[j])] += 1
        for terms, weight in weights.iteritems():
            graph.add_edge(terms[0], terms[1], weight)
        nodes_rank = graph.rank(self.thesaurus)
        index = min(topn, len(candidates))
        start = 0
        for tag, weight in sorted(nodes_rank.items(), key=lambda x: -x[1])[:index]:
            if tag in self.junk_terms:
                continue
            if start < 2:
                yield tag, round(weight, 2)
            elif weight >= textrank_threshold:
                yield tag, round(weight, 2)
            start += 1

    def extract(self, cid, topn=15, fast=False, update_only=False):

        # general tag
        new_general = self.general_tagger.label(cid)
        if new_general:
            logger_tag.info('General Tag of %s, %s' % (cid, ','.join([str(tid) for tid in new_general])))

        contents = list(self.feeder.feed(cid, quanlity='medium'))
        results = {}
        if len(contents) > self.max_contents_length:
            contents = sorted(contents, key=lambda x: -x[1])[:self.max_contents_length]
        # source tags
        source_tags = self.__extract_source_tag(cid)
        # print ','.join(source_tags)
        # results = self.merge(results, {}.fromkeys(source_tags, 0.5))
        # important tag
        results = self.merge(results, self.__extract_important(contents, source_tags), 1)
        # regular tag
        results = self.merge(results, dict(self.__extract_textrank(contents, topn)))
        # verified tag
        results = self.merge(results, dict.fromkeys(dbutil.get_company_tags_verified(self.db, cid), 1))
        # topic tag
        results = self.merge(results, dict.fromkeys(dbutil.get_company_topics_tags(self.db, cid), 1.5))
        # normalize
        results = self.__normalize(results)
        # vip tags
        vips = self.update_vip_tags(cid, results, source_tags)
        # update contents based tags
        results = self.__normalize_replacement(results)
        try:
            new_tags, remove_tags = self.update_contents_tags(cid, results, source_tags, vips, topn)
        except Exception, e:
            new_tags, remove_tags = [], []
            logger_tag.info('Fail to update contents tags, %s, %s' % (cid, e))
        if not update_only:
            for remove_tag in remove_tags:
                dbutil.update_company_tag(self.db, cid, remove_tag, 0, active="N")
        logger_tag.info('Processed %s, new tags %s, removed %s' % (cid, ','.join([str(tid) for tid in new_tags]),
                                                                   ','.join([str(tid) for tid in remove_tags])))

        # process gang tag 派系标签
        gangtag_ids = self.gang.predict(cid)
        for gangtagid in gangtag_ids:
            dbutil.update_company_tag(self.db, cid, gangtagid, 1.001)

        try:
            self.review(cid, contents)
        except Exception, e:
            logger_tag.exception('Review failed, %s, due to %s' % (cid, e))

    def __normalize_replacement(self, tags):

        if type(tags) is dict:
            normalized_tags = {}
            for tag, weight in tags.items():
                if tag in self.replacements:
                    for replacement in self.replacements.get(tag):
                        normalized_tags[replacement] = weight
                else:
                    normalized_tags[tag] = weight
        else:
            normalized_tags = []
            for tag in tags:
                if tag in self.replacements:
                    for replacement in self.replacements.get(tag):
                        normalized_tags.append(replacement)
                else:
                    normalized_tags.append(tag)
        return normalized_tags

    def update_vip_tags(self, cid, support_tags, source_tags):

        vips = {}
        support_tag_ids = set(dbutil.get_tag_id(self.db, tag)[0] for tag in support_tags)
        support_vips = {self.vip_tags.get(tag): weight
                        for tag, weight in support_tags.items() if tag in self.vip_tags.keys()}
        for support_vip, support_weight in support_vips.iteritems():
            hyponyms = dbutil.get_hyponym_tags(self.db, support_vip)
            support_vips[support_vip] = support_weight + len(set(hyponyms) & support_tag_ids)
        source_vips = [self.vip_tags.get(tag) for tag in source_tags if tag in self.vip_tags.keys()]
        # desc = ' '.join(self.wfilter([x[0] for x in self.tagger.tag(self.feeder.feed_string(cid, 'with_tag'))]))
        desc = ' '.join(self.wfilter(self.seg.cut4search(self.feeder.feed_string(cid, 'with_tag'))))
        if not desc:
            desc = u'其他'
        # print desc
        classifier_vips = {int(tag.replace(u'__label__', '')): weight for (tag, weight) in
                           self.vip_classifier.predict_proba([desc], 3)[0] if weight > self.vip_lower}
        traditional = self.traditional_classifier.predict_proba([desc], 1)[0][0]
        if source_vips:
            for rank, vip in enumerate(sorted([t for t in source_vips if t in classifier_vips],
                                              key=lambda x: support_vips.get(x, 0)+classifier_vips.get(x, 0),
                                              reverse=True)):
                vips[vip] = 2.999 - round(rank/10.0, 1)
        if traditional[0].replace('__label__', '') == '1' and traditional[1] > 0.6:
            vips[604330] = round(2 + traditional[1], 2)
        elif len(vips) > 1:
            pass
        else:
            vip_candidates = sorted((set(support_vips.keys()) | set(classifier_vips.keys())),
                                    key=lambda x: -support_vips.get(x, 0.1)*0.1*classifier_vips.get(x, 0.01))
            if len(vip_candidates) == 0:
                pass
            elif len(vip_candidates) == 1:
                vip = vip_candidates[0]
                vips[vip] = max(2.9, round(2 + support_vips.get(vip, 0.01) * classifier_vips.get(vip, 0.01), 2))
            else:
                for rank, vip in enumerate(vip_candidates):
                    # print rank, vip, support_vips.get(vip, 0.01), classifier_vips.get(vip, 0.01)
                    rank_discount = {0: 1,
                                     1: 0.3}.get(rank, 0.2)
                    if support_vips.get(vip, 0.01)*rank_discount + classifier_vips.get(vip, 0.01) > self.vip_threshold:
                        vips[vip] = round(max(2.9-rank*0.01,
                                              2+support_vips.get(vip, 0.01)*classifier_vips.get(vip, 0.01)), 2)
        for tid, weight in vips.items():
            if self.replacements.get(tid):
                for rtid in self.replacements.get(tid, []):
                    dbutil.update_company_tag(self.db, cid, rtid, weight)
            else:
                dbutil.update_company_tag(self.db, cid, tid, weight)
            # print dbutil.get_tag_info(self.db, tid, 'name'), tid, weight
        return vips.keys()

    def review(self, cid, contents):

        global logger_tag
        # load active tags
        tags = {t.tid: t for t in dbutil.get_company_tags_info(self.db, cid)}
        chains, merged = [], set()
        chain_candidates = {}
        for rel in dbutil.analyze_tags_relations(self.db, tags.keys(), 54041):
            chain_candidates.setdefault(rel.tagId, []).append(rel.tag2Id)
        for t1, t2s in chain_candidates.iteritems():
            for t2 in t2s:
                if (t1, t2) in merged:
                    continue
                if tags.get(t1).get('sector', False) == 1 and chain_candidates.get(t2, False):
                    for t3 in chain_candidates.get(t2, []):
                        chains.append([t1, t2, t3])
                        merged.add((t2, t3))
                else:
                    chains.append([t1, t2])
        chains = {index: [tags.get(tid).get('name') for tid in chain] for index, chain in enumerate(chains)}
        if len(chains) == 0:
            return

        # support selection
        supports = {}
        for index, (content, dweight) in enumerate(contents):
            for word in self.wfilter([x[0] for x in self.tagger.tag(content)]):
                if word not in self.w2v:
                    continue
                for index, chain in chains.iteritems():
                    similarity = self.w2v.n_similarity([tag for tag in chain if tag in self.w2v], [word])
                    if similarity > self.chain_simi_threshold:
                        supports[index] = supports.get(index, 0) + dweight * similarity
        major = sorted(supports.iteritems(), key=lambda x: -x[1])[0][0]
        self.mongo.keywords.majorchain.update({'company': cid}, {'company': cid, 'major': chains.get(major)}, True)

        # delete outliers
        (outliers1, outliers2) = self.__detect_outliers(tags.values())
        if len([t.tid for t in tags.itervalues() if t.type in (11012, 11013)]) > 5:
            if outliers2:
                delete2 = sorted(outliers2, key=lambda x: self.thesaurus_ids.get(x, 4))[0]
                logger_tag.info('delete outlier %s of %s' % (delete2, cid))
                dbutil.update_company_tag(self.db, cid, delete2, 0, active='N')

    def __detect_outliers(self, tags):

        tids = set([t.tid for t in tags])
        vip_count = len([t.tid for t in tags if t.type == 11012])
        outliers = {}
        for tag in tags:
            if tag.verify and tag.verify == 'Y':
                continue
            if vip_count > 2 and tag.type == 11012:
                if not (set(dbutil.get_hyponym_tags(self.db, tag.tid, 1)) & tids):
                    outliers.setdefault(1, []).append(tag.tid)
            if tag.type == 11013:
                supports = set(dbutil.get_hyponym_tags(self.db, tag.tid, 2)) | \
                           set(dbutil.get_hypernym_tags(self.db, tag.tid))
                if not (supports & tids):
                    outliers.setdefault(2, []).append(tag.tid)
        return outliers.get(1, []), outliers.get(2, [])

    def update_contents_tags(self, cid, tags, source_tags, vips, topn):

        """
        normalize contents based tags and update mysql
        """

        old_tags = dbutil.get_company_tags_old(self.db, cid)
        new_tags = []
        for tag, weight in sorted(tags.items(), key=lambda x: -x[1])[:topn]:
            tid, active = dbutil.get_tag_id(self.db, tag)
            if tag in source_tags:
                weight += 0.009
            if tid in self.vip_tags.values():
                continue
            if active:
                new_tags.append(tid)
            if self.replacements.get(tid):
                new_tags.remove(tid)
                for rtid in self.replacements.get(tid, []):
                    if rtid in self.vip_tags.values():
                        continue
                    dbutil.update_company_tag(self.db, cid, rtid, weight, active=active)
                    new_tags.append(rtid)
            else:
                dbutil.update_company_tag(self.db, cid, tid, weight, active=active)
        # add classifed tags
        try:
            content = list(self.feeder.feed_seged(cid))
            if u'区块链' not in content:
                pass
            else:
                content = [np.mean([self.w2v[w] for w in content if w in self.w2v], axis=0)]
                for tid, clf in self.trained_tag_clfs.iteritems():
                    if clf.predict(content)[0] == 1:
                        dbutil.update_company_tag(self.db, cid, tid, 2.806, verify='N', active='Y')
                        new_tags.append(tid)
        except Exception, e:
            logger_tag.exception('Fail to classify, due to %s', e)
        # remove old tags
        remove_tags = [tid for tid in old_tags if (tid not in new_tags and tid not in self.yellows and tid not in vips)]
        return new_tags, remove_tags

    def extract_without_update(self, cid, topn=15):

        contents = list(self.feeder.feed(cid))
        results = {}
        if len(contents) > self.max_contents_length:
            contents = sorted(contents, key=lambda x: -x[1])[:self.max_contents_length]

        # important tag
        results = self.merge(results, self.__extract_important(contents), 1)
        # regular tag
        results = self.merge(results, dict(self.__extract_textrank(contents, topn)))
        # verified tag
        results = self.merge(results, dict.fromkeys(dbutil.get_company_tags_verified(self.db, cid), 1))
        # normalize
        results = self.__normalize(results)
        # update contents based tags
        results = self.__normalize_replacement(results)
        new_tags = self.update_vip_tags(cid, results, [])
        for tag, weight in sorted(results.items(), key=lambda x: -x[1])[:topn]:
            tid, active = dbutil.get_tag_id(self.db, tag)
            if tid in self.vip_tags.values():
                continue
            if active:
                new_tags.append(tid)
        return new_tags

    def extract_all(self):

        global logger_tag
        db_back = dbcon.connect_torndb()
        for cid in dbutil.get_all_company_id(db_back):
            try:
                self.extract(cid)
                logger_tag.info('%s processed' % cid)
            except Exception, e:
                logger_tag.exception('%s, %s' % (cid, e))
        db_back.close()

    def merge(self, d1, d2, weight=0):

        # weight is a bonus weight
        for k, v in d2.iteritems():
            d1[k] = d1.get(k, 0) + v + weight
        return d1

    def __normalize(self, d):

        if not d:
            return d
        normalizer = max(d.values()) + 1.0
        for tag, weight in d.items():
            d[tag] = round(weight/normalizer, 2)
        return d

    def __load_weighted_tags(self, tid=False):

        if not tid:
            return {tag.name: (tag.novelty or 1) for tag in dbutil.get_tags_by_type(self.db)}
        else:
            return {tag.id: (tag.novelty or 1) for tag in dbutil.get_tags_by_type(self.db)}

    def __load_junk_tags(self):

        return set(tag.name for tag in dbutil.get_tags_by_type(self.db, typeset=([11001])))

    def reload_replacements(self):

        self.replacements = {r['source']: r['replacement'] for r in self.mongo.keywords.replacement.find()}

    def redirect(self):

        for replacement in self.mongo.keywords.replacements.find({'active': 'Y'}):
            source, replace = replacement.get('source'), replacement.get('replacement')
            dbutil.update_tag_type(self.db, source, 11003, with_tag_id=True)
            for cid in dbutil.get_company_from_tag(self.db, source):
                dbutil.update_company_tag(self.db, cid, source, 0, active='N')
                for rtid in replace:
                    dbutil.update_company_tag(self.db, cid, rtid, 1, active='Y')


def init_kafka():

    global producer_tag, consumer_tag

    url = tsbconfig.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    producer_tag = SimpleProducer(kafka)
    consumer_tag = KafkaConsumer("aggregator_v2", group_id="keyword_extract",
                                 bootstrap_servers=[url], auto_offset_reset='smallest')


def incremental_extract():

    global logger_tag, consumer_tag, producer_tag
    logger_tag.info('Incremental keyword extraction initializing')
    cach = FixLenList(10)
    extractor = Extractor()
    socket.setdefaulttimeout(0.5)
    init_kafka()

    while True:
        try:
            logger_tag.info('Incremental keyword extraction starts')
            for message in consumer_tag:
                try:
                    if message.offset % 100 == 0:
                        extractor.reload_replacements()
                        logger_tag.info('Replacements reloaded')
                    locker = open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'tag.lock'))
                    fcntl.flock(locker, fcntl.LOCK_EX)
                    logger_tag.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                   message.offset, message.key,
                                                                   message.value))
                    cid = json.loads(message.value).get('id')
                    action = json.loads(message.value).get('action', 'create')
                    visible = json.loads(message.value).get('visible', True)
                    if (not cid) or (cid == 'None'):
                        consumer_tag.commit()
                        continue
                    if action == 'create':
                        if cid in cach:
                            logger_tag.info('company %s in cach' % cid)
                            cach.remove(cid)
                            producer_msg = {"id": cid, 'action': action}
                            producer_tag.send_messages("keyword_v2", json.dumps(producer_msg))
                            continue
                        extractor.extract(cid)
                        cach.append(cid)
                        logger_tag.info('company %s tags extracted' % cid)
                    consumer_tag.commit()
                    producer_msg = {"id": cid, 'action': action}
                    if action == 'delete':
                        if json.loads(message.value).get('artifactId'):
                            producer_msg["artifactId"] = json.loads(message.value).get('artifactId')
                        if json.loads(message.value).get('aliasId'):
                            producer_msg["aliasId"] = json.loads(message.value).get('aliasId')
                    if visible:
                        try:
                            producer_tag.send_messages("keyword_v2", json.dumps(producer_msg))
                        except FailedPayloadsError, fpe:
                            logger_tag.exception('Kafka Payload Error, re-init')
                            init_kafka()
                            producer_tag.send_messages("keyword_v2", json.dumps(producer_msg))
                    else:
                        logger_tag.info('No need to re-index %s' % cid)
                except Exception, e:
                    logger_tag.exception("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                                        message.offset, message.key,
                                                                        message.value))
                    logger_tag.exception(e)
                finally:
                    fcntl.flock(locker, fcntl.LOCK_UN)
                    locker.close()
        except Exception, e:
            logger_tag.error('Outside#%s' % e)


class RuleBasedExtractor(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.client = SearchClient()

    def replace(self):

        for replacement in self.mongo.keywords.replacement.find({'active': 'Y'}):
            source = replacement.get('source')
            replaces = replacement.get('replacement')
            if len(replaces) > 1 and dbutil.get_tag_info(self.db, source, 'type') >= 11010:
                for c in reduce(lambda x, y: x & y,
                                [set(dbutil.get_company_from_tag(self.db, replace)) for replace in replaces]):
                    dbutil.update_company_tag(self.db, c, source, 1.503, 'P')

    def infer_hierarchically(self):

        global logger_tag
        for t2 in dbutil.get_sectored_tags(self.db, 2):
            t3s = dbutil.get_tags_by_relation(self.db, t2.id, 54041)
            if t3s:
                check_point = datetime.now() - timedelta(hours=2)
                t1s = dbutil.get_hypernym_tags(self.db, t2.id, 1)
                hierachicals = (set(dbutil.get_company_from_tags(self.db, list(t3s))) &
                                set(dbutil.get_company_from_tags(self.db, t1s)))
                if len(hierachicals) > 2500:
                    dbutil.clear_company_common_tag(self.db, t2.id, check_point)
                    logger_tag.exception('Hierachical cross threshold, %s, %s' % (t2.name, len(hierachicals)))
                else:
                    for c in hierachicals:
                        dbutil.update_company_tag(self.db, c, t2.id, 1.504, 'P')
                    dbutil.clear_company_common_tag(self.db, t2.id, check_point)
                    logger_tag.info('Hierachically processed %s' % t2.name)

    def infer_rules(self):

        global logger_tag
        for t in dbutil.get_ruled_tags(self.db):
            logger_tag.info('Processing rule for %s' % t.name)
            try:
                rule = t.rule.replace(u'，', u',').replace(u'（', u'(').replace(u'）', u')').replace(u' ', u'').lower()
                rule = generate_rule_based_query(rule)
                if rule:
                    codes = self.client.search('topic', query=rule).get('company', {}).get('data', [])
                    if len(codes) > 2000:
                        logger_tag.exception('To many results, %s, %s' % (t.name, len(codes)))
                    else:
                        logger_tag.info('%s processed' % t.name)
                        for code in codes:
                            cid = dbutil.get_id_from_code(self.db, code)
                            if not dbutil.exist_company_tag(self.db, cid, t.id):
                                dbutil.update_company_tag(self.db, cid, t.id, 1.505)
            except Exception, e:
                logger_tag.exception('Fail to process tag rules %s, due to %s' % (t.name, e))


def full_extract():

    e = Extractor()
    e.extract_all()


def makup_extract():

    global logger_tag
    e = Extractor()
    db = dbcon.connect_torndb()
    for cid in dbutil.get_company_ids_by_modify(db, 1):
        e.extract(cid)
        logger_tag.info('%s extracted' % cid)


def re_weight():

    db = dbcon.connect_torndb()
    for item in db.query('select company_tag_rel.*, tag.type tt from company_tag_rel, tag where tagId=tag.id and '
                         'tag.type in (11011, 11012, 11013) and company_tag_rel.verify="N" and '
                         '(company_tag_rel.active is null or company_tag_rel.active="Y")'):
        if item.tt == 11012:
            conf = item.confidence - floor(item.confidence) + 1
        else:
            conf = item.confidence - floor(item.confidence) + 1
        db.execute('update company_tag_rel set confidence=%s where companyId=%s and tagId=%s;',
                   round(conf, 3), item.companyId, item.tagId)
        print item.companyId, item.tagId


def rule_based():

    rbe = RuleBasedExtractor()
    rbe.infer_rules()
    rbe.infer_hierarchically()


class RedirectTagger(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

    def redirect(self):

        for replacement in self.mongo.keywords.replacement.find({'active': 'Y'}):
            source, replace = replacement.get('source'), replacement.get('replacement')
            dbutil.update_tag_type(self.db, source, 11003, with_tag_id=True)
            for cid in dbutil.get_company_from_tag(self.db, source):
                dbutil.update_company_tag(self.db, cid, source, 0, active='N')
                for rtid in replace:
                    dbutil.update_company_tag(self.db, cid, rtid, 1, active='Y')


if __name__ == '__main__':

    print __file__

    if sys.argv[1] == 'incr' or sys.argv[1] == 'incremental':
        incremental_extract()
    elif sys.argv[1] == 'full':
        full_extract()
    elif sys.argv[1] == 'single':
        e = Extractor()
        e.extract(int(sys.argv[2]))
    elif sys.argv[1] == 'makeup':
        makup_extract()
    elif sys.argv[1] == 'reweight':
        re_weight()
    elif sys.argv[1] == 'rbe':
        rule_based()
    elif sys.argv[1] == 'redirect':
        rt = RedirectTagger()
        rt.redirect()
