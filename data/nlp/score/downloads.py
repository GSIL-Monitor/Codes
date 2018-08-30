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

import logging
import pandas as pd
from datetime import datetime, timedelta


# logging
logging.getLogger('android').handlers = []
logger_download = logging.getLogger('android')
logger_download.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_download.addHandler(stream_handler)


app_markets = [16010, 16020, 16030, 16040]


class NoValidDownloadScoreWarning(Warning):

    def __init__(self):
        pass


class DownloadScorer(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

    def update(self, aid, apk):

        global app_markets
        no_valid_record = 1
        for market in app_markets:
            download = evaluate_download(self.mongo, market, [True, apk], aspect='abs')
            growth = evaluate_download(self.mongo, market, [True, apk], aspect='growth')
            valid = self.__check_outlier(download, growth)
            # print '1', market, download, growth
            if valid:
                dbutil.update_source_android(self.db, aid, market, download, growth)
            no_valid_record *= (not valid)
        if no_valid_record:
            raise NoValidDownloadScoreWarning()

    def __check_outlier(self, download, growth):

        if download <= 0 or growth < 0:
            return False
        return True


def source_android_all():

    global logger_download
    database = dbcon.connect_torndb()
    ds = DownloadScorer()
    for item in iter(database.query('select distinct id, domain from artifact where type=4050 and '
                                    '(active is null or active="Y") and domain is not null;')):
        try:
            ds.update(item.id, item.domain)
            logger_download.info('Generate source summary for %s' % item.id)
        except NoValidDownloadScoreWarning:
            logger_download.warning('%s had no valid android score' % item.id)
        except Exception, e:
            logger_download.exception('%s failed %s' % (item.id, e))

    database.close()


def summary_android_all():

    global logger_download, app_markets
    db = dbcon.connect_torndb()

    for source in app_markets:
        groups = db.query('select company.id as cid, company.round as round, count(*) as count '
                          'from company, artifact, source_summary_android '
                          'where company.id=artifact.companyId and source_summary_android.artifactId=artifact.id '
                          'and company.active="Y" and artifact.domain is not null and artifact.type=4050 '
                          'and (artifact.active="Y" or artifact.active is null) '
                          'and source_summary_android.modifyTime>%s and source_summary_android.source=%s '
                          'group by cid having (count>0 and count<5);', datetime.today().date(), source)
        df = pd.DataFrame(groups)
        df['sector'] = df.apply(lambda x: get_sector(db, x), 1)
        df['download'] = df.apply(lambda x: get_best_performance(db, x, source, 'abs'), 1)
        df['growth'] = df.apply(lambda x: get_best_performance(db, x, source, 'growth'), 1)

        # filter out empty result
        df = df.drop(df[df.sector == -1].index)
        df = df.drop(df[df.download == -1].index)
        df = df.drop(df[df.growth == -1].index)

        for sector, sdf in df.groupby(by='sector'):
            for iround, rdf in sdf.groupby(by='round'):
                if rdf.shape[0] < 10:
                    logger_download.warning('No sufficient data %s, %s, %s' % (source, sector, iround))
                else:
                    # first download
                    rdf = rdf.sort_values(by='download', ascending=False)
                    column = rdf.shape[0]
                    for index in xrange(column):
                        cid = rdf.iloc[index].cid
                        # print cid, sector, source
                        if float(index)/column < 0.3:
                            updated = dbutil.update_android_summary(db, cid, sector, source, 30, 'download')
                        elif float(index)/column < 0.7:
                            updated = dbutil.update_android_summary(db, cid, sector, source, 70, 'download')
                        else:
                            updated = dbutil.update_android_summary(db, cid, sector, source, 100, 'download')

                        if updated:
                            yield cid, updated
                    logger_download.info('Rank %s, %s, %s' % (source, sector, iround))
    db.close()


def get_sector(db, row):

    cid = row[0]
    results = db.query('select tag.id as tid, company_tag_rel.confidence as confidence from company_tag_rel, tag '
                       'where (company_tag_rel.active="Y" or company_tag_rel.active is null) '
                       'and company_tag_rel.tagId=tag.id and tag.type=11012 and company_tag_rel.companyId=%s '
                       'order by confidence desc;', cid)
    if results and len(results) > 0:
        return results[0].tid
    return -1


def get_best_performance(db, row, source, aspect='abs'):

    cid = row[0]
    results = db.query('select source_summary_android.download as download, source_summary_android.growth as growth '
                       'from artifact, source_summary_android '
                       'where artifact.companyId=%s and artifact.id=source_summary_android.artifactId '
                       'and source_summary_android.modifyTime>%s and source_summary_android.source=%s '
                       'order by download desc;',
                       cid, datetime.today().date(), source)
    if results and len(results) > 0:
        if aspect == 'abs':
            return results[0].download
        elif aspect == 'growth':
            return results[0].growth
    return -1


def black_android_all():

    global logger_download, app_markets
    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()

    cids = db.query('select company.id as cid, artifact.id as aid, artifact.domain as apk, '
                    'company_tag_rel.tagId as tid, company.round as round '
                    'from company, company_tag_rel, tag, artifact '
                    'where (company.active="Y" or company.active is null) '
                    'and (company_tag_rel.active="Y" or company_tag_rel.active is null) '
                    'and (artifact.active="Y" or artifact.active is null) and artifact.companyId=company.id '
                    'and company_tag_rel.companyId=company.id and company_tag_rel.tagId=tag.id and tag.type=11012 '
                    'and company.round in (1010, 1020) and artifact.domain is not null and artifact.type=4050;')
    results = pd.DataFrame(cids)
    db.close()

    # exclude companies who have more than 5 artifacts
    filtering = results.groupby('cid').agg(lambda x: len(set(x['aid'])))
    filtering = filtering[filtering.aid <= 5].index
    results = results[results['cid'].isin(filtering)]

    # return results
    black = {}
    for sector, sectordf in results.groupby('tid'):
        for iround, rounddf in sectordf.groupby('round'):
            if rounddf.shape[0] < 10:
                continue
            for market in app_markets:
                rounddf['download'] = rounddf.apply(lambda x: evaluate_download(mongo, market, x), 1)
                rounddf = rounddf.drop(rounddf[rounddf.download == -1].index)
                ave = rounddf.download.mean()
                tmp = rounddf.sort_values(by='download', ascending=False)[:10]
                for i in xrange(10):
                    black[int(tmp.iloc[i].cid)] = \
                        black.get(int(tmp.iloc[i].cid), 0) + round(tmp.iloc[i].download/ave, 2)
    # print len(black), black
    mongo.close()
    return black


def evaluate_download(mongo, market, row, aspect='abs'):

    """
    evaluate artifact's download performance,
        abs, absolute download (average download amount over past 7 days)
        growth, 7 days' download delta rate
    """
    df = pd.DataFrame(list(mongo.trend.android.find({'apkname': row[1], 'appmarket': market,
                                                     'date': {'$gt': (datetime.today()-timedelta(days=8))}})))
    if df.shape[0] == 0:
        return 0
    df.fillna(method='pad')
    if aspect == 'abs':
        try:
            return df.download.mean()
        except AttributeError, ae:
            return -1
        except Exception, e:
            download = [int(x) for x in list(df.download)]
            return sum(download)/len(download)
    if aspect == 'growth':
        df = df.sort_values(by='date', ascending=False)
        return round(((df.iloc[0].download - df.iloc[-1].download) / df.iloc[-1].download) * 100, 4)


if __name__ == '__main__':

    print __file__

    # mongo = dbcon.connect_mongo()
    # evaluate_download(mongo, 16010, [u'com.leho.mag.food'])
    # mongo.close()
    # summary_android_all()

    if sys.argv[1] == 'test':
        ds = DownloadScorer()
        print ds.update(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'androidsummary':
        for update in summary_android_all():
            print 'updated', update[0]
    elif sys.argv[1] == 'sourceall':
        source_android_all()
    elif sys.argv[1] == 'androidrank':
        db = dbcon.connect_torndb()
        for cid, score in black_android_all().iteritems():
            dbutil.update_collection(db, 8, cid, score)
        db.close()
