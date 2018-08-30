# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil

import codecs
from itertools import chain


def dump_share_holders():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    # investors = set(dbutil.get_online_investors(db)) & set(dbutil.get_famous_investors(db))
    investors = set([i.id for i in db.query('select distinct investorId id from famous_investor '
                                            'where (active is null or active="Y") and createUser in (-1, -2);')])
    investors = set(dbutil.get_online_investors(db)) & investors
    investors = {iid: [i[1] for i in dbutil.get_investor_gongshang_with_ids(db, iid)] for iid in investors}
    with codecs.open('dumps/famous.sh', 'w', 'utf-8') as fo:
        for iid, imajias in investors.iteritems():
            iname = dbutil.get_investor_name(db, iid)
            for majia in imajias:
                try:
                    gs = mongo.info.gongshang.find_one({'name': majia})
                    if not gs:
                        continue
                    share_holers = gs.get('investors', [])
                    share_holers = [i.get('name') for i in share_holers if i.get('name') not in imajias]
                    share_holers = [i for i in share_holers if len(i) > 5]
                    if not share_holers:
                        fo.write('%s\t%s\n' % (iname, majia))
                    else:
                        for sh in share_holers:
                            fo.write('%s\t%s\t%s\n' % (iname, majia, sh))
                except Exception, e:
                    print majia, e

if __name__ == '__main__':

    print __file__
    dump_share_holders()