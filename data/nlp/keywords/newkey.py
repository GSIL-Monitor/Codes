# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
import loghelper
import config as tsbconfig
from common import dicts, dbutil
from common.zhtools import word_filter, hants
from common.zhtools.segment import Segmenter
from common.zhtools.postagger import Tagger
from common.feed import Feeder
from common.dsutil import UndirectWeightedGraph, FixLenList

import re
import codecs
import collections
from math import ceil
from copy import deepcopy
from itertools import chain

import fasttext
from gensim.models import Word2Vec
from sklearn.externals import joblib

word2vec_model = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                              '../embedding/models/s400w3min20_yitai.binary.w2vmodel')
viptag_model_20171221 = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models/20180319.bin')

loghelper.init_logger('new_key', True)
logger_nk = loghelper.get_logger('new_key')


class KeywordExtractor(object):

    def __init__(self):

        global word2vec_model, viptag_model_20171221
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.feeder = Feeder()
        self.tagger = Tagger(itags=True)
        self.seg = Segmenter(tags=True)
        self.wfilter = word_filter.get_default_filter()

        self.w2v = Word2Vec.load(word2vec_model)
        self.trained_tag_clfs = self.__load_trained_clfs()
        self.vip_classifier = fasttext.load_model(viptag_model_20171221)

        self.yellows = dbutil.get_yellow_tags(self.db)
        self.vip_tags = {t.name: t.id for t in dbutil.get_sectored_tags(self.db, 1)}
        self.hyponym = {vip_name: set([dbutil.get_tag_name(self.db, tid)
                                       for tid in dbutil.get_hyponym_tags(self.db, vip_id)])
                        for vip_name, vip_id in self.vip_tags.iteritems()}
        self.importants = set(t.name.lower() for t in dbutil.get_tags_by_type(self.db, [11011, 11013]))
        self.thesaurus = self.__load_tag_novelties()
        self.thesaurus_ids = self.__load_tag_novelties(tid=True)
        self.tag_types = self.__load_tag_types()
        self.trusted_sources = dicts.get_known_company_source()
        self.replacements = {dbutil.get_tag_name(self.db, r['source']): [dbutil.get_tag_name(self.db, rtid)
                                                                         for rtid in r['replacement']]
                             for r in self.mongo.keywords.replacement.find()}
        self.junk_terms = set(tag.name for tag in dbutil.get_tags_by_type(self.db, typeset=([11001])))

        self.similarity_threshold = 0.4
        self.textrank_window_size = 2
        self.textrank_threshold = 0
        self.source_tag_default_weight = 2
        self.vip_lower = 0.3
        self.important_threshold = 0.2
        self.important_max_count = 5

        print 'model inited'

    def __load_trained_clfs(self):

        model_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models')
        clfs = {}
        for model_file in os.listdir(model_dir):
            if model_file.endswith('.model'):
                tid = model_file.split('.')[0]
                if not isinstance(tid, int):
                    continue
                clfs[dbutil.get_tag_name(self.db, int(tid))] = joblib.load(os.path.join(model_dir, model_file))
        return clfs

    def __load_tag_novelties(self, tid=False):

        if not tid:
            return {tag.name: (tag.novelty or 1) for tag in dbutil.get_tags_by_type(self.db)}
        else:
            return {tag.id: (tag.novelty or 1) for tag in dbutil.get_tags_by_type(self.db)}

    def __load_tag_types(self):

        return {tag.name: (tag.type or 0) for tag in dbutil.get_tags_by_type(self.db)}

    def __extract_source_tag(self, cid):

        tags = dbutil.get_source_company_tags(self.db, cid, self.trusted_sources)
        if tags:
            return set(chain(*[dbutil.analyze_source_tag(self.db, tname, self.replacements)
                               for tname in tags if tname and tname.strip()]))
        return set([])

    def __extract_vecrank(self, candidates, candidates_important, candidates_vips, topn):

        graph = UndirectWeightedGraph()
        weights = collections.defaultdict(int)
        proper_hyponym = dict.fromkeys(set(chain(*[self.hyponym.get(dbutil.get_tag_name(self.db, cv))
                                                   for cv in candidates_vips.iterkeys()])), 2)
        for i in xrange(len(candidates)):
            for j in xrange(i+1, i+self.textrank_window_size):
                if j >= len(candidates):
                    break
                weights[(candidates[i], candidates[j])] += 1
            if candidates[i] not in self.w2v:
                continue
            for word, weight in candidates_important.items():
                if word == candidates[i] or word not in self.w2v:
                    continue
                similarity = self.w2v.similarity(candidates[i], word)
                if similarity > self.similarity_threshold:
                    weights[(candidates[i], word)] += similarity * weight
        for terms, weight in weights.iteritems():
            graph.add_edge(terms[0], terms[1], weight)
        nodes_rank = graph.rank(self.thesaurus, proper_hyponym)
        topn = min(topn, len(candidates))
        start = 0
        for tag, weight in sorted(nodes_rank.items(), key=lambda x: -x[1])[:topn]:
            if tag in self.junk_terms:
                continue
            if start < 2:
                yield tag, round(weight, 2)
            elif weight >= self.textrank_threshold:
                yield tag, round(weight, 2)
            start += 1

    def extract_vip(self, cid):

        desc = ' '.join(self.wfilter(self.seg.cut4search(self.feeder.feed_string(cid, 'with_tag'))))
        if not desc:
            return {}
        classifier_vips = [(int(tag.replace(u'__label__', '')), weight) for (tag, weight) in
                           self.vip_classifier.predict_proba([desc], 2)[0] if weight > self.vip_lower]
        classifier_vips.sort(key=lambda x: -x[1])
        # if 2 candidate vip label, check whether their probability is comparable
        if len(classifier_vips) == 2 and classifier_vips[0][1] > classifier_vips[1][1] * 2:
            return {classifier_vips[0][0]: classifier_vips[0][1]}
        return dict(classifier_vips)

    def __extract_important(self, contents, candidates):

        # support assginment
        supports = deepcopy(candidates)
        for word in contents:
            if word not in self.w2v:
                continue
            for candidate in candidates.keys():
                if candidate not in self.w2v:
                    continue
                similarity = self.w2v.similarity(candidate, word)
                if similarity > self.similarity_threshold:
                    supports[candidate] = supports.get(candidate, 0) + similarity
        # support selection
        results = {}
        candi_size, content_size = len(candidates), len(''.join(candidates))
        for candidate, weight in supports.iteritems():
            if candi_size >= 2 and weight < content_size / 20:
                continue
            results[candidate] = weight * self.thesaurus.get(candidate, 1)
        if len(results) == 0:
            return results
        # normalization
        normalizer = max(results.values())
        for k, v in results.items():
            results[k] = round(v/normalizer, 2)
        # narrow down results size
        if len(results) < 4:
            pass
        else:
            results = dict(filter(lambda x: x[1] > self.important_threshold, results.iteritems()))
            if len(results) > self.important_max_count:
                size = min(10, max(int(ceil(len(results)/2.0)), self.important_max_count))
                results = dict(sorted(results.iteritems(), key=lambda x: -x[1])[:size])
        return results

    def __extract_textrank(self, candidates, topn=15):

        """
        weighted textrank, weights use tags' novelties
        """
        graph = UndirectWeightedGraph()
        weights = collections.defaultdict(int)
        for i in xrange(len(candidates)):
            for j in xrange(i+1, i+self.textrank_window_size):
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
            elif weight >= self.textrank_threshold:
                yield tag, round(weight, 2)
            start += 1

    def __prepare_tag_contents(self, cid):

        # prepare contents
        contents = list(self.feeder.feed(cid, quanlity='medium'))
        candidates = []
        for content, _ in contents:
            candidates.extend([x[0] for x in self.tagger.tag(content)])
        candidates = self.wfilter(candidates)
        source_tags = self.__extract_source_tag(cid)
        candidates_important = {}
        for content, weight in contents:
            for tag in [x[0] for x in self.tagger.tag(content) if x[1] == 'itag' or x[0] in self.importants]:
                candidates_important[tag] = candidates_important.get(tag, 0) + weight
        for tag in source_tags:
            candidates_important[tag] = candidates_important.get(tag, 0) + self.source_tag_default_weight

        return source_tags, candidates, candidates_important

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

    def __normalize(self, d):

        if not d:
            return d
        normalizer = max(d.values()) + 1.0
        for tag, weight in d.items():
            type_promotion = {
                11011: 1,
                11013: 1.5,
                11012: 2.5
            }.get(self.tag_types.get(tag, 0), 0)
            d[tag] = round(weight/normalizer, 2) + type_promotion
        return d

    def merge(self, d1, d2, weight=0):

        # weight is a bonus weight
        for k, v in d2.iteritems():
            d1[k] = d1.get(k, 0) + v + weight
        return d1

    def extract(self, cid, topn=15):

        # prepare contents
        source_tags, candidates, candidates_important = self.__prepare_tag_contents(cid)
        candidates_vips = self.extract_vip(cid)

        # generate results
        results = dict(self.__extract_vecrank(candidates, candidates_important, candidates_vips, topn))
        results = self.merge(results, {dbutil.get_tag_name(self.db, tid): w for tid, w in candidates_vips.iteritems()})
        # results = self.merge(results, self.__extract_important(candidates, candidates_important), 1)
        # results = self.merge(results, dict(self.__extract_textrank(candidates, topn)))
        results = self.__normalize(results)
        results = self.__normalize_replacement(results)
        return results

    def extract_from_text(self, text):

        candidates = []
        for content, _ in text.iteritems():
            candidates.extend([x[0] for x in self.tagger.tag(content)])
        candidates = self.wfilter(candidates)
        candidates_important = {}
        for content, weight in text.iteritems():
            for tag in [x[0] for x in self.tagger.tag(content) if x[1] == 'itag' or x[0] in self.importants]:
                candidates_important[tag] = candidates_important.get(tag, 0) + weight
        desc = ' '.join(self.wfilter(self.seg.cut4search(' '.join(text.keys()))))
        candidates_vips = {int(tag.replace(u'__label__', '')): weight for (tag, weight) in
                           self.vip_classifier.predict_proba([desc], 3)[0] if weight > self.vip_lower}
        results = {}
        results = self.merge(results, self.__extract_important(candidates, candidates_important), 1)
        results = self.merge(results, dict(self.__extract_textrank(candidates, 10)))
        # results = dict(self.__extract_vecrank(candidates, candidates_important, candidates_vips, 10))
        results = self.merge(results, {dbutil.get_tag_name(self.db, tid): w for tid, w in candidates_vips.iteritems()})
        results = self.__normalize(results)
        results = self.__normalize_replacement(results)
        deducts = self.__deduct_2nd(results)
        if len(deducts) < 3:
            results = self.merge(results, deducts)
        return results

    def __deduct_2nd(self, tags):

        deduct = []
        tags = [(dbutil.get_tag_id(self.db, t)[0], t) for t in tags.keys()]
        for (tid, tag) in tags:
            if self.tag_types.get(tag, 0) == 11013:
                t1s = dbutil.get_hypernym_tags(self.db, tid, 1)
                for t1 in set(t1s) & set([t[0] for t in tags]):
                    t2s = set(dbutil.get_hyponym_tags(self.db, t1, 2)) & set(dbutil.get_hypernym_tags(self.db, tid, 2))
                    for t2 in t2s:
                        if t2 not in set([t[0] for t in tags]):
                            deduct.append(t2)
        return {dbutil.get_tag_name(self.db, t2): 2.49 for t2 in deduct}


def do_yitai():

    ke = KeywordExtractor()
    fo = codecs.open('dumps/yitai.0522.out', 'w', 'utf-8')
    for line_index, line in enumerate(codecs.open('files/yitai.0522.in', encoding='utf-8')):
        try:
            data = {}
            data[line.strip()] = 1
            tags = ','.join([t[0].strip() for t in sorted(ke.extract_from_text(data).iteritems(),
                                                          key=lambda x: -x[1])
                             if ke.tag_types.get(t[0]) in {11010, 11011, 11012, 11013}])
            fo.write('%s\n' % tags)
        except Exception, e:
            print line_index, e
            fo.write('\n')
    fo.close()


if __name__ == '__main__':

    do_yitai()
