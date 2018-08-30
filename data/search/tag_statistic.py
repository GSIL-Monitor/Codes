# coding=utf-8
__author__ = 'wangqc'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import db as dbcon
import config
from client import SearchClient
from nlp.common import dbutil
from search.universal.universal_client import UniversalSearchClient


import time
import logging
import pandas as pd


# logging
logging.basicConfig(level=logging.INFO, format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
logger_ts = logging.getLogger('tag statistic')

def test():
    db = dbcon.connect_torndb()
    client = UniversalSearchClient()

    tier1 = [s.id for s in dbutil.get_sectored_tags(db, 1)]
    tier2 = [s.id for s in dbutil.get_sectored_tags(db, 2)]
    tier3 = [s.id for s in dbutil.get_sectored_tags(db, 3)]

    result = {}
    result['t1'] = {tag: [client.search('general', input='', filter={'tag': [dbutil.get_tag_name(db, tag)]}).get('company').get('count')] for tag in tier1}
    result['t2'] = {tag: [client.search('general', input='', filter={'tag': [dbutil.get_tag_name(db, tag)]}).get('company').get('count')] for tag in tier2}
    result['t3'] = {tag: [client.search('general', input='', filter={'tag': [dbutil.get_tag_name(db, tag)]}).get('company').get('count')] for tag in tier3}
    for tag in result['t1']:
        result['t1'][tag].append(get_company_from_tag(db, tag))
    for tag in result['t2']:
        result['t2'][tag].append(get_company_from_tag(db, tag))
    for tag in result['t3']:
        result['t3'][tag].append(get_company_from_tag(db, tag))
    return result


def get_company_from_tag(db, tid):
    results = db.get('select count(distinct companyId) as count from company_tag_rel ct join company c on ct.companyId = c.id'
                       ' where tagId=%s and (ct.active is null or ct.active!="N") and (c.active is null or c.active="Y");', tid)
    return int(results.count)


if __name__ == '__main__':
    db = dbcon.connect_torndb()
    raw = test()
    data = [[k, dbutil.get_tag_name(db, vk), raw[k][vk][0], raw[k][vk][1], raw[k][vk][1] - raw[k][vk][0]]
              for k in sorted(raw.keys()) for vk in sorted(raw[k].keys())]
    df = pd.DataFrame(data=data, columns=['tier', 'tag', 'secnt', 'dbcnt', 'gap'])
    df.to_csv('logs/tag_stat.csv', encoding='utf_8_sig')