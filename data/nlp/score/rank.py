# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil
from completeness import ScorerCompleteness

import codecs
from math import log10


def score():

    db = dbcon.connect_torndb()
    with codecs.open('dumps/rank', 'w', 'utf-8') as fo:
        for tag in [u'大数据', u'小程序', u'短视频', u'民宿', u'足球', u'咖啡']:
            cids = []
            tid = dbutil.get_tag_id(db, tag)[0]
            complete = db.query('select rel.companyId cid from company_tag_rel rel, company_scores s '
                                'where (rel.active="Y" or rel.active is null) and rel.companyId=s.companyId '
                                'and s.type=37010 and tagId=%s order by score desc limit 100;', tid)
            cids.extend([c.cid for c in complete])
            yellows = db.query('select companyId cid, count(*) c from company_tag_rel rel, tag '
                               'where tag.id=tagId and tag.type=11100 and (tag.active is null or tag.active="Y") '
                               'and (rel.active="Y" or rel.active is null) and companyId in '
                               '(select distinct companyId from company_tag_rel where tagId=%s '
                               'and (active is null or active="Y")) group by companyId order by c desc limit 100;', tid)
            cids.extend([c.cid for c in yellows])
            msgs = db.query('select msg.companyId cid, count(*) c from company_message msg, company_tag_rel rel '
                            'where msg.active="Y" and msg.companyId=rel.companyId and msg.publishTime>"2018-02-01" '
                            'and rel.tagId=%s and (rel.active="Y" or rel.active is null) group by msg.companyId '
                            'order by c desc limit 100;', tid)
            cids.extend([c.cid for c in msgs])
            cids = set(cids)
            for cid in cids:
                name = dbutil.get_company_name(db, cid)
                brief = dbutil.get_company_brief(db, cid)
                url = 'http://www.xiniudata.com/#/company/%s/overview' % dbutil.get_company_code(db, cid)
                s1 = dbutil.get_company_score(db, cid, 37010)
                s1 = 1 if s1 >= 0.5 else s1
                s2 = (len(dbutil.get_company_tags_yellow(db, cid, False)) + 1 - dbutil.get_company_yellow_time_deduction(db, cid)) / 9
                s3 = (log10(len(dbutil.get_company_messages(db, cid, 'Y', '2018-02-01')) + 1)) / 4
                s4 = db.get('select confidence from company_tag_rel where companyId=%s and tagId=%s;', cid, tid).confidence
                fo.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (tag, name, brief, url, s1, round(s2, 2), round(s3, 2), round(s4, 2)))


if __name__ == '__main__':

    print __file__
    score()
