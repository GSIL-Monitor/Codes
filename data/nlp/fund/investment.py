# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil
from classifier.simple_sector import SimpleSectorClassifier

import json
import logging
import gridfs
import pandas as pd
from copy import deepcopy

# logging
logging.getLogger('fund').handlers = []
logger_fund = logging.getLogger('fund')
logger_fund.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_fund.addHandler(stream_handler)


class InvestmentEvents(object):

    def __init__(self, split=True):

        self.db = dbcon.connect_torndb()
        self.clf = SimpleSectorClassifier()
        self.gfs = self.__init_mongo()

        if split:
            self.data = self.split()
        else:
            self.data = self.fetch()

    def __init_mongo(self):

        global logger_fund
        try:
            mongo = dbcon.connect_mongo()
            return gridfs.GridFS(mongo.gridfs)
        except Exception, e:
            logger_fund.error('Mongodb connection error#%s' % e)
            return

    def plot_all(self):

        global logger_fund
        for iid in set(self.data.investor):
            try:
                self.prepare_graphs(iid)
            except Exception, e:
                logger_fund.exception('Failed %s' % iid)

    def prepare_graphs(self, iid):

        global logger_fund

        # investor outstanding companies
        dbutil.update_investor_outstanding_companies(self.db, iid, self.__generate_star_companies(iid), 48001)
        dbutil.update_investor_outstanding_companies(self.db, iid, self.__generate_favourite_companies(iid), 48002)

        # investing size
        try:
            mid = self.gfs.put(json.dumps(self.__generate_investing_size(iid)),
                               content_type='json', filename='%s_size' % str(iid))
            dbutil.update_investor_chart(self.db, iid, 49001, mid)
            logger_fund.info('%s investing size chart stored' % iid)
        except Exception, e:
            logger_fund.exception('Failed investing size chart, %s # %s' % (iid, e))

        # development
        try:
            mid = self.gfs.put(json.dumps(self.__generate_development(iid)),
                               content_type='json', filename='%s_development' % str(iid))
            dbutil.update_investor_chart(self.db, iid, 49003, mid)
            logger_fund.info('%s development chart stored' % iid)
        except Exception, e:
            logger_fund.exception('Failed development chart, %s # %s' % (iid, e))

        # history
        try:
            mid = self.gfs.put(json.dumps(self.__generate_history(iid)),
                               content_type='json', filename='%s_history' % str(iid))
            dbutil.update_investor_chart(self.db, iid, 49002, mid)
            logger_fund.info('%s history chart stored' % iid)
        except Exception, e:
            logger_fund.exception('Failed history chart, %s # %s' % (iid, e))

    def __generate_history(self, iid):

        results = {}

        df = self.data[self.data['investor'] == iid]
        df['fundingDate'] = df.apply(lambda x: x[2].year, 1)
        top5sector = sorted(dict(df.groupby('sector').size()).items(), key=lambda x: x[1], reverse=True)[:5]
        top5sector = [x[0] for x in top5sector]
        df['sector'] = df.apply(lambda x: x[7] if x[7] in top5sector else u'其他', 1)

        sectors = sorted(list(set(df.sector)))
        series = []
        for year, ydf in df.groupby('fundingDate'):
            annual = []
            for sector, sdf in ydf.groupby('sector'):
                annual.append([sdf.id.count(), sdf.investment.sum(), sdf.investment.sum(), sector, year])

            # mark lacking sector as a default close-zero record
            exist_sector = [item[3] for item in annual]
            lack_sector = [sector for sector in sectors if sector not in exist_sector]
            for sector in lack_sector:
                annual.append([0.01, 0.01, 0.01, sector, year])
            annual.sort(key=lambda x: x[3])

            series.append(annual)
        results['series'] = series
        results['timeline'] = sorted(list(set(df.fundingDate)))
        results['sector'] = sectors
        return results

    def __generate_investing_size(self, iid):

        df = self.data[self.data['investor'] == iid]
        df['fundingDate'] = df.apply(lambda x: '%s0%s' % (x[2].year, (x[2].month-1 or 0)/3+1), 1)
        funding_date, count, amount = [], [], []
        for fdate, ddf in df.sort('fundingDate').groupby('fundingDate'):
            funding_date.append(fdate)
            count.append(len(set(ddf.id)))
            amount.append(ddf.investment.sum())
        return {'date': funding_date, 'amount': amount, 'count': count}

    def __generate_development(self, iid):

        df = self.data[self.data['investor'] == iid]
        cdfs = self.data[self.data.companyId.isin(set(df.companyId.values))]

        development = {}
        for row in df.iterrows():
            row = row[1]
            development.setdefault(row.sector, []).append(
                cdfs[(cdfs['companyId'] == row.companyId) & (cdfs['fundingDate'] > row.fundingDate)].id.count()
            )
        results = {}
        for k, v in development.items():
            count = [v.count(0), v.count(1), v.count(2), v.count(3)]
            max_value = sum(count)
            results[k] = map(lambda x: int(x*1.0/max_value*100),
                             [sum(count), sum(count[1:]), sum(count[2:]), sum(count[3:])])
        return results

    def __generate_star_companies(self, iid, count=5):

        df = self.data[self.data['investor'] == iid]
        cids = map(int, list(self.data[self.data.companyId.isin(set(df.companyId.values))].
                             sort('investment', ascending=False).companyId))
        results = []
        for cid in cids:
            if len(results) == count:
                return results
            if cid in results:
                continue
            results.append(cid)
        return results

    def __generate_favourite_companies(self, iid, count=5):

        cids = dict(self.data[self.data['investor'] == iid].groupby('companyId').size())
        cids = sorted(cids.iteritems(), key=lambda x: x[1], reverse=True)[:count]
        return [int(cid[0]) for cid in cids]

    def fetch(self):

        df = pd.DataFrame(self.db.query('select id, companyId, investment, round, currency, precise, fundingDate '
                                        'from funding where (fundingType is null or fundingType=8030) '
                                        'and (active is null or active="Y");'))
        df.set_index('id')

        # normalize the currency and amount of investment
        df['investment'] = df.apply(self.__normalize_investment, 1)
        del df['currency']
        del df['precise']

        # insert investors
        df['investors'] = df.apply(self.__get_investors, 1)

        # remove no_investors/zero_investment
        df = df.drop(df[(df.investors == "") | (df.investment == 0)].index)

        # insert tags
        df['tags'] = df.apply(self.__get_tags, 1)
        df = df.drop(df[df.tags == ""].index)

        # insert sector
        df['sector'] = df.apply(self.__get_sector, 1)

        return df

    def split(self):

        df = self.fetch()
        spdf = pd.DataFrame()
        for cid, cdf in df.groupby('companyId'):
            pastiids = set([])
            for row in cdf.sort('fundingDate').iterrows():
                row = row[1]
                iids = [int(investor) for investor in row.investors.split(';')]
                newin = len([iid for iid in iids if iid not in pastiids])
                wasin = len(iids) - newin
                follow_share = {
                    True: int(row.investment * 0.2 / wasin) if wasin else 0,
                    False: int(row.investment * 0.8 / newin) if newin else 0
                }
                for iid in iids:
                    newrow = deepcopy(row)
                    newrow['investor'] = iid
                    newrow['investment'] = follow_share[iid in pastiids]
                    newrow['follow'] = iid in pastiids
                    spdf = spdf.append(newrow)
                pastiids.update(iids)

        del spdf['investors']
        return spdf

    def __get_investors(self, item):

        return ';'.join([str(x.investorId) for x in self.db.query('select distinct investorId '
                                                                  'from funding_investor_rel '
                                                                  'where fundingId=%s;', item[2])])

    def __get_sector(self, item):

        return self.clf.classify(self.__get_tags(item).split(';'))

    def __get_tags(self, item):

        tags = [x.name.strip() for x in self.db.query('select tag.name as name from company_tag_rel, tag '
                                                      'where company_tag_rel.companyId=%s and tag.name is not null '
                                                      'and company_tag_rel.tagId=tag.id and tag.type=11012 '
                                                      'and company_tag_rel.active="Y";', item[0])]
        sector = dbutil.get_company_sector(self.db, item[0], name=True)
        tags.extend(sector)
        return ';'.join(tags)

    def __normalize_investment(self, item):

        currency, precise, investment = item[1], item[5], item[4]
        if precise == 'N':
            if investment == 1000000:
                investment = 2000000
            elif investment == 100000:
                investment = 500000
        return {
            3010: 6.5,
            3020: 1,
            3030: 4.5
        }[currency] * investment


