# -*- coding: utf-8 -*-
__author__ = 'victor'

"""
util of data structure
"""

import collections
import re


class FixLenList(list):

    def __init__(self, length):

        list.__init__(self)
        self.max_length = length

    def append(self, p_object):

        removed = None
        if self.__len__() == self.max_length:
            removed = super(FixLenList, self).pop(0)
        super(FixLenList, self).append(p_object)
        return removed

    def full(self):

        return self.__len__() == self.max_length


class FrozenLenList(list):

    def __init__(self, length):

        list.__init__(self)
        self.max_length = length

    def append(self, p_object):

        if self.__len__() == self.max_length:
            return
        super(FrozenLenList, self).append(p_object)
        return

    def full(self):

        return self.__len__() == self.max_length


class SortedFixLenList(FixLenList):

    def __init__(self, length, key=lambda x: x):

        FixLenList.__init__(self, length)
        self.key = key
        self.sort(key=self.key, reverse=True)

    def append(self, p_object):

        if self.full() and cmp(self.key(p_object), self.key(self.__getitem__(0))) < 1:
            return
        super(SortedFixLenList, self).append(p_object)
        self.sort(key=self.key, reverse=True)


class FixLenDictCach():

    def __init__(self, length):

        self.index = FixLenList(length)
        self.cach = dict()

    def append(self, p_tuple):

        if p_tuple[0] in self.index:
            return
        removed = self.index.append(p_tuple[0])
        if removed:
            del self.cach[removed]
        self.cach[p_tuple[0]] = p_tuple[1]

    def get(self, p_index):

        if p_index in self.index:
            return self.cach.get(p_index)
        return False


class UndirectWeightedGraph(object):

    d = 0.85

    def __init__(self):
        self.graph = collections.defaultdict(list)

    def add_edge(self, start, end, weight):
        # use a tuple (start, end, weight) instead of a Edge object
        self.graph[start].append((start, end, weight))
        self.graph[end].append((end, start, weight))

    def rank(self, prior=None, local_prior=None):

        prior = {} if not prior else prior
        local_prior = {} if not local_prior else local_prior
        weights = collections.defaultdict(float)
        out_sum = collections.defaultdict(float)  # out sum of one node

        # wsdef = 1.0 / (len(self.graph) or 1.0)
        for n, out in self.graph.items():
            # weights[n] = wsdef
            weights[n] = prior.get(n, 0) * 1.5 + 1
            weights[n] = local_prior.get(n, 1) * weights.get(n)
            out_sum[n] = sum((e[2] for e in out), 0.0)

        # this line for build stable iteration
        sorted_keys = sorted(self.graph.keys())
        for x in xrange(20):  # iters
            for n in sorted_keys:
                s = 0
                for e in self.graph[n]:
                    s += e[2] / out_sum[e[1]] * weights[e[1]]
                weights[n] = (1 - self.d) + self.d * s

        max_rank, min_rank = max(weights.values()), min(weights.values())

        for n, w in weights.items():
            weights[n] = (w - min_rank / 10.0) / (max_rank - min_rank / 10.0)

        return weights


def weighted_jaccard(set1, set2):

    sum_up, sum_down = 0, 0
    set1, set2 = dict(set1), dict(set2)
    for tag in (set(set1.keys()) | set(set2.keys())):
        sum_up += min(set1.get(tag, 0), set2.get(tag, 0))
        sum_down += max(set1.get(tag, 0), set2.get(tag, 0))
    return float(sum_up)/sum_down if sum_down else 0


# def construct(prefix_expression):
#
#     operators = [u',', u'+', u'-']
#     pending_terms = []
#     for index, c in enumerate(prefix_expression):
#         if c not in operators:
#             pending_terms.append(SearchTree(c))
#         else:
#             c1, c2 = pending_terms.pop(-1), pending_terms.pop(-1)
#             parent = SearchTree(c)
#             parent.set_child(c1)
#             parent.set_child(c2)
#             c1.set_parent(parent)
#             c2.set_parent(parent)
#             pending_terms.append(parent)
#     return pending_terms


if __name__ == '__main__':

    print __file__

