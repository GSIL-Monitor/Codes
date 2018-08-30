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
from copy import copy
from bson import ObjectId


def get_shareholder():

    mongo = dbcon.connect_mongo()
    majias = [line.strip() for line in codecs.open('files/yuanma', encoding='utf-8')]
    with codecs.open('files/yuanma.lp', 'w', 'utf-8') as fo:
        for majia in majias:
            try:
                investors = mongo.info.gongshang.find_one({'name': majia}).get('investors', [])
                investors = [investor.get('name') for investor in investors if investor.get('name') not in majias]
                fo.write('%s\t%s\n' % (majia, ','.join(investors)))
            except Exception, e:
                print majia


def reshape_majia():

    fo = codecs.open('files/yuanma.reshape', 'w', 'utf-8')
    for line in codecs.open('files/yuanma.lp', encoding='utf-8'):
        data = line.strip().split('\t')
        if len(data) == 0 or len(data) == 1:
            fo.write(line)
        else:
            lps = data[1].split(',')
            fo.write('%s\t%s\n' % (data[0], lps[0]))
            for lp in lps[1:]:
                fo.write('\t%s\n' % lp)


def analyze_yuanhe():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    investors = {name: iid for iid, name in
                 dbutil.get_investor_alias_with_ids(db, *[x[0] for x in dbutil.get_all_investor(db)])}
    candidates = {name: iid for iid, name in dbutil.get_investor_alias_candidates(db, *dbutil.get_online_investors(db))}
    # majias = [alias.name for alias in db.query('select * from fof_alias;')]
    # majias.extend(dbutil.get_investor_alias(db, 348))
    # majias = set(majias)
    # majias2 = set(copy(majias))
    with codecs.open('files/yuanhe', 'w', 'utf-8') as fo:
        # for majia in majias:
        #     print majia
        #     gongshang = mongo.info.gongshang.find_one({'name': majia})
        #     if not gongshang:
        #         continue
        #     invests = [g.get('name') for g in gongshang.get('invests', [])]
        #     invests = [i for i in invests if u'投资' in i or u'股权' in i or u'创业' in i]
        #     for index, investor in enumerate(invests):
        #         iid = investors.get(investor)
        #         iidc = candidates.get(investor)
        #         if iid == 348 or iidc == 348:
        #             majias2.add(investor)
        #             continue
        # majias = dbutil.get_investor_alias(db, 348)
        have = [line.strip() for line in codecs.open('files/yuanhe.have')]
        # majias2 = [m for m in majias if m not in have]
        # allm = set(majias) | set(have)
        for majia in have:
            print majia
            gongshang = mongo.info.gongshang.find_one({'name': majia})
            if not gongshang:
                print 'no gongshang', majia
                continue
            invests = [g.get('name') for g in gongshang.get('invests', []) if g.get('name') not in have]
            if not invests:
                fo.write('%s\t\t\n' % majia)
            # invests = [i for i in invests if u'投资' in i or u'股权' in i or u'创业' in i]
            for index, investor in enumerate(invests):
                iid = investors.get(investor)
                iidc = candidates.get(investor)
                if iid:
                    iname = dbutil.get_investor_name(db, iid)
                elif iidc:
                    iname = '%s(待确认)' % dbutil.get_investor_name(db, iidc)
                else:
                    iname = ''
                majia_name = majia if index == 0 else ''
                fo.write('%s\t%s\t%s\n' % (majia_name, investor, iname))


def check_lp():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()

    for (iid, alias) in dbutil.get_investor_alias_with_ids(db, *dbutil.get_online_investors(db)):
        try:
            gs = mongo.info.gongshang.find_one({'name': alias})
            lps = [lp.get('name') for lp in gs.get('investors', [])]
            lps = [lp for lp in lps if u'宜信' in lp]
            if len(lps) > 0:
                print dbutil.get_investor_name(db, iid), alias, lps[0]
        except Exception, e:
            pass
            # print 'fail', alias
    gs = mongo.info.gongshang.find_one({'name': '宜信惠民投资管理（北京）有限公司'})
    for ptfl in gs.get('invests', []):
        alias = db.get('select * from investor_alias where name=%s;', ptfl.get('name'))
        if alias:
            print ptfl.get('name')


def link_july():

    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    shall = {}
    fo = codecs.open('dumps/june.out', 'w', 'utf-8')
    for (iid, name) in dbutil.get_investor_gongshang_with_ids(db, *dbutil.get_online_investors(db)):
        shall[name] = ','.join(('investor', name, str(iid), dbutil.get_investor_name(db, iid)))
        igs = mongo.info.gongshang.find_one({'name': name})
        if igs:
            for sh in igs.get('investors', []):
                if sh.get('name'):
                    shall[sh.get('name')] = ','.join(('sh', name, str(iid), dbutil.get_investor_name(db, iid)))
    print len(shall)
    shall_keys = set(shall.keys())
    for line in codecs.open('files/funded.july', encoding='utf-8'):
        name, establish, founded = line.strip().split('\t')
        amac = mongo.amac.fund.find_one({'fundName': name})
        if founded == u'是':
            fo.write(u'%s\t%s\t%s\t关联到机构\n' % (name, establish, amac.get('regDate')))
            continue
        gs = mongo.info.gongshang.find_one({'name': name})
        if not gs:
            if u'私募' in name:
                fo.write(u'%s\t%s\t%s\t私募\n' % (name, establish, amac.get('regDate')))
                continue
            else:
                l1 = name.strip().replace(u'(', u'（').replace(u')', u'）')
                l2 = name.strip().replace(u'（', u'(').replace(u'）', u')')
                gs = mongo.info.gongshang.find_one({'name': l1}) or mongo.info.gongshang.find_one({'name': l2})
                if not gs:
                    fo.write(u'%s\t%s\t%s\t无工商\n' % (name, establish, amac.get('regDate')))
                    continue
        share_holders = set(filter(lambda x: x.strip(), [sh.get('name', '') for sh in gs.get('investors', [])]))
        shared = share_holders & shall_keys
        if shared:
            fo.write(u'%s\t%s\t%s\t潜在新机构\n' % (name, establish, amac.get('regDate')))
        else:
            fo.write(u'%s\t%s\t%s\t无结果\n' % (name, establish, amac.get('regDate')))


def organize_july():

    db = dbcon.connect_torndb()
    for line in codecs.open('files/funded.july.2org', encoding='utf-8'):
        investor = db.get('select * from investor where name=%s order by online desc limit 1;', line.split('\t')[0])
        if not investor.locationId:
            domestic = -1
        elif investor.locationId < 371:
            domestic = 1
        else:
            domestic = 0
        print line.strip(), '\t', investor.online, '\t', domestic


def get_gongshang_establish():

    mongo = dbcon.connect_mongo()
    fo = codecs.open('dumps/20180720', 'w', 'utf-8')
    for line in codecs.open('files/20180720', encoding='utf-8'):
        gs = mongo.info.gongshang.find_one({'name': line.strip()})
        if not gs:
            l1 = line.strip().replace(u'(', u'（').replace(u')', u'）')
            l2 = line.strip().replace(u'（', u'(').replace(u'）', u')')
            gs = mongo.info.gongshang.find_one({'name': l1}) or mongo.info.gongshang.find_one({'name': l2})
        if gs:
            fo.write('%s\n' % (gs.get('establishTime', '')))
        else:
            fo.write('\n')


if __name__ == '__main__':

    print __file__
    get_gongshang_establish()
    # organize_july()
    # link_july()
    # check_lp()
    # analyze_yuanhe()
    # reshape_majia()
    # get_shareholder()
