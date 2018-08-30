# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')


import codecs

import db as dbcon
from common import dbutil, dicts


def cmp_fi():

    fio = dicts.get_known_angels()
    db = dbcon.connect_torndb()
    fin = dbutil.get_famous_investors(db)
    diff = [i for i in fio if i not in fin]
    for i in diff:
        investor = dbutil.get_investor_info(db, i)
        if investor.active is None or investor.active == 'Y':
            print i, investor.name


def dump_tags():

    db = dbcon.connect_torndb()
    # with codecs.open('files/tag.dump', 'w', 'utf-8') as fo:
    #     vips = [(t.id, t.name) for t in dbutil.get_tags_by_type(db, [11012])]
    #     for vipid, name in vips:
    #         for sub in db.query('select tag2Id from tags_rel where tagId=%s and type=54040;', vipid):
    #             fo.write('%s\t%s\n' % (name, dbutil.get_tag_info(db, sub.tag2Id, 'name')))
    with codecs.open('files/tag.dump', 'w', 'utf-8') as fo:
        for t in dbutil.get_tags_by_type(db, [11010]):
            fo.write('%s\n' % t.name.strip())
    db.close()


def statistic():

    path = u'/Users/eastdog/Documents/work/xiniu/机构/statistic'
    count = {}
    data = {}
    alli = set()
    for line in codecs.open(path, encoding='utf-8'):
        if line.strip():
            org, gs = line.strip().split('\t')
            if org.strip() and org != u'1':
                current = org
                alli.add(org)
            if gs == u'2':
                continue
            count.setdefault(gs, []).append(current)
            data.setdefault(current, set()).add(gs)
    # for g, c in sorted(count.items(), key=lambda x: len(set(x[1])), reverse=True):
    #     print g, '\t', len(c), len(set(c))
    for x in [y for y in alli if y not in data]:
        print x
    for iv, gss in data.items():
        for g in gss:
            print iv, '\t', g

if __name__ == '__main__':

    print __file__
    statistic()
    # dump_tags()
    # cmp_fi()
