# coding=utf-8
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


loghelper.init_logger('General Tag')
logger_gt = loghelper.get_logger('General Tag')


class GeneralTagger(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()

    def label(self, cid):

        dbutil.clear_company_tag(self.db, cid, 579089)
        general_tags = []
        for tag in self.__extract_11120(cid):
            dbutil.update_company_tag(self.db, cid, tag, 0, active='H')
            general_tags.append(tag)
        if 589015 in general_tags:
            dbutil.update_company_tag_comment(self.db, cid, 589015, 80, dbutil.get_company_latest_fa(self.db, cid))
        return general_tags

    def label_full(self):

        global logger_gt
        for cid in self.db.query('select distinct id from company where active="Y" or active is null;'):
            logger_gt.info('Processing, %s' % cid)
            self.label(cid.id)

    def __extract_11120(self, cid):

        # 早期公司，小于等于B轮，成立时间在2010年之后
        if 0 <= dbutil.get_company_round(self.db, cid) <= 1040 \
                and dbutil.get_company_establish_date(self.db, cid).year >= 2010:
            yield 579089
        # 公司状态，融资中 等
        status = dbutil.get_company_status(self.db, cid)
        if status in (2010, 2020, 2025):
            yield {
                2010: 589014,
                2015: 589015,
                2020: 589016,
                2025: 589017
            }[status]


if __name__ == '__main__':

    gt = GeneralTagger()
    gt.label_full()
