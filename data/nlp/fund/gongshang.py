# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
import loghelper
from common import dbutil

from datetime import datetime, timedelta
from bson.objectid import ObjectId

loghelper.init_logger("gsf", stream=True)
logger_gsf = loghelper.get_logger('gsf')


class GongshangFundEvent(object):

    def __init__(self, check_period=1):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.check_period = check_period

    def generate_gs_fund_event(self):

        global logger_gsf
        yesterday = datetime.now() - timedelta(days=self.check_period)
        logger_gsf.info('Gongshang Fund starts')
        for tpm in dbutil.get_topic_messages(self.db, 44, yesterday):
            logger_gsf.info('Processing %s' % tpm.id)
            change_date = tpm.get('comments')
            # update funding
            cids = self.mongo.article.news.find_one({'_id': ObjectId(tpm.relateId)}).get('companyIds', [])
            for cid in cids:
                cprtid = dbutil.get_company_corporate_id(self.db, cid)
                dbutil.update_gongshang_funding(self.db, cid, cprtid, change_date)
            # generate task news
            self.mongo.task.news.update({'news_id': tpm.relateId},
                                        {'news_id': tpm.relateId, 'news_date': datetime.now(), 'type': 'fund',
                                         'createTime': datetime.utcnow(), 'processStatus': int(0),
                                         'source': 'gongshang', 'companyIds': cids}, True)


if __name__ == '__main__':

    gsfe = GongshangFundEvent()
    gsfe.generate_gs_fund_event()
