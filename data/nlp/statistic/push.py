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
from datetime import datetime


def yellow(today=None):

    log_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], '../recommend/logs/push.task.log')
    today = datetime.today() if not today else today
    today = today.strftime('%d %b %Y')
    db = dbcon.connect_torndb()

    with codecs.open(log_path, encoding='utf-8') as f:
        pushed = []
        for line in f:
            if 'pushed #' not in line:
                continue
            if today in line:
                cids = [int(item.strip()) for item in line.split('# ')[-1].split(',')]
                yellows = [dbutil.exist_yellow_tags(db, cid) for cid in cids]
                pushed.append(yellows.count(True) > 0)
    db.close()

    return len(pushed), pushed.count(True)


def convertion(oid=1):

    db = dbcon.connect_torndb()
    deals = db.query('select distinct deal.id as did, deal.companyId from deal, deal_user_rel where dealId=deal.id and '
                     'deal.organizationId=%s and deal_user_rel.type=23030 and deal.status>19000;', oid)
    for deal in deals:
        if db.get('select type from deal_user_rel where dealId=%s '
                  'order by createTime limit 1;', deal.did).type == 23030:
            dbutil.update_collection(db, 612, deal.companyId)
    # dbutil.update_collection_user(db, 612, 19)
    db.close()


if __name__ == '__main__':

    if sys.argv[1] == 'yellow':
        if len(sys.argv) == 2:
            print yellow()
        else:
            today = datetime(int(sys.argv[2][:4]), int(sys.argv[2][4:6]), int(sys.argv[2][6:]))
            print yellow(today)
    elif sys.argv[1] == 'convertion':
        convertion()