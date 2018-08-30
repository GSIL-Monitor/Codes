# -*- encoding=utf-8 -*-
__author__ = "kailu"


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


logging.getLogger('apkdownload').handlers = []
logger_apkdownload = logging.getLogger('apkdownload')
logger_apkdownload.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_apkdownload.addHandler(stream_handler)


def get_vip_tag_ids(db):
    r = db.query("select id from tag where type=11012 and (active is null or active='Y');")
    return [item.id for item in r]


def get_company_ids_by_tags_rounds(db, tids, rounds):
    r = db.query("select c.id from company c, company_tag_rel ctr where c.id=ctr.companyid and ctr.tagid in %s and (c.active is null or c.active='Y') and c.type = 41010 and c.round in %s and (ctr.active is null or ctr.active='Y');", tids, rounds)
    return [item.id for item in r]


def get_apk_domains_by_companies(db, cids):
    r = db.query("select domain from artifact where companyid=%s and type=4050 and (active is null or active ='Y');", cids)
    return [item.domain for item in r]


class Download_Optimization():

    def __init__(self):
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.model = LinearRegression(fit_intercept=False)

        self.markets = [16010, 16020, 16030, 16040]
        # pre-A, A~B, post-B
        self.round_groups = [[1000,1010,1011,1020],
                             [1030,1031,1039,1040,1041],
                             [1050,1060,1070,1080,1090,1100,1105,1106,1110]]
        self.tid_list = get_vip_tag_ids(self.db)

        self.default_backdayrange = [100, 0]
        self.model_trained_flag = False
        self.top_percentage = 5
        self.coef_threshold = 2

    # backdayrange: back tracking days indicator
    def _get_download_amount(self, apkname, market, backdayrange):
        if backdayrange[0] < backdayrange[1]:
            raise ValueError("endday should no early than startday.")
        startdate = datetime.today() - timedelta(backdayrange[0])
        enddate = datetime.today() - timedelta(backdayrange[1])
        cr = self.mongo.trend.android.find({"apkname":apkname, "appmarket":market, "date":{"$gte":startdate, "$lte":enddate}})
        df = pd.DataFrame(list(cr))
        return df

    def train_model(self, apkname, market, backdayrange=None, download_minimum_threshold=1000):
        if backdayrange is None:
            backdayrange = self.default_backdayrange
        df = self._get_download_amount(apkname, market, backdayrange)
        try:
            result = df.sort_values(by=['date'], ascending=[1])
            ts = result['download']
            ds = result['date']
        except KeyError:
            return []
        a = [i if i else 0.0 for i in ts]
        if not a:
            self.model_trained_flag = False
            return self.model_trained_flag
        if download_minimum_threshold:
            if a[-1] < download_minimum_threshold:
                self.model_trained_flag = False
                return self.model_trained_flag
        b = [np.datetime64(i, 'D') for i in ds]
        # y = [np.float64(a[i+1]-a[i])/np.float64(b[i+1]-b[i])/(math.log(2+a[i],2)) for i in xrange(len(a)-1)]
        y = [np.float64(a[i+1]-a[i])/np.float64(b[i+1]-b[i]) for i in xrange(len(a) - 1)]
        y = [np.float64(0.0) if np.isnan(item) else item for item in y]
        y = np.array(y)
        X = np.arange(len(y)).reshape((len(y), 1))
        try:
            self.model.fit(X, y)
        except ValueError:
            self.model_trained_flag = False
        else:
            self.model_trained_flag = True

        return self.model_trained_flag


    def _get_sorted_coefs_by_tags_rounds(self, tids, rounds):
        cids = get_company_ids_by_tags_rounds(self.db, tids, rounds)
        cid_apknames_pairs = [(cid, get_apk_domains_by_companies(self.db, cid)) for cid in cids]
        cid_coef_pairs = []
        for (cid, apknames) in cid_apknames_pairs:
            temp_coef = 0.0
            for apkname in apknames:
                for market in self.markets:
                    self.train_model(apkname, market)
                    if self.model_trained_flag:
                        if self.model.coef_ > temp_coef:
                            temp_coef = self.model.coef_
            cid_coef_pairs.append((cid, temp_coef))
        return sorted(cid_coef_pairs, key=lambda tup: tup[1], reverse=True)

    def _modify_download_outlier_value(self):
        pass

    def get_nice_download_cids(self, top_percentage=None, coef_threshold=None, tids=None):
        if top_percentage is None:
            top_percentage = self.top_percentage
        if coef_threshold is None:
            coef_threshold = self.coef_threshold
        if tids is None:
            tids = self.tid_list
        nice_cid_list = []
        for tid in tids:
            logger_apkdownload.info("Dealing tag id: %s.", tid)
            for rounds in self.round_groups:
                temp_sorted_cid_coef_pairs = self._get_sorted_coefs_by_tags_rounds([tid], rounds)
                n = len(temp_sorted_cid_coef_pairs) * top_percentage / 100
                temp_nice_cid_list = []
                for (cid, coef) in temp_sorted_cid_coef_pairs[:n]:
                    if coef < coef_threshold:
                        break
                    if cid not in nice_cid_list:
                        nice_cid_list.append(cid)
                        yield (cid, math.log(coef, 2))
                    temp_nice_cid_list.append(cid)
                logger_apkdownload.info("tag id: %s, rounds: %s --- nice donwload company amount: %s.", tid, rounds, len(temp_nice_cid_list))
        logger_apkdownload.info("Distinct nice donwload company amount: %s.", len(nice_cid_list))


def test_get_code():
    test_do = Download_Optimization()
    test_output = "test_do"
    with open(test_output, 'w') as f:
        f.write(dbutil.get_company_code(test_do.db, 261))


def test():
    test_do = Download_Optimization()
    test_output = "test_nice_download_output"
    with open(test_output, 'w') as f:
        # 40 游戏
        for cid, score in test_do.get_nice_download_cids(tids=[40]):
            f.write(dbutil.get_company_code(test_do.db, cid))
            f.write(' ')
            f.write(str(round(score, 4)))
            f.write('\n')


def main():
    do = Download_Optimization()
    for cid, score in do.get_nice_download_cids():
        # 566646 下载优秀
        logger_apkdownload.info("insert into company_tag_rel: companyid %s, tagid 566646", cid)
        dbutil.update_company_tag(do.db, cid, 566646, round(score, 4), "Y")
    do.db.close()


if __name__ == "__main__":
    main()