class InvestmentEvents2(object):

    def __init__(self, split=False):

        self.db = dbcon.connect_torndb()
        self.clf = SimpleSectorClassifier()
        if split:
            self.data = self.split()
        else:
            self.data = self.fetch()

    def fetch(self):

        df = pd.DataFrame(self.db.query('select id, companyId, investment, round, currency, precise, fundingDate '
                                        'from funding where (fundingType is null or fundingType=8030) '
                                        'and (active is null or active="Y");'))
        df.set_index('id')

        # normalize the currency and amount of investment
        df['investment'] = df.apply(self.__normalize_investment, 1)
        del df['currency']
        del df['precise']

        # insert investors
        df['investors'] = df.apply(self.__get_investors, 1)

        # remove no_investors/zero_investment
        df = df.drop(df[(df.investors == "") | (df.investment == 0)].index)

        # insert tags
        df['tags'] = df.apply(self.__get_tags, 1)
        df = df.drop(df[df.tags == ""].index)

        # insert sector
        df['sector'] = df.apply(self.__get_sector, 1)

        return df

    def split(self):

        df = self.fetch()
        spdf = pd.DataFrame()
        for cid, cdf in df.groupby('companyId'):
            pastiids = set([])
            for row in cdf.sort('fundingDate').iterrows():
                row = row[1]
                iids = [int(investor) for investor in row.investors.split(';')]
                newin = len([iid for iid in iids if iid not in pastiids])
                wasin = len(iids) - newin
                follow_share = {
                    True: int(row.investment * 0.2 / wasin) if wasin else 0,
                    False: int(row.investment * 0.8 / newin) if newin else 0
                }
                for iid in iids:
                    newrow = deepcopy(row)
                    newrow['investor'] = iid
                    newrow['investment'] = follow_share[iid in pastiids]
                    newrow['follow'] = iid in pastiids
                    spdf = spdf.append(newrow)
                pastiids.update(iids)

        del spdf['investors']
        return spdf

    def __get_investors(self, item):

        return ';'.join([str(x.investorId) for x in self.db.query('select distinct investorId '
                                                                  'from funding_investor_rel '
                                                                  'where fundingId=%s;', item[2])])

    def __get_sector(self, item):

        return self.clf.classify2(self.__get_tags(item).split(';'))

    def __get_tags(self, item):

        tags = [x.name.strip() for x in self.db.query('select tag.name as name from company_tag_rel, tag '
                                                      'where company_tag_rel.companyId=%s and tag.name is not null '
                                                      'and company_tag_rel.tagId=tag.id '
                                                      'and company_tag_rel.active="Y";', item[0])]
        # sector = dbutil.get_company_sector(self.db, item[0], name=True)
        # tags.extend(sector)
        return ';'.join(tags)

    def __normalize_investment(self, item):

        currency, precise, investment = item[1], item[5], item[4]
        if precise == 'N':
            if investment == 1000000:
                investment = 2000000
            elif investment == 100000:
                investment = 500000
        return {
            3010: 6.5,
            3020: 1,
            3030: 4.5
        }[currency] * investment


if __name__ == '__main__':

    if sys.argv[1] == 'plotall':
        ie = InvestmentEvents()
        ie.plot_all()
    elif sys.argv[1] == 'plotone':
        ie = InvestmentEvents()
        ie.prepare_graphs(int(sys.argv[2]))