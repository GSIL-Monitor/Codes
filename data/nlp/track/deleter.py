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
from bson.objectid import ObjectId


def delete_old():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()

    # tms = [t.id for t in db.query('select * from topic_message where topicid=9 and id>=23697 and active="P";')]
    # tms = [t.id for t in db.query('select * from topic_message where topicid=10 and id>20198 and active="P";')]
    # tms = [t.id for t in db.query('select * from topic_message where topicid in (40, 41, 51) and relateType=60;')]
    # mongo.message.user_message.remove({'topicMessageId': {'$in': tms}})
    # db.execute('delete from topic_message_sector_rel where topicMessageId in %s;', tms)
    # db.execute('delete from topic_message_company_rel where topicMessageId in %s;', tms)
    # db.execute('delete from topic_tab_message_rel where topicMessageId in %s;', tms)
    # db.execute('delete from topic_message where id in %s;', tms)

    cms = [c.id for c in db.query('select id from company_message where trackdimension=3108 '
                                  'and createTime>"2017-11-18";')]
    mongo.message.user_message.remove({'companyMessageId': {'$in': cms}})
    db.execute('delete from company_message where id in %s;', cms)

    # tcs = [t.id for t in db.query('select * from topic_company where active="P" and topicid=57 and id>0;')]
    # print len(tcs)
    # db.execute('delete from topic_tab_company_rel where topicCompanyId in %s;', tcs)
    # db.execute('delete from topic_message_company_rel where topicCompanyId in %s;', tcs)
    # db.execute('delete from topic_company_sector_rel where topicCompanyId in %s;', tcs)
    # db.execute('delete from topic_company where id in %s;', tcs)

    # for tpc in db.query('select * from topic_company where topicid=52;'):
    #     tpmc = db.query('select * from topic_message_company_rel where topicCompanyId=%s order by createTime;', tpc.id)
    #     if len(tpmc) == 1:
    #         db.execute('update topic_message set detailId=%s where id=%s;', tpc.companyId, tpmc[0].topicMessageId)
    #     if len(tpmc) < 2:
    #         continue
    #     else:
    #         delete = [item.topicMessageId for item in tpmc][1:]
    #         mongo.message.user_message.remove({'topicMessageId': {'$in': delete}})
    #         db.execute('delete from topic_message_sector_rel where topicMessageId in %s;', delete)
    #         db.execute('delete from topic_message_company_rel where topicMessageId in %s;', delete)
    #         db.execute('delete from topic_tab_message_rel where topicMessageId in %s;', delete)
    #         db.execute('delete from topic_message where id in %s;', delete)


def makeup_code():

    db = dbcon.connect_torndb()
    with codecs.open('files/big', encoding='utf-8') as f:
        for line in f:
            sname, code = line.strip().split('\t')
            print sname
            sid = db.get('select id from sector where sectorname=%s and active="Y";', sname).id
            cid = db.get('select id from company where code=%s', code).id
            db.execute('insert into hot_company (sectorId, companyId, createTime, active) '
                       'values (%s, %s, now(), "Y");', sid, cid)


def reverse():

    db = dbcon.connect_torndb()
    tcs = [tc.id for tc in db.query('select * from topic_company where topicId in (44) and active="Y";')]
    for tmcr in db.query('select * from topic_message_company_rel where topicCompanyId in %s;', tcs):
        print tmcr
        db.execute('update topic_message set active="Y" where id=%s;', tmcr.topicMessageId)


def delete_sourcing():

    db = dbcon.connect_torndb()
    for c in db.query('select * from company_extract_source where createtime>"2017-07-07" and type=67003;'):
        if db.get('select count(*) c from company_extract_source '
                  'where createtime>"2017-07-07" and companyId=%s;', c.companyId) > 1:
            continue
        db.execute('delete from sourcing_company where companyId=%s and createTime>"2017-07-07";', c.companyId)
        db.execute('delete from sourcing_company_user_rel where companyId=%s and createTime>"2017-07-07"', c.companyId)
    db.execute('delete from company_extract_source where createtime>"2017-07-07" and type=67003')


def makeup_intro():

    db = dbcon.connect_torndb()
    for line in codecs.open('files/introduction', encoding='utf-8'):
        s, code = line.strip().split('\t')
        sid = db.get('select id from sector where sectorName=%s and active="Y";', s).id
        cid = db.get('select id from company where code=%s;', code).id
        if db.get('select count(*) c from hot_company where sectorId=%s and companyId=%s;', sid, cid).c > 0:
            db.execute('update hot_company set active="Y" where sectorId=%s and companyId=%s;', sid, cid)
        else:
            db.execute('insert into hot_company (sectorId, companyId, createUser, createTime, verify, active) '
                       'values (%s, %s, 215, now(), "Y", "Y")', sid, cid)


def correct_comps_weight():

    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    for tpc in dbutil.get_topic_companies(db, 57):
        candidates = mongo.comps.candidates.find_one({'company': tpc.companyId}).get('candidates')
        for candidate in candidates:
            if len(candidate) < 2:
                print tpc.companyId, candidate


def rm_dup_industry_company():

    db = dbcon.connect_torndb()
    for ic in db.query('select industryId, companyId, count(*) c from industry_company '
                       'group by industryId, companyId having c>1;'):
        db.execute('delete from industry_company where active="N" and companyId=%s and industryId=%s;',
                   ic.companyId, ic.industryId)
    db.close()


def rm_dup_company_tag():

    db = dbcon.connect_torndb()
    for ct in db.query('select companyId, tagId, count(*) c from company_tag_rel '
                       'group by companyId, tagId having c>1;'):
        for index, ctr in enumerate(db.query('select id from company_tag_rel where companyId=%s and tagId=%s;',
                                             ct.companyId, ct.tagId)):
            if index > 0:
                db.execute('delete from company_tag_rel where id=%s;', ctr.id)
    db.close()


if __name__ == '__main__':

    print __file__
    # makeup_intro()
    # delete_sourcing()
    # reverse()
    # makeup_code()
    # delete_old()
    # correct_comps_weight()
    # rm_dup_industry_company()
    # rm_dup_company_tag()
