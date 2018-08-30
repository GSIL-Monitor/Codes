# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from basic_track import CompanyTracker
from common import dbutil

from datetime import datetime, timedelta


class AndroidUpdateCompanyTracker(CompanyTracker):

    """
    update every day
        check whether there is big version update of android app
    """

    def __init__(self):

        CompanyTracker.__init__(self)

    def feed(self, cid, today=None):

        today = datetime.today() if not today else today
        for apk in dbutil.get_artifact_from_cid(self.db, cid, 4050):
            if apk.domain and self.__feeda(apk.domain, today):
                self.mongo.track.track.insert({
                    'topic': 4,
                    'companyId': cid,
                    'abstract': u'%s旗下Android产品有大的版本更新' % dbutil.get_company_name(self.db, cid),
                    'createTime': today
                })

    def __feeda(self, apkname, today):

        results = self.mongo.market.android.find({'updateDate': {'$gt': (today - timedelta(hours=24)), '$lte': today},
                                                  'apkname': apkname, 'histories': {'$ne': None}})
        for result in results:
            new_version = int(result.get('version', '').split('.')[0] or -1)
            old_version = max([
                int(history.get('version', '').split('.')[0] or -1) for history in result.get('history', [])
            ])
            if new_version and old_version and new_version > old_version:
                return new_version
        return False


def c4_2(today=None):

    aut = AndroidUpdateCompanyTracker()
    db = dbcon.connect_torndb()
    for cid in iter(dbutil.get_all_company_id(db)):
        aut.feed(cid, today)
    db.close()


if __name__ == '__main__':

    if sys.argv[1] == 'c4.2':
        c4_2()