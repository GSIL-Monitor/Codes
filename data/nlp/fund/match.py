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

import codecs
import numpy as np
from itertools import chain
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class FundMatcher(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.funds = dict(dbutil.get_all_investor(self.db))
        self.fund_profiles, self.fund_mapping, self.transformer = self.init_profile()
        self.fund_rounds, self.activeness, self.locations = self.init_filter()

    def init_profile(self):

        fund_profiles = {iid: dbutil.get_investor_profile(self.db, iid, '2016-01-01') for iid in self.funds.keys()}
        mapping, profiles = {}, []
        for index, (iid, features) in enumerate(fund_profiles.iteritems()):
            mapping[index] = iid
            profiles.append(features)
        v = DictVectorizer()
        profiles = v.fit_transform(profiles)
        return profiles, mapping, v

    def init_filter(self):

        portfilios = {iid: dbutil.get_investor_portfilio(self.db, iid, ('2016-01-01', '2017-10-31'))
                      for iid in self.funds.keys()}
        fund_rounds = {iid: np.mean([dbutil.get_company_round(self.db, p.cid) for p in ps])
                       for iid, ps in portfilios.iteritems()}
        fund_activeness = {iid: len(ps) for iid, ps in portfilios.iteritems()}
        fund_locations = {iid: len(filter(lambda x:
                                          dbutil.get_company_location(self.db, x.cid)[0] < 371, ps)) * 2 > len(ps)
                          for iid, ps in portfilios.iteritems()}
        return fund_rounds, fund_activeness, fund_locations

    def match(self, cid):

        tags = {name: weight for _, name, weight in
                dbutil.get_company_tags_idname(self.db, cid, tag_out_type=(11000, 11001, 11002, 11100, 11054))}
        tags = self.transformer.transform(tags)
        similarities = cosine_similarity(self.fund_profiles, tags)
        similarities = {self.fund_mapping.get(index): s for index, s in enumerate([s[0] for s in similarities])}
        # similarities = filter(lambda item: 1020 <= self.fund_rounds.get(item[0]) < 1040, similarities)
        # similarities = filter(lambda item: self.activeness.get(item[0]) > 3, similarities)
        investor_comps = list(chain(*[dbutil.get_company_investors(self.db, comp)
                                      for comp in dbutil.get_company_comps(self.db, cid)]))
        for ic in set(investor_comps):
            similarities[ic] = similarities.get(ic, 0) * investor_comps.count(ic) + 1
        similarities = sorted(similarities.items(), key=lambda x: -x[1])
        famous = set(dbutil.get_online_investors(self.db))
        with codecs.open('dumps/fund', 'w', 'utf-8') as fo:
            for iid, weight in similarities:
                fo.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (self.funds.get(iid), weight, iid in famous,
                                                       self.fund_rounds.get(iid), self.activeness.get(iid),
                                                       self.locations.get(iid)))


if __name__ == '__main__':

    print __file__
    fm = FundMatcher()
    fm.match(152766)
