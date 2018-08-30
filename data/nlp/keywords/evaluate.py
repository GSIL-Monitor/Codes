# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil
from newkey import KeywordExtractor

import codecs
from copy import copy

mapping = {line.split('\t')[0]: line.split('\t')[1].strip()
           for line in codecs.open('files/qmp.sector', encoding='utf-8')}


def dump():

    global mapping
    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    ke = KeywordExtractor()
    raw = mongo.raw.qmp.find({"url": "http://vip.api.qimingpian.com/d/c3", "processed": True},
                             {'postdata': 1, 'data.basic': 1})
    results = {}
    fo = codecs.open('dumps/20180726', 'w', 'utf-8')
    for qmp in raw:
        basic = qmp.get('data', {}).get('basic')
        tags = []
        tags.append(basic.get('hangye1', ''))
        tags.append(basic.get('hangye2', ''))
        tags.extend(basic.get('tags_match', '').split('|'))
        tags = [tag for tag in tags if tag.strip()]
        sc = db.get('select companyId from source_company where source=13121 and sourceId=%s;', qmp['postdata']['id'])
        tag_qmp = set(tags) & set(mapping.keys())
        if not tag_qmp:
            continue
        if not (sc and sc.companyId):
            continue
        orignal = copy(tag_qmp)
        tag_qmp = [mapping.get(tag) for tag in tag_qmp]
        tag_xiniu = [dbutil.get_tag_name(db, tid) for tid in ke.extract_vip(sc.companyId).keys()]
        url = 'http://www.xiniudata.com/company/%s/overview' % dbutil.get_company_code(db, sc.companyId)
        desc = db.get('select brief from company where id=%s;', sc.companyId).brief
        desc = desc.replace('\n', '') if desc else ''
        if set(tag_qmp) & set(tag_xiniu):
            # results[1] = results.get(1, 0) + 1
            fo.write('%s\t%s\t1\t%s\t%s\n' % (','.join(orignal), ','.join(tag_xiniu), url, desc))
        else:
            fo.write('%s\t%s\t0\t%s\t%s\n' % (','.join(orignal), ','.join(tag_xiniu), url, desc))
            # results[0] = results.get(0, 0) + 1
    for k, v in results.items():
        print k, v


if __name__ == '__main__':

    print __file__
    dump()
