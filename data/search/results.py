# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

from nlp.common import dicts

from itertools import combinations
from math import log


def log2(x):

    if int(x) == 0:
        return -10000
    return log(x, 2)


class ResultAnalyzer(object):

    yellows = set(dicts.get_yellow_tags_name())

    def __init__(self):

        self.prompt_tag_size = 6
        self.max_trigger_count = 30000
        self.min_trigger_count = 50
        self.min_tag_portion = 0.005
        self.max_tag_candidate = 10

    def prompt_filter(self, hits):

        return self.__prompt_tag_filter(hits)

    def __prompt_tag_filter(self, hits):

        if ('error' in hits) or hits.get('time_out'):
            return []
        if self.min_trigger_count < hits.get('hits', {}).get('total', 0) < self.max_trigger_count:
            total = float(hits.get('hits', {}).get('total'))
            # 备选tag筛选，大于min_tag_portion,不多于max_tag_candidate
            tags = {}
            for index, data in enumerate(hits.get('hits').get('hits')):
                for tag in data.get('_source', {}).get('tags', []):
                    tags.setdefault(tag, []).append(index)
            tags = {tag: companies for tag, companies in tags.iteritems()
                    if (len(companies) > (total * self.min_tag_portion)) and (tag not in self.yellows)}
            if len(tags) > self.max_tag_candidate:
                tags = dict(sorted(tags.iteritems(), key=lambda x: -len(x[1]))[:self.max_tag_candidate])
            # print 'tags', len(tags)
            # 排列组合挑选entropy最低的组合
            entropy, final_tags = 100000000, []
            for tagset in combinations(tags.keys(), self.prompt_tag_size):
                current_entropy = 0
                no_others = set()
                for tag in tagset:
                    current_entropy -= (len(tags.get(tag))/total)*log2(len(tags.get(tag))/total)
                    no_others = no_others | set(tags.get(tag))
                current_entropy -= ((total-len(no_others))/total)*log2((total-len(no_others))/total)
                if current_entropy < entropy:
                    final_tags = tagset
                    entropy = current_entropy
            return final_tags
        else:
            return []