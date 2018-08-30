# coding=utf-8
__author__ = 'wangqc'


import os
import sys
import logging
import math
from datetime import datetime, timedelta

import pymongo
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil


# logging
# logger_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'logs/tmp.log')
logging.basicConfig(level=logging.INFO, format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
logger_apkdownload = logging.getLogger('logger_apkdownload')


class Download_Optimization():

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.model = LinearRegression(fit_intercept=False)

        self.markets = (16010, 16020, 16030, 16040)
        self.sectors = [t.id for t in dbutil.get_tags_by_type(self.db, (11012,))]
        self.round_groups = {(1000, 1010, 1011, 1020): 'Pre-A',
                             (1030, 1031, 1039, 1040, 1041): 'A~B',
                             (1050, 1060, 1070, 1080, 1090, 1100, 1105, 1106, 1110): 'Post-B'}

        # day_range: (start_date, end_date)
        self.default_day_range = (100, 0)
        self.top_share = 0.05
        self.coef_threshold = 2
        self.modify_outlier = False

    def _get_cid_apk_pairs_by_sector_rounds(self, db, sector, round_group):

        sql_find_cid = '''
        select distinct c.id
        from company c join corporate cor on c.corporateId = cor.id join company_tag_rel ctr on c.id = ctr.companyId
        where ctr.tagId = %s and (c.active is null or c.active='Y') and c.type = 41010
        and c.round in %s and (ctr.active is null or ctr.active='Y')
        '''
        sql_find_apk = "select domain from artifact where companyId=%s and type = 4050 and (active is null or active ='Y')"

        return {cid.id: [apk.domain for apk in db.query(sql_find_apk % cid.id)] for cid in db.query(sql_find_cid % (sector, round_group))}

    def _train_model(self, apk, market, day_range=None, download_lower_bound=1000):

        day_range = day_range or self.default_day_range
        if day_range[0] < day_range[1]:
            raise ValueError("End day should be earlier than start day.")
        df = pd.DataFrame(list(self.mongo.trend.android.find({'apkname': apk, 'appmarket': market,
                                            'date': {'$gte': datetime.today() - timedelta(day_range[0]),
                                                     '$lte': datetime.today() - timedelta(day_range[1])}}).sort([('date', 1)])))
        try:
            download, date = df['download'], df['date']
        except KeyError:
            return False
        download = np.array(download.fillna(0.0))
        if not download.any() or download[-1] < download_lower_bound:
            return False
        date = np.array([np.datetime64(d, 'D') for d in date])
        # y = np.array([np.float64(download[i+1] - download[i]) / np.float64(date[i+1] - date[i]) for i in xrange(len(download) - 1)])
        y = np.float64(download[1:] - download[:-1]) / np.float64(date[1:] - date[:-1])
        y[np.isnan(y)] = 0.0
        if self.modify_outlier:
            y = np.clip(y, 0, np.percentile(y, 97))
        X = np.arange(len(y)).reshape((-1, 1))
        try:
            self.model.fit(X, y)
        except ValueError:
            return False
        else:
            return True


    def _get_top_coef_by_sector_rounds(self, sector, round_group, top_share):

        cid_apk_pairs = self._get_cid_apk_pairs_by_sector_rounds(self.db, sector, round_group)
        cid_coef_pairs = []
        for cid, apks in cid_apk_pairs.items():
            temp_coef = 0.0
            for apk in apks:
                for market in self.markets:
                    if self._train_model(apk, market):
                        temp_coef = max(temp_coef, self.model.coef_)
            cid_coef_pairs.append((cid, temp_coef))
        return sorted(cid_coef_pairs, key=lambda x: x[1], reverse=True)[: int(len(cid_coef_pairs) * top_share)]


    def get_nice_download_cids(self, top_share=None, coef_threshold=None, sectors=None):

        top_share = top_share or self.top_share
        coef_threshold = coef_threshold or self.coef_threshold
        sectors = sectors or self.sectors
        count_cid = 0
        for sector in sectors:
            logger_apkdownload.info("Dealing tag id: %s", sector)
            count_sector_cid = 0
            for round_group in sorted(self.round_groups):
                count_sector_round_cid = 0
                for cid, coef in self._get_top_coef_by_sector_rounds(sector, round_group, top_share):
                    if coef >= coef_threshold:
                        yield cid, math.log(coef, 2)
                        count_sector_round_cid += 1
                logger_apkdownload.info('Tag id: %s Round: %s Nice download company amount: %s'
                                        % (sector, self.round_groups[round_group], count_sector_round_cid))
                count_sector_cid += count_sector_round_cid
            logger_apkdownload.info('Tag id: %s Nice download company amount: %s' % (sector, count_sector_cid))
            count_cid += count_sector_cid
        logger_apkdownload.info('Total nice download company amount: %s' % count_cid)


def test():

    test_do = Download_Optimization()
    with open('tmp/test_nice_download_output', 'w') as f:
        # 40 游戏
        for cid, score in test_do.get_nice_download_cids(sectors=[22, 40, 107]):
            f.write(dbutil.get_company_code(test_do.db, cid))
            f.write(' ')
            f.write(str(round(score, 4)))
            f.write('\n')


def main():

    do = Download_Optimization()
    for cid, score in do.get_nice_download_cids():
        # 566646 下载优秀
        logger_apkdownload.info("Insert into company_tag_rel: companyid %s, tagid 566646", cid)
        # dbutil.update_company_tag(do.db, cid, 566646, round(score, 4), "Y")
    do.db.close()


if __name__ == "__main__":

    # test()
    main()
