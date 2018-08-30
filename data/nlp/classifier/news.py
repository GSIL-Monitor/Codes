# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common.zhtools import word_filter, hants
from common.zhtools.postagger import Tagger

from math import ceil
from gensim.models import Word2Vec


word2vec_model = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                              '../embedding/models/s400w4min20.binary.w2vmodel')


class SubSector(object):

    def __init__(self):

        global word2vec_model

        self.mongo = dbcon.connect_mongo()

        self.w2v = Word2Vec.load(word2vec_model)
        self.similarity_threshold = 0.4

        self.important_lower = 0.1
        self.important_threshold = 0.2
        self.important_max_num = 5

        self.tagger = Tagger(tags=True)
        self.wfilter = word_filter.get_default_filter()

    def train(self):

        pass

    def extract_tag(self, nid):

        return self.__extract_itag(nid)

    def __extract_itag(self, nid):

        contents = list(self.mongo.article.news.find({"_id": nid}))[0]['contents']

        # candidates generation
        candidates = {}
        for content in contents:
            for tag in [x[0] for x in self.tagger.tag(content['content']) if x[1] == 'itag' and x[0] in self.w2v.vocab]:
                candidates[tag] = candidates.get(tag, 0)

        # support assginment
        total = 0
        supports = {}
        for index, content in enumerate(contents):
            for word in self.wfilter([x[0] for x in self.tagger.tag(content['content'])]):
                if word not in self.w2v.vocab:
                    continue
                total += 1
                for candidate in candidates.keys():
                    similarity = self.w2v.similarity(candidate, word)
                    if similarity > self.similarity_threshold:
                        supports.setdefault(candidate, []).append((index, 1, similarity))

        # support selection
        results = {}
        for candidate, v in supports.iteritems():
            # if (csize >= 2) and \
            #         (sum([y[1] for y in set([(x[0], x[1]) for x in v])]) < min(6, ceil(float(len(contents))/3))):
            #     continue
            support = sum([round(item[1]*item[2], 2) for item in v])
            results[candidate] = support
        if len(results) == 0:
            return results

        # normalization, max weight equals to 1
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
