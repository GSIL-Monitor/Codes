# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import dicts

import time
import json
import codecs
from random import randint
from datetime import date
from datetime import datetime, timedelta
from math import log10
from copy import copy
from itertools import chain


def get_tag_id(db, name, important=False):

    """
    type of returned id is long
    :return: tag id and active,
    active=Y, active=N, active=D for delete
    """
    name = name.strip()
    result = db.get('select * from tag where name=%s', name)
    if result:
        if result.type == 11001:
            return False, 'D'
        if result.type == 11002 or result.type == 11000:
            return result.id, 'N'
        return result.id, 'Y'
    else:
        if important:
            db.execute('insert into tag (name, type, createTime, modifyTime, createUser, novelty) '
                       'values (%s, 11000, now(), now(), 139, 4);', name)
            return db.get('select id from tag where name=%s', name).id, 'Y'
        else:
            db.execute('insert into tag (name, type, createTime, modifyTime, createUser, novelty) '
                       'values (%s, 11002, now(), now(), 139, 4);', name)
            return db.get('select id from tag where name=%s', name).id, 'N'


def filter_sector_tags(db, names):

    if not names:
        return []
    return [t.id for t in db.query('select id from tag where name in %s and sectorType=1 order by novelty desc;', names)]


def analyze_source_tag(db, name, replacement):

    names = name.replace(u'；', ',').replace(u'，', ',').replace(';', ',').split(',')
    replaced_names = []
    for name in names:
        if replacement.get(name):
            replaced_names.extend(replacement.get(name))
        else:
            replaced_names.append(name)
    tags = []
    for tname in replaced_names:
        if len(tname) < 2:
            continue
        # tag = db.get('select * from tag where name=%s;', tname)
        # if tag and tag.type == 11003:
        #     tags.extend([item.tag2Id for item in db.query('select * from tags_rel where tagId=%s', tag.id)])
        # else:
        tid, active = get_tag_id(db, tname, important=True)
        if active == 'D':
            continue
        tags.append(tname)
    return tags


def get_tag_info(db, tid, column=None):

    if not column:
        return db.get('select * from tag where id=%s;', tid)
    else:
        info = db.get('select * from tag where id=%s and (active is null or active="Y");', tid)
        return info[column] if info else None


def get_tag_name(db, tid):

    tag_name = db.get('select name from tag where id=%s;', tid)
    return tag_name.name if tag_name else tag_name


def get_tags_by_type(db, typeset='default'):

    if typeset == 'default':
        typeset = (11010, 11011, 11012, 11013)
    return db.query('select * from tag where type in %s order by type desc', typeset)


def get_searchable_tags(db):

    return [t.name for t in db.query('select * from tag where (type in (11011, 11012, 11013) '
                                     'or (type >= 11050 and type<=11100)) and (active is null or active="Y");')]


def get_tags_by_relation(db, tid, relation):

    return [t.tag2Id for t in db.query('select * from tags_rel where tagId=%s and type=%s order by type desc;',
                                       tid, relation)]


def get_hyponym_tags(db, tid, level=1):

    if level == 1:
        tags = get_tags_by_relation(db, tid, 54041)
        tags.extend([t.tag2Id for t in db.query('select * from tags_rel where tagId in %s and type=54041;', tags)])
        return list(set(tags))
    if level == 2:
        return get_tags_by_relation(db, tid, 54041)


def get_hypernym_tags(db, tid, target=0):

    tags = [t.tagId for t in db.query('select * from tags_rel where tag2Id=%s and type=54041;', tid)]
    if tags:
        tags.extend([t.tagId for t in db.query('select * from tags_rel where tag2Id in %s and type=54041;', tags)])
    if target == 0:
        return list(set(tags))
    else:
        return list(set([t.id for t in db.query('select * from tag where id in %s and sectorType=%s;', tags, target)]))


def analyze_tags_relations(db, tids, relation):

    return db.query('select * from tags_rel where tagId in %s and tag2Id in %s and type=%s;', tids, tids, relation)


def exist_tag(db, tname, general=False):

    if not general:
        return db.get('select count(*) as count from tag where name=%s and type>11003;', tname).count > 0
    return db.get('select count(*) as count from tag where name=%s;', tname).count > 0


def exist_company_tag(db, cid, tid):

    return db.get('select count(*) as count from company_tag_rel where companyId=%s and tagId=%s and '
                  '(active is null or active!="N");', cid, tid).count > 0


def get_company_id(db, name):

    result = db.query('select id from company where name=%s;', str(name))
    if result:
        return [x.id for x in result]


def get_artifact_website(db, aid):

    return db.get('select link from artifact where id=%s', aid).link


def get_android_summary(db, cid, sid, source, aspect='download'):

    result = db.get('select * from summary_android where companyId=%s and sector=%s and source=%s;', cid, sid, source)
    if not result:
        return None
    if aspect == 'download':
        return result.downloadRank
    if aspect == 'growth':
        return result.growthRank


def update_android_summary(db, cid, sid, source, rank, aspect='download'):

    """
    :return: whether this record is updated
    """
    old = db.get('select count(*) as count from summary_android where companyId=%s and sector=%s and source=%s;',
                 cid, sid, source).count
    if old == 0:
        if aspect == 'download':
            db.execute('insert into summary_android '
                       '(companyId, sector, source, downloadRank, createTime, modifyTime) '
                       'values (%s, %s, %s, %s, now(), now())', cid, sid, source, rank)
        elif aspect == 'growth':
            db.execute('insert into summary_android '
                       '(companyId, sector, source, growthRank, createTime, modifyTime) '
                       'values (%s, %s, %s, %s, now(), now())', cid, sid, source, rank)
        return False
    oldrank = get_android_summary(db, cid, sid, source, aspect)
    if oldrank and oldrank == rank:
        db.execute('update summary_android set modifyTime=now() where companyId=%s and sector=%s and source=%s;',
                   cid, sid, source)
        return False
    if aspect == 'download':
        if not oldrank:
            db.execute('update summary_android set modifyTime=now(), downloadRank=%s '
                       'where companyId=%s and sector=%s and source=%s;', cid, sid, source)
            return False
    elif aspect == 'growth':
        if not oldrank:
            db.execute('update summary_android set modifyTime=now(), growthRank=%s '
                       'where companyId=%s and sector=%s and source=%s;', cid, sid, source)
            return False
    return tuple([oldrank, rank])


def get_company_info(db, cid):

    return db.get('select * from company where id=%s', cid)


def get_company_name(db, cid):

    return db.get('select name from company where id=%s', cid).name


def get_company_digital_coin_info(db, cid):

    return db.get('select * from digital_token where companyId=%s limit 1;', cid)


def get_company_investors(db, cid):

    return [i.iid for i in db.query('select investor.id iid from investor, company, funding, funding_investor_rel '
                                    'where company.id=%s and company.corporateId=funding.corporateId and '
                                    'funding.id=funding_investor_rel.fundingId '
                                    'and funding_investor_rel.investorId=investor.id '
                                    'and (company.active="Y" or company.active is null) and '
                                    '(funding.active="Y" or funding.active is null) and '
                                    '(funding_investor_rel.active="Y" or funding_investor_rel.active is null) and'
                                    '(investor.active="Y" or investor.active is null)', cid)]


def get_company_investor_names(db, cid):

    iids = get_company_investors(db, cid)
    if not iids:
        return []
    names = [i.name for i in db.query('select name from investor_alias where (active is null or active="Y") '
                                      'and investorId in %s', iids)]
    names.extend([i.name for i in db.query('select name from investor where (active is null or active="Y") '
                                           'and id in %s', iids)])
    names.extend([name.replace(u'基金', '').replace(u'投资', '').replace(u'资本', '').replace(u'创投', '')
                  for name in names])
    return list(set(names))


def get_company_funding(db, cid, period=None):

    copid = get_company_corporate_id(db, cid)
    if not period:
        return db.query('select * from funding where corporateId=%s and (active is null or active="Y");', copid)
    return db.query('select * from funding where corporateId=%s and (active is null or active="Y") and '
                    'createTime>%s and createTime<%s;', copid, period[0], period[1])


def update_gongshang_funding(db, cid, cprid, change_date):

    if db.get('select count(*) c from funding where companyId=%s and gsChangeDate>=%s', cid, change_date).c > 0:
        return
    db.execute('insert into funding (source, companyId, corporateId, createTime, fundingDate, active, gsChangeDate) '
               'values (69002, %s, %s, now(), %s, "P", %s)', cid, cprid, change_date, change_date)


def get_corporate_latest_funding(db, copid, period=None):

    if not period:
        resutls = db.query('select * from funding where corporateId=%s and (active is null or active="Y") '
                           'order by fundingDate desc;', copid)
    else:
        resutls = db.query('select * from funding where corporateId=%s and (active is null or active="Y") and '
                           'createTime>%s and createTime<%s order by fundingDate desc;', copid, period[0], period[1])
    if resutls and len(resutls) > 0:
        return resutls[0]


def get_funding_by_date(db, period=None):

    if period:
        return db.query('select * from funding where (active is null or active="Y") and '
                        'fundingDate>%s and fundingDate<%s;', period[0], period[1])
    return db.query('select * from funding where (active is null or active="Y");')


def get_itered_funding(db):

    return db.iter('select id from funding;')


def get_makeup_funding(db, limit=500):

    return db.query('select * from funding order by id desc limit %s;', limit)


def get_funding(db, fid):

    return db.get('select * from funding where id=%s;', fid)


def get_funding_index_type(db, fid):

    return db.get('select count(*) c from funding f, corporate cp, company c where c.corporateId=cp.id '
                  'and f.corporateId=cp.id and (f.active is null or f.active="Y") and f.id=%s '
                  'and (c.active="Y" or c.active is null) and (cp.active="Y" or cp.active is null);', fid).c > 0


def get_untracked_fundings(db):

    return db.query('select * from funding where (active is null or active="Y") and tracked is null;')


def get_all_FA(db, start=None, end=None):

    if not start:
        return db.query('select * from company_fa where (active is null or active="Y");')
    if not end:
        end = datetime.now()
    return db.query('select * from company_fa where (active is null or active="Y") '
                    'and modifyTime>%s and modifyTime<%s;', start, end)


def get_all_fund_raising(db):

    return [c.id for c in db.query('select * from company where (active is null or active="Y") '
                                   'and companyStatus=2015 order by createTime;')]


def random_company_id(db, notequal=None):

    if not notequal:
        return db.get('select id from company order by rand() limit 1;').id
    for _ in xrange(20):
        cid = db.get('select id from company order by rand() limit 1;').id
        if not cid == notequal:
            return cid
    return cid


def random_company_ids(db, out_list, size=100):

    return [rel.cid for rel in db.query('select companyId cid from company_tag_rel '
                                        'where companyId not in %s and (active="Y" or active is null) and verify="Y" '
                                        'and createTime>"2017-10-01" order by rand() limit %s;', out_list, size)]


def get_company_gongshang_name(db, cid, with_verify=False):

    alias = db.query('select corporate_alias.name name, corporate_alias.verify verify from corporate_alias, company '
                     'where company.id=%s and company.corporateId=corporate_alias.corporateId and '
                     '(corporate_alias.active is null or corporate_alias.active="Y");', cid)
    if with_verify:
        if len(alias) == 1:
            return [(name.name, True) for name in alias]
        return [(name.name, True if (name.verify and name.verify == "Y") else False) for name in alias]
    else:
        return [name.name for name in alias]


def get_cid_from_gongshang(db, gname):

    return [c.id for c in db.query('select distinct company.id id from corporate_alias, company '
                                   'where corporate_alias.name=%s and '
                                   '(corporate_alias.active is null or corporate_alias.active="Y") and '
                                   'company.corporateId=corporate_alias.corporateId and '
                                   '(company.active is null or company.active!="N");', gname)]


def get_company_corporate_name(db, cid, short=True):

    corporate = db.get('select corporate.name as name, corporate.fullName as full from corporate, company '
                       'where company.id=%s and corporateId=corporate.id;', cid)
    if corporate:
        return corporate.name if short else corporate.full
    return None


def get_company_corporate_id(db, cid):

    return db.get('select corporateId from company where id=%s;', cid).corporateId


def get_corporate_alias(db, cid):

    corporates = db.query('select corporate_alias.name as name from corporate_alias, company '
                          'where company.id=%s and company.corporateId=corporate_alias.corporateId and '
                          '(corporate_alias.active is null or corporate_alias.active="Y");', cid)
    return [alias.name for alias in corporates]


def get_company_context(db, cid):

    """
    get all text relevant to a company, texts are weighted
    :param db:
    :param cid:
    :return: a suite of (weight, content, tags)
    """
    for item in db.query('select source, description, tags from source_company where companyId=%s', cid):
        tags = item.get('tags').split(',') if item.get('tags') else []
        yield __get_text_weight(item.get('source')), item.get('description'), tags


def get_source_company_tags(db, cid, source=None):

    if source:
        results = db.query('select tags from source_company where companyId=%s and (active is null or active="Y") and '
                           'source in %s and (aggregateVerify is null or aggregateVerify="Y");', cid, source)
    else:
        results = db.query('select tags from source_company where companyId=%s and (active is null or active="Y") '
                           'and (aggregateVerify is null or aggregateVerify="Y");', cid)

    if results:
        return [result.tags for result in results]
    else:
        return []


def get_company_index_type(db, cid):

    result = db.get('select active from company where id=%s', cid)
    if result.active is None or result.active == 'Y':
        return True
    return False


def get_nonactive_company(db):

    return [item.id for item in db.query('select id from company where active="N" or type=41020;')]


def get_nocomps_company(db, limit=500):

    return [item.id for item in db.query('select id from company where type!=41020 and (active is null or active="Y") '
                                         'and  not exists (select * from companies_rel where companyId=company.id) '
                                         'order by id desc;')][:limit]


def get_company_relevant_context(db, cid):

    contents = db.query('select source_context.content as content from source_context, source_company '
                        'where source_company.companyId=%s and source_context.sourceCompanyId=source_company.id '
                        'and source_context.type!=30010;', cid)
    contents = '\n'.join([content.content for content in contents])
    if len(contents.strip()) < 10:
        brief = db.get('select brief from company where id=%s', cid).brief
        description = db.get('select description from company where id=%s', cid).description
        if brief:
            contents = '%s\n%s' % (contents, brief)
        if description:
            contents = '%s\n%s' % (contents, description)
    return contents


def get_source_company_description_from_cid(db, cid):

    for item in db.query('select id, description from source_company where companyId=%s and description!="" '
                         'and (active is null or active="Y");', cid):
        yield item.id, item.description


def get_source_company_description(db, scid):

    item = db.get('select id, description from source_company where id=%s;', scid)
    return item.id, item.description


def get_company_brief(db, cid):

    brief = db.get('select id, brief from company where id=%s and brief!="";', cid)
    return brief.brief if brief else ''


def get_source_company_brief(db, scid):

    item = db.get('select id, brief from source_company where id=%s;', scid)
    return item.id, item.brief


def get_source_company_brief_from_cid(db, cid):

    for item in db.query('select id, brief from source_company where companyId=%s and brief!="" '
                         'and (active is null or active="Y");', cid):
        yield item.id, item.brief


def get_currency_rate(db, currency):

    rate = db.get('select rate from exchange_rate where currency=%s;', currency)
    return rate.rate if rate else 1


def get_source_company_productDesc(db, scid):

    item = db.get('select id, productDesc from source_company where id=%s', scid)
    return item.id, item.productDesc if item else None, None


def get_tags_rel(db, tid1, tid2=None, type=54020):

    if not tid2:
        return db.query('select * from tags_rel where tagId=%s and type=%s;', tid1, type)
    else:
        results = db.query('select * from tags_rel where tagId=%s and tag2Id=%s;', tid1, tid2)
        if len(results) == 0:
            return []
        return [(result.type, result.confidence) for result in results]


def get_tag_novelty(db, tag, name=False):

    if name:
        return db.get('select novelty from tag where name=%s;', tag).novelty
    else:
        return db.get('select novelty from tag where id=%s', tag).novelty


def get_company_tags_info(db, cid, typelist=None):

    if not typelist:
        typelist = [11010, 11011, 11012, 11013, 11014]
    results = db.query('select rel.tagId tid, rel.confidence conf, rel.verify verify, tag.sectorType sector, '
                       'tag.novelty novelty, tag.type type, tag.name name from company_tag_rel rel, tag '
                       'where rel.companyId=%s and rel.tagId=tag.id and rel.active="Y" and tag.type in %s '
                       'order by rel.confidence desc;', cid, typelist)
    return results


def get_company_tags_idname(db, cid, active='Y', tag_out_type='default'):

    if tag_out_type == 'default':
        tag_out_type = (11000, 11001, 11002, 11100)
    yellows = get_yellow_tags(db)
    results = db.query('select company_tag_rel.tagId as tid, company_tag_rel.confidence as weight, '
                       'tag.id, tag.name as tname '
                       'from company_tag_rel, tag '
                       'where company_tag_rel.companyId=%s and company_tag_rel.tagId=tag.id '
                       'and (company_tag_rel.active=%s or company_tag_rel.active is null) '
                       'and (tag.type not in %s or tag.type is null);',
                       cid, active, tag_out_type)
    if results and 11100 in tag_out_type:
        return map(lambda x: (x.tid, x.tname, x.weight), [y for y in results if y.tid not in yellows])
    elif results:
        return map(lambda x: (x.tid, x.tname, x.weight), [y for y in results])
    return []


def get_companies_sector_tag(db, cids, sector_types='default', order='default'):

    if sector_types == 'default':
        sector_types = [1, 2, 3]
    if order == 'novelty':
        return [r.tid for r in db.query('select distinct t.id tid from tag t, company_tag_rel rel use index (companyId) '
                                        'where (rel.active is null or rel.active="Y") and companyId in %s '
                                        'and rel.tagId=t.id and t.sectorType in %s order by t.novelty desc;',
                                        cids, sector_types)]
    return [r.tid for r in db.query('select distinct t.id tid from tag t, company_tag_rel rel use index (companyId) '
                                    'where (rel.active is null or rel.active="Y") and companyId in %s '
                                    'and rel.tagId=t.id and t.sectorType in %s order by rel.confidence desc;',
                                    cids, sector_types)]


def get_company_sector_tag(db, cid, sector_types='default'):

    if sector_types == 'default':
        sector_types = [1]
    return [r.tid for r in db.query('select distinct t.id tid from tag t, company_tag_rel rel use index (companyId) '
                                    'where (rel.active is null or rel.active="Y") and companyId=%s '
                                    'and rel.tagId=t.id and t.sectorType in %s order by rel.confidence desc;',
                                    cid, sector_types)]


def prompt_tag_filter(db, comps, size=3):

    if not comps:
        return []
    tids = db.query('select tagId, tag.name name, count(*) c from company_tag_rel rel, tag '
                    'where tagId=tag.id and tag.type in (11011, 11012, 11013) and companyId in %s '
                    'and (rel.active is null or rel.active="Y") group by tagId order by c desc limit %s', comps, size)
    return [t.name for t in tids]


def get_company_tags_comment(db, cid, tids):

    results = db.query('select comment from company_tag_rel where comment is not null and companyId=%s and '
                       '(active is null or active!="N") and tagId in %s;', cid, tids)
    if results and len(results) > 0:
        return json.loads(list(results)[0].comment)


def get_company_tags_old(db, cid):

    results = db.query('select company_tag_rel.tagId from company_tag_rel, tag where companyId=%s and tagId=tag.id and '
                       'tag.type<11110 and (company_tag_rel.verify is null or company_tag_rel.verify="N");', cid)
    return [result.tagId for result in results]


def get_company_tags_verified(db, cid):

    results = db.query('select tag.name name from company_tag_rel, tag where companyId=%s and tagId=tag.id and '
                       'tag.type<11110 and (company_tag_rel.verify is null or company_tag_rel.verify="Y") and '
                       '(company_tag_rel.active is null or company_tag_rel.active="Y");', cid)
    return [result.name for result in results]


def get_company_topics_tags(db, cid):

    results = db.query('select distinct tag.name name from tag, topic_tag_rel rel, topic_company tc '
                       'where rel.tagId=tag.id and tc.companyId=%s and tc.topicId=rel.topicId and rel.active="Y" '
                       'and tc.active="Y";', cid)
    return [result.name for result in results]


def get_company_topics(db, cid):

    return db.query('select * from topic_company where companyId=%s and (active is null or active="Y");', cid)


def get_company_tags_deleted(db, cid):

    results = db.query('select tag.name name from company_tag_rel, tag where companyId=%s and tagId=tag.id and '
                       'company_tag_rel.active="N" and company_tag_rel.verify="Y";', cid)
    return [result.name for result in results]


def get_company_tags_yellow(db, cid, name=True):

    results = db.query('select tag.id as tid, tag.name as name from tag, company_tag_rel where companyId=%s and '
                       'tag.id=tagId and (company_tag_rel.active="Y" or company_tag_rel.active is null) '
                       'and tag.type=11100;', cid)
    if name:
        return [item.name for item in results]
    else:
        return [item.tid for item in results]


def get_company_yellow_time_deduction(db, cid):

    tag = db.get('select company_tag_rel.createTime from company_tag_rel, tag where tag.type=11100 and tag.id=tagId '
                 'and (company_tag_rel.active="Y" or company_tag_rel.active is null) and companyId=%s '
                 'order by createTime desc limit 1;', cid)
    if tag:
        return min(round(1-(datetime.now() - tag.createTime).days/10000.0, 4), 0.99)
    return 1


def get_company_round(db, cid):

    cround = db.get('select corporate.round as round from corporate, company '
                    'where company.id=%s and corporateId=corporate.id;', cid)
    return cround.round if (cround and cround.round) else 0


def get_round_sort(db, round):

    if round:
        value = db.get('select * from dictionary where typevalue=1 and value=%s;', round)
        return value.sort if value else None
    return None


def get_company_active(db, cid):

    active = db.get('select active from company where id=%s;', cid)
    if active and active.active is None:
        return 'Y'
    if active and active.active:
        return active.active


def get_company_verify(db, cid):

    verify = db.get('select verify from company where id=%s;', cid)
    if verify and verify.verify == 'Y':
        return 'Y'
    else:
        return 'N'


def get_company_verified(db, cid):

    return db.get('select verify from company where id=%s;', cid).verify is not None


def get_corporate_verified(db, cid):

    return db.get('select corporate.verify verify from company, corporate where company.id=%s '
                  'and company.corporateId=corporate.id;', cid).verify is not None


def get_company_alias_verified(db, cid):

    return db.get('select count(*) c from company_alias where companyId=%s and (active is null or active="Y") '
                  'and verify is null', cid).c == 0


def get_corporate_alias_verified(db, cid):

    return db.get('select count(*) c from corporate_alias, company '
                  'where company.id=%s and (corporate_alias.active is null or corporate_alias.active="Y") '
                  'and corporate_alias.verify is null and company.corporateId=corporate_alias.corporateId', cid).c == 0


def get_funding_verified(db, cid):

    return db.get('select count(*) c from funding, company where (funding.active is null or funding.active="Y") and '
                  'funding.corporateId=company.corporateId and funding.verify is null and company.id=%s;', cid).c == 0


def get_artifact_verified(db, cid):

    return db.get('select count(*) c from artifact where companyId=%s and (active is null or active="Y") '
                  'and verify is null', cid).c == 0


def get_member_verified(db, cid):

    return db.get('select count(*) c from company_member_rel, member where companyId=%s and memberId=member.id '
                  'and member.verify is null and (member.active is null or member.active="Y") and '
                  '(company_member_rel.active is null or company_member_rel.active="Y") and '
                  '(type = 0 or type = 5010 or type = 5020)', cid).c == 0


def get_recruit_verified(db, cid):

    return db.get('select count(*) c from company_recruitment_rel where companyId=%s '
                  'and (active is null or active="Y") and verify is null', cid).c == 0


def get_company_establish_date(db, cid):

    edate = db.get('select cp.establishDate establishDate from company c, corporate cp where c.id=%s '
                   'and c.corporateId=cp.id;', cid)
    return edate.establishDate.date() if edate.establishDate else date(1993, 4, 30)


def get_company_create_date(db, cid):

    cdate = db.get('select createTime from company where id=%s', cid)
    return cdate.createTime if cdate.createTime else datetime(1993, 4, 30, 0, 0, 0)


def get_company_latest_fa_date(db, cid):

    fadate = db.get('select publishDate from company_fa where companyId=%s order by publishDate desc limit 1', cid)
    return fadate.publishDate if (fadate and fadate.publishDate) else datetime(1993, 4, 30, 0, 0, 0)


def get_company_latest_fa(db, cid, start=None):

    if not start:
        fa = db.get('select * from company_fa where companyId=%s and (active="Y" or active is null) '
                    'order by publishDate desc limit 1', cid)
    else:
        fa = db.get('select * from company_fa where companyId=%s and (active="Y" or active is null) and publishDate>%s '
                    'order by publishDate desc limit 1', cid, start)
    return fa.id if (fa and fa.id) else None


def get_company_latest_artifact_date(db, cid, verify=True):

    if verify:
        adate = db.get('select releaseDate from artifact where companyId=%s and (active is null or active="Y") '
                       'and verify is not null '
                       'order by releaseDate desc limit 1;', cid)
    else:
        adate = db.get('select releaseDate from artifact where companyId=%s and (active is null or active="Y") '
                       'order by releaseDate desc limit 1;', cid)
    return adate.releaseDate if (adate and adate.releaseDate) else datetime(1993, 4, 30, 0, 0, 0)


def get_company_tag_recent_update(db, cid, days=1):

    recent = db.get('select modifyTime from company_tag_rel where companyId=%s and (active is null or active="Y") '
                    'order by modifyTime desc limit 1;', cid)
    if recent and recent.modifyTime > (datetime.now() - timedelta(days=days)):
        return True
    return False


def __get_text_weight(key):

    if key in [13020, 13030, 13040]:
        return 1
    elif key in [13010]:
        return 0.8
    else:
        return 0.6


def get_company_source(db, cid, justify=False):

    """
    :param justify: if True, return whether this company is from one or more truested source
    :return:
    """
    # result = db.query('select source from source_company where companyId=%s and (active is null or active="Y");', cid)
    result = db.query('select source from source_company where companyId=%s;', cid)
    if not result:
        return []
    result = set(item.source for item in result)
    if justify:
        if result & set(dicts.get_known_company_source()):
            return True
        return False
    return result


def get_source_company_infos(db, cid):

    return db.query('select * from source_company where companyId=%s and (active is null or active="Y") '
                    'and (aggregateVerify is null or aggregateVerify="Y");', cid)


def get_company_solid_description(db, cid):

    result = db.get('select description from company where id=%s', cid)
    return result.description if result else ''


def get_company_sector(db, cid, level=1, name=False):

    results = db.query('select company_sector.sectorId as sid, sector.sectorName as name from company_sector, sector '
                       'where company_sector.companyId=%s and company_sector.sectorId=sector.id '
                       'and sector.level=%s;', cid, level)
    if not name:
        return [int(result.sid) for result in results] if len(results) > 0 else [999]
    else:
        return [result.name for result in results] if len(results) > 0 else []


def get_sector_tags(db, level=1):

    sectors = {s.id: s.tagId for s in db.query('select id, tagId from sector where level=%s and active="Y";', level)}
    for sid, tid in sectors.items():
        tags = [tid]
        tags.extend([tag.tag2Id for tag in db.query('select tag2Id from tags_rel where tagId=%s and type=54040;', tid)])
        sectors[sid] = tags
    return sectors


def get_sectored_tags(db, sector_type=2):

    return db.query('select * from tag where sectorType=%s;', sector_type)


def get_coldcall_infos(db, ccid):

    processed = db.get('select processed from coldcall where id=%s', ccid)
    if (not processed) or processed.processed == 'Y':
        return
    return db.get('select * from coldcall where id=%s', ccid)


def get_organization_watcher_users(db, oid, purpose='task'):

    """
    return user ids who will receive deal
    """

    if purpose == 'task':
        results = db.query('select distinct userId from user_organization_rel where organizationId=%s '
                           'and (active is null or active="Y");', oid)
    elif purpose == 'coldcall':
        results = db.query('select distinct rel.userId from user_organization_rel rel, user_role '
                           'where rel.organizationId=%s and (rel.active is null or rel.active="Y") '
                           'and user_role.userId=rel.userId and user_role.role=25040;', oid)
    else:
        results = []

    if not results:
        return []
    return map(lambda x: x.userId, results)


def mark_coldcall_processed(db, ccid):

    db.execute('update coldcall set processed="Y" where id=%s', ccid)


def mark_funding_tracked(db, fid):

    db.execute('update funding set tracked="Y" where id=%s;', fid)


def update_recommedation_following_fundings(db):

    for uid in get_all_user(db):
        update_recommedation_following_funding(db, uid)


def update_recommedation_following_funding(db, uid):

    for record in db.query('select id, companyId, createTime from recommendation '
                           'where userId=%s and hasRead="Y";', uid):
        copid = get_company_corporate_id(db, record.companyId)
        latest = get_corporate_latest_funding(db, copid)
        if latest and latest.fundingDate and latest.fundingDate > record.createTime:
            db.execute('update recommendation set hasNewFunding="Y" where id=%s;', record.id)


def get_artifacts_from_iOS(db, iOS_domain):

    # results = db.query('select id from artifact where domain=%s and (active is null or active="Y") '
    #                    'and artifact.type=4040 order by modifyTime desc;', str(iOS_domain))
    results = db.query('select artifact.id as id from company, artifact where artifact.domain=%s and '
                       'artifact.companyId=company.id and (company.active is null or company.active="Y") and'
                       '(artifact.active is null or artifact.active="Y") and artifact.type=4040;', str(iOS_domain))
    return [result.id for result in results]


def get_artifacts_from_apk(db, apkname):

    results = db.query('select artifact.id as id from company, artifact where artifact.domain=%s and '
                       'artifact.companyId=company.id and (company.active is null or company.active="Y") and '
                       '(artifact.active is null or artifact.active="Y") and artifact.type=4050;', str(apkname))
    return [result.id for result in results]


def get_recommend_artifacts_from_domain(db, domain):

    results = db.query('select artifact.id as id from company, artifact where artifact.domain=%s and '
                       'artifact.companyId=company.id and (company.active is null or company.active="Y") and '
                       '(artifact.active is null or artifact.active="Y") and recommend="Y";', str(domain))
    return [result.id for result in results]


def get_artifacts_by_date(db, check_date, artifact_type=(4040, 4050)):

    results = db.query('select artifact.id aid, company.id cid, artifact.type atype, artifact.domain domain '
                       'from artifact, company where artifact.createTime>%s and '
                       '(artifact.active is null or artifact.active="Y") and companyId=company.id and '
                       '(company.active is null or company.active="Y") and artifact.type in %s;',
                       check_date, artifact_type)
    return [(result.aid, result.cid, result.atype, result.domain) for result in results]


def get_artifact_name(db, aid):

    return db.get('select name from artifact where id=%s;', aid).name


def get_artifact_info(db, aid, column):

    return db.get('select * from artifact where id=%s;', aid)[column]


def get_artifact_type(db, aid, string=False):

    atype = db.get('select type from artifact where id=%s;', aid).type
    if string:
        return {
            4010: u'网站',
            4020: u'微信',
            4030: u'微博',
            4040: u'iOS',
            4050: u'Android',
            4060: u'Windows Phone',
            4070: u'PC',
            4080: u'Mac'
        }[atype]
    else:
        return atype


def get_artifact_idname_from_cid(db, cid, strict=False):

    if not strict:
        results = db.query('select id, name from artifact where companyId=%s and name!="" '
                           'and (active="Y" or active is null);', cid)
    else:
        strict_types = [4020, 4030, 4040]
        items = db.query('select id, name, type, rank from artifact where companyId=%s and name!="" '
                         'and (active="Y" or active is null) and type in %s;', cid, strict_types)
        results = []
        for stype in strict_types:
            if stype == 4010:
                results.extend(sorted(filter(lambda y: y.get('type') == stype, items),
                                      key=lambda x: (x.get('rank', 0) or 0))[:1])
            else:
                results.extend(sorted(filter(lambda y: y.get('type') == stype, items),
                                      key=lambda x: -(x.get('rank', 0) or 0))[:1])

    if results:
            return map(lambda x: (x.id, x.name), results)


def get_artifact_idname_from_did(db, did):

    results = db.query('select artifact.id, artifact.name from artifact, deal_artifact_rel where dealId=%s and '
                       'deal_artifact_rel.artifactId=artifact.id and '
                       '(deal_artifact_rel.active="Y" and deal_artifact_rel.active is null)', did)
    if results:
        return map(lambda x: (x.id, x.name), results)


def get_artifact_from_cid(db, cid, type):

    return db.query('select * from artifact where companyId=%s and name!="" '
                    'and (active!="N" or active is null) and type=%s', cid, type)


def get_recommend_artifact(db, cid):

    return db.get('select * from artifact where companyId=%s and recommend="Y" and '
                  '(active!="N" or active is null) limit 1;', cid)


def get_alias_idname(db, cid):

    results = db.query('select id, name from company_alias where companyId=%s and name!="" and '
                       '(active is null or active="Y");', cid)
    if results:
        return map(lambda x: (x.id, x.name), results)


def get_company_code(db, cid):

    return db.get('select code from company where id=%s', cid).code


def get_id_from_code(db, code):

    return db.get('select id from company where code=%s', code).id


def get_id_from_company_message(db, cmid):

    return db.get('select companyId from company_message where id=%s;', cmid).companyId


def get_id_from_name(db, name):

    return [item.id for item in
            db.query('select id from company where name=%s and (active is null or active="Y");', str(name))]


def get_company_location(db, cid, with_sort=False):

    result = db.get('select location.locationId, location.locationName, location.sort '
                    'from location, company, corporate '
                    'where company.id=%s and company.corporateId=corporate.id '
                    'and corporate.locationId=location.locationId;', cid)
    if with_sort:
        return (result.locationId, result.sort) if result else (None, '')
    return (result.locationId, result.locationName) if result else (None, '')


def get_member_idname(db, cid, key=True):

    member_types = (5010, 5020) if key else (5010, 5020, 5030, 5040)
    results = db.query('select member.id as mid, member.name as mname from company_member_rel rel, member '
                       'where rel.companyId=%s and rel.memberId=member.id and member.name!="" and '
                       '(rel.active is null or rel.active="Y") and (member.active is null or member.active="Y") and '
                       'type in %s;', cid, member_types)
    if results:
        return map(lambda x: (x.mid, x.mname), results)
    return []


def get_all_investor(db):

    results = db.query('select id, name from investor where (active is null or active="Y");')
    return map(lambda x: (x.id, x.name), results)


def get_all_investor_withna(db):

    return [i.id for i in db.query('select id from investor;')]


def get_all_investor_info(db, only_active=True):

    if only_active:
        return db.query('select * from investor where (active is null or active="Y");')
    return db.query('select * from investor;')


def get_famous_investors(db):

    return [i.id for i in db.query('select distinct investorId id from famous_investor '
                                   'where (active is null or active="Y");')]


def get_online_investors(db):

    results = db.query('select id, name from investor where (active is null or active="Y") and online="Y";')
    return map(lambda x: x.id, results)


def get_funding_investor_ids(db, fid):

    return [item.id for item in db.query('select investor.id id from investor, funding_investor_rel '
                                         'where fundingId=%s and investorId=investor.id and '
                                         '(funding_investor_rel.active is null or funding_investor_rel.active="Y") '
                                         'and (investor.active is null or investor.active="Y");', fid)]


def get_all_organizations(db):

    return [x.id for x in db.query('select id from organization where type=17020;')]


def get_sourcing_organizations(db):

    return [x.organizationId for x in db.query('select * from org_function_switch where functionValue=68010;')]


def get_organization_sourcing_modules(db, oid):

    return [x.source for x in db.query('select * from org_sourcing_switch where organizationId=%s;', oid)]


def get_all_tag(db, type_filter=None, recent=False):

    if recent:
        type_filter = [11010] if type_filter is None else type_filter
        results = list(db.query('select * from tag where type is null or type in %s '
                                'order by createTime desc limit 500;', type_filter))
        results.extend(db.query('select * from tag where type is null or type in %s '
                                'order by modifyTime desc limit 500;', type_filter))
        return results
    if not type_filter:
        return db.query('select * from tag where (type!=11001 or type is null) and name is not null;')
    return db.query('select * from tag where (type!=11001 or type is null) and name is not null '
                    'and type in %s order by createTime desc;', type_filter)


def get_verified_tags(db, min_count=200):

    return [t.tagId for t in db.query('select tagId, count(*) c from company_tag_rel '
                                      'where (active is null or active="Y") and verify="Y" '
                                      'group by tagId having c>%s order by c desc;', min_count)]


def get_ruled_tags(db):

    return db.query('select * from tag where type>11010 and rule is not null;')


def get_yellow_tags_name():

    return [line.strip() for line in codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                                              'thesaurus/yellow.name'), encoding='utf-8')]


def get_yellow_tags(db):

    return [int(line.strip()) for line in open(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                                            'thesaurus/yellow'))]
    # return [item.id for item in db.query('select id from tag where type=11100;')]


def exist_yellow_tags(db, cid):

    yellows = get_yellow_tags(db)
    return db.get('select count(*) as count from company_tag_rel where (active is null or active="Y") and companyId=%s '
                  'and tagId in %s;', cid, yellows).count > 0


def get_all_locations(db):

    results = db.query('select locationId, locationName from location;')
    return map(lambda x: (x.locationId, x.locationName), results)


def get_location_en_name(db, lid):

    return db.get('select locationEnName from location where locationId=%s;', lid).locationEnName


def get_all_coldcall(db):

    return map(lambda x: x.id, db.query('select distinct id from coldcall where processed="N";'))


def get_cids2shot(db):

    return map(lambda x: x.companyId, db.query('select distinct companyId from artifact where type=4010;'))


def get_all_company_id(db):

    return map(lambda x: x.id, db.query('select distinct id from company where (active="Y" or active is null) '
                                        'order by id desc;'))


def get_all_company_id_withna(db):

    return map(lambda x: x.id, db.query('select distinct id from company where '
                                        '(type is null or type=41010 or type=0) order by id desc;'))


def get_all_company_id_makeups(db):

    return map(lambda x: x.companyId, db.query('select distinct companyId from companies_rel where active="Y" and '
                                               'modifyTime>"2016-11-06" and modifyTime<"2016-11-12";'))


def get_company_ids_by_modify(db, period=2):

    return map(lambda x: x.id, db.query('select distinct id from company where (active="Y" or active is null) and '
                                        '(type is null or type!=41020) and '
                                        'company.modifyTime>date_add(curdate(), interval -%s day)', period))


def get_company_ids_by_create(db, start):

    return map(lambda x: x.id, db.query('select distinct id from company where (type is null or type!=41020) and '
                                        'company.createTime>%s', start))


def get_all_company(db):

    for cid in get_all_company_id(db):

        # contents = db.query('select source_context.content as content from source_company, source_context '
        #                     'where source_company.companyId=%s and source_company.id=source_context.sourceCompanyId '
        #                     'and source_context.type!=30010;',
        #                     cid)
        context = []
        brief = db.get('select brief as content from company where id=%s', cid)
        if brief and brief.content:
            context.append(brief.content)
        description = db.get('select description as content from company where id=%s', cid)
        if description and description.content:
            context.append(description.content)

        cname = db.get('select name from company where id=%s', cid)
        if cname and cname.name:
            context = '\n'.join(context).replace(cname.name, '')

        yield {
            'id': cid,
            'context': context
        }


def get_all_dead_company(db):

    return db.query('select * from company where active="N";')


def get_no_index_company(db):

    return db.query('select * from company where active is not null and active!="Y";')


def get_controlled_company(db):

    pass


def get_all_user(db):

    return [user.id for user in db.query('select distinct id from user where (active is null or active!="D");')]


def get_banned_user(db):

    return set([user.id for user in db.query('select distinct id from user where (active="N" or active="D");')])


def exist_verified_investor(db, uid):

    return db.get('select count(*) c from user where id=%s and verifiedInvestor="Y";', uid).c > 0


def get_company_score(db, cid, type=37010):

    result = db.get('select score from company_scores where companyId=%s and type=%s', cid, type)
    if result and result.score:
        return result.score
    return 0


def get_company_status(db, cid):

    status = db.get('select companyStatus from company where id=%s;', cid)
    return status.companyStatus if status else 0


def get_company_ipo_status(db, cid):

    return len(set(f.round for f in get_company_funding(db, cid)) & {1110}) > 0


def get_company_subscription_count(db, cid):

    return db.get('select count(*) c from user_company_subscription where companyId=%s '
                  'and (active is null or active="Y");', cid).c > 0


def get_company_subscription_details(db, start, end, *cids):

    if not cids:
        return []
    if not start:
        return db.query('select * from user_company_subscription where companyId in %s '
                        'and (active is null or active="Y");', cids)
    return db.query('select * from user_company_subscription where companyId in %s and createTime>%s and createTime<%s '
                    'and (active is null or active="Y");', list(cids), start, end)


def get_all_company_info(db):

    return db.query('select * from company where (active="Y" or active is null);')


def get_similar_companies(db, cid):

    results = db.query('select company2Id from companies_rel where companyId=%s', cid)
    if len(results) == 0:
        return None
    return map(lambda x: x.company2Id, results)


def get_user_favorite(db, uid):

    results = db.query('select companyId from mylist_company_rel, user_mylist_rel '
                       'where user_mylist_rel.userId=%s and user_mylist_rel.mylistId=mylist_company_rel.mylistId and '
                       'mylist_company_rel.createTime>date_add(curdate(), interval -180 day);', uid)
    return [result.companyId for result in results]


def get_user_sectors(db, uid, tid=True):

    if tid:
        return [s.tid for s in db.query('select sector.tagId tid from sector, user_sector where sectorId=sector.id and '
                                        '(user_sector.active is null or user_sector.active="Y") and userId=%s;', uid)]
    return [s.sectorId for s in db.query('select sectorId from user_sector where userId=%s and '
                                         '(active is null or active="Y");', uid)]


def get_user_sanaozi_sectors(db, uid):

    return [conf.tagId for conf in db.query('select distinct tagId from user_saoanzi_sector_conf '
                                            'where userId=%s and active="Y";', uid)]


def get_user_sanaozi_sources(db, uid):

    return [conf.saoanziSourceId for conf in db.query('select distinct saoanziSourceId from user_saoanzi_source_conf '
                                                      'where userId=%s and active="Y";', uid)]


def get_user_profile(db, uid, name=False):

    tids = {}

    # portfolio
    cids = db.query('select deal.companyId as cid from deal, deal_user_rel where deal.status=19050 '
                    'and deal_user_rel.userId=%s and deal_user_rel.dealId=deal.id;', uid)
    if cids:
        for cid in cids:
            for tid, tname, weight in (get_company_tags_idname(db, cid.cid) or []):
                tids[tid] = tids.get(tid, 0) + weight * 0.3

    # sector itself
    sector_extend = dicts.get_sector_extend()
    sector_supports = get_sector_tags(db)
    snames = db.query('select sector.sectorName name, sector.tagId tid, sector.id sid from sector, user_sector '
                      'where sector.id=user_sector.sectorId and user_sector.userId=%s and sector.id!=999 '
                      'and (user_sector.active is null or user_sector.active="Y") and sector.active="Y";', uid)
    for sector in snames:
        tids[sector.tid] = tids.get(sector.tid, 0) + 5
        supports = sector_supports.get(sector.sid)
        if supports:
            for tid in supports[1:]:
                tids[tid] = tids.get(tid, 0) + 1
        for extend in sector_extend.get(sector.name.strip(), []):
            tid, useful = get_tag_id(db, extend)
            if useful == 'Y':
                tids[tid] = tids.get(tid, 0) + 1

    # favorite
    cids = get_user_favorite(db, uid)
    if cids:
        for cid in cids:
            for tid, tname, weight in (get_company_tags_idname(db, cid) or []):
                tids[tid] = tids.get(tid, 0) + (weight or 1)

    # search
    # TODO

    if not name:
        return tids
    else:
        return {
            db.get('select name from tag where id=%s', tid).name.strip(): weight
            for tid, weight in tids.iteritems()
        }


def get_push_pool(db, sids, verify='Y'):

    return [p.companyId for p in db.query('select companyId from push_pool, company '
                                          'where sectorId in %s and push_pool.verify=%s and companyId=company.id;',
                                          sids, verify)]


def get_all_push_pool(db, verify='Y'):

    return [p.companyId for p in db.query('select companyId from push_pool where verify=%s;', verify)]


def get_investor_profile(db, iid, start='1900-01-01', end=None, portfolio_tag=None, ignore_tags=None):

    if not end:
        end = datetime.now().strftime('%Y-%m-%d')
    profile = {}
    companies = get_investor_portfilio(db, iid, (start, end), portfolio_tag)
    if companies:
        companies = sorted(companies, key=lambda x: x.size, reverse=True)
        for index, company in enumerate(companies):
            for tid, tname, weight in (get_company_tags_idname(db, company.cid,
                                                               tag_out_type=(11000, 11001, 11002, 11100, 11054)) or []):
                if ignore_tags and tid in ignore_tags:
                    continue
                profile[tname] = profile.get(tname, 0) + (weight or 0)
    return profile


def update_investor_profile(db, iid, period, profile, tag=None):

    if not tag:
        if db.get('select count(*) c from investor_favorite_field '
                  'where investorId=%s and period=%s;', iid, period).c > 0:
            db.execute('update investor_favorite_field set tags=%s '
                       'where investorId=%s and period=%s;', profile, iid, period)
        else:
            db.execute('insert into investor_favorite_field (investorId, period, tags, active, createTime, modifyTime) '
                       'values (%s, %s, %s, "Y", now(), now())', iid, period, profile)
    else:
        if db.get('select count(*) c from investor_favorite_field '
                  'where investorId=%s and period=%s and tagId=%s;', iid, period, tag).c > 0:
            db.execute('update investor_favorite_field set tags=%s '
                       'where investorId=%s and period=%s and tagId=%s;', profile, iid, period, tag)
        else:
            db.execute('insert into investor_favorite_field '
                       '(investorId, period, tags, active, createTime, modifyTime, tagId) '
                       'values (%s, %s, %s, "Y", now(), now(), %s);', iid, period, profile, tag)


def update_investor_code(db, iid, code):

    if db.get('select code from investor where id=%s;', iid).code:
        return
    else:
        db.execute('update investor set code=%s where id=%s;', code, iid)


def get_investor_tags(db, iid, period):

    tags = db.get('select tags from investor_favorite_field '
                  'where investorId=%s and period=%s and tagId is null;', iid, period)
    return tags.tags if tags else "{}"


def get_investor_portfilio(db, iid, period=None, tag=None):

    if not period:
        return db.query('select company.id as cid, funding.investment size '
                        'from company, funding, funding_investor_rel rel, corporate cp '
                        'where rel.investorId=%s and funding.corporateId = company.corporateId '
                        'and (company.active is null or company.active="Y") '
                        'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                        'and rel.fundingId=funding.id and (funding.active is null or funding.active="Y") '
                        'and (rel.active is null or rel.active="Y");', iid)
    if tag:
        return db.query('select company.id as cid, funding.investment as size '
                        'from company, funding, corporate cp, funding_investor_rel fir, company_tag_rel ctr '
                        'where fir.investorId=%s and company.id=ctr.companyId and ctr.tagId=%s '
                        'and (ctr.active is null or ctr.active="Y") and funding.corporateId = company.corporateId '
                        'and (company.active is null or company.active="Y") and (fir.active is null or fir.active="Y") '
                        'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                        'and funding.fundingDate>=%s and funding.fundingDate<=%s '
                        'and fir.fundingId=funding.id and (funding.active is null or funding.active="Y");',
                        iid, tag, period[0], period[1])
    return db.query('select company.id as cid, funding.investment size '
                    'from company, funding, funding_investor_rel rel, corporate cp '
                    'where rel.investorId=%s and funding.corporateId = company.corporateId '
                    'and (company.active is null or company.active="Y") '
                    'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                    'and rel.fundingId=funding.id and (funding.active is null or funding.active="Y") '
                    'and (rel.active is null or rel.active="Y")'
                    'and funding.fundingDate>=%s and funding.fundingDate<=%s;', iid, period[0], period[1])


def get_investor_name(db, iid):

    return db.get('select name from investor where id=%s;', iid).name


def get_investor_info(db, iid):

    return db.get('select * from investor where id=%s;', iid)


def get_investor_alias(db, *iids):

    return [i.name for i in db.query('select name from investor_alias where (active is null or active="Y") '
                                     'and investorId in %s;', list(iids))]


def get_investor_short_alias(db, *iids):

    return [i.name for i in db.query('select name from investor_alias where (active is null or active="Y") '
                                     'and type=12020 and investorId in %s;', list(iids))]


def locate_investor_alias(db, inames):

    investor = db.get('select distinct investorId from investor_alias '
                      'where (active is null or active="Y") and name in %s limit 1;', inames)
    if investor:
        return investor.investorId
    return


def get_investor_alias_with_ids(db, *iids):

    return [(i.investorId, i.name) for i in db.query('select investorId, name from investor_alias where verify="Y" and '
                                                     '(active is null or active="Y") and investorId in %s;',
                                                     list(iids))]


def get_investor_alias_candidates(db, *iids):

    return [(i.investorId, i.name) for i in db.query('select investorId, name from investor_alias_candidate where '
                                                     'investorId in %s;', list(iids))]


def get_investor_gongshang_with_ids(db, *iids):

    return [(i.investorId, i.name) for i in db.query('select investorId, name from investor_alias where type=12010 and '
                                                     '(active is null or active="Y") and investorId in %s '
                                                     'and verify="Y";', list(iids))]


def get_organization_profile(db, oid, oname=None):

    profile = {}
    if oname and len(db.query('select id from investor where name=%s', oname)) == 1:
        iid = db.get('select id from investor where name=%s', oname).id
        fields = db.get('select field from investor where name=%s', oname).field
        if fields:
            for field in fields.split(','):
                if len(field) > 5:
                    continue
                profile[field] = profile.get('field', 0) + 1
        companies = db.query('select company.id as cid, funding.investment as size '
                             'from company, funding, funding_investor_rel '
                             'where funding_investor_rel.investorId=%s and funding.fundingDate>"2014-06-01" '
                             'and funding.corporateId = company.corporateId '
                             'and (company.active is null or company.active="Y") '
                             'and funding_investor_rel.fundingId=funding.id', iid)
        if companies:
            companies = sorted(companies, key=lambda x: x.size, reverse=True)
            for index, company in enumerate(companies):
                if index < len(companies)/5:
                    profile[db.get('select name from company where id=%s', company.cid).name] = 3
                for tid, tname, weight in (get_company_tags_idname(db, company.cid) or []):
                    profile[tname] = profile.get(tname, 0) + weight
    for uid in get_organization_watcher_users(db, oid):
        for name, weight in get_user_profile(db, uid, True).iteritems():
            profile[name] = profile.get(name, 0) + weight
    return profile


def get_companies_from_investors(db, *iids):

    results = db.query('select company.id as cid from company, funding, funding_investor_rel '
                       'where funding_investor_rel.investorId in %s and funding.id=funding_investor_rel.fundingId '
                       'and funding.corporateId=company.corporateId and (company.active is null or company.active="Y") '
                       'and (funding.active is null or funding.active="Y");', list(iids))
    return [item.cid for item in results]


def get_user_task_volumn(db, uid):

    num = db.get('select recommendNum from user_setting where userId=%s', uid)
    return num.recommendNum if num else 2


def get_company_index(db, cid):

    index = db.get('select android from company_index where companyId=%s', cid)
    if index and index.android:
        return index.android
    return None


def get_artifact_company(db, aid):

    return list(db.query('select companyId from artifact where id=%s;', aid))[0]['companyId']


def get_corporate_companies(db, corid):

    return [item.id for item in db.query('select id from company where corporateId=%s '
                                         'and (active is null or active="Y");', corid)]


def get_company_from_iOS(db, iOS_domain):

    results = db.query('select company.id as cid from company, artifact where artifact.domain=%s and '
                       'artifact.companyId=company.id and (company.active is null or company.active="Y") and'
                       '(artifact.active is null or artifact.active="Y") and artifact.type=4040;', str(iOS_domain))
    if len(results) == 0:
        return None
    return results[0].cid


def get_company_from_tag(db, tid, with_verify=False):

    results = db.query('select distinct companyId, verify, modifyUser from company_tag_rel where tagId=%s '
                       'and (active is null or active!="N");', tid)
    if not with_verify:
        return [result.companyId for result in results]
    return [(result.companyId, result.verify, result.modifyUser) for result in results]


def get_company_from_tags(db, tids):

    # results = db.query('select distinct companyId from company_tag_rel where tagId in %s '
    #                    'and (active is null or active!="N") order by createTime desc;', tids)
    results = db.query('select distinct companyId from company, company_tag_rel where tagId in %s '
                       'and (company_tag_rel.active is null or company_tag_rel.active!="N") '
                       'and (company.active is null or company.active="Y") and company.id=companyId '
                       'order by company.createTime;', tids)
    return [result.companyId for result in results]


def get_company_from_message(db, cmid):

    return db.get('select company.* from company, company_message where companyId=company.id '
                  'and company_message.id=%s;', cmid)


def get_key_terms(db):

    return db.query('select termName, weight from thesaurus where termType in (35010, 35020);')


def get_terms_by(db, *by):

    return db.query('select distinct termName, weight from thesaurus where termType in (%s);',
                    ','.join([str(x) for x in by]))


def get_junk_terms(db):

    return set(map(lambda x: x.termName, db.query('select termName from thesaurus where termType=35001;')))


def get_job_work_year(db):

    return {
        2200: (0, 1),
        2201: (0, 1),
        2202: (0, 1),
        2203: (1, 3),
        2204: (3, 5),
        2205: (5, 10),
        2206: (10, 20)
    }


def get_company_recruitments(db, cid):

    return [item.jobCompanyId for item in db.query('select jobCompanyId from company_recruitment_rel '
                                                   'where companyId=%s and (active is null or active="Y");', cid)]


def get_company_headcount_max(db, cid):

    return db.get('select headCountMax from company where id=%s;', cid).headCountMax


def get_jobs(db, cid, period=None):

    if not period:
        return db.query('select * from job where companyId=%s and (active is null or active="Y");', cid)
    return db.query('select * from job where companyId=%s and (active is null or active="Y") and '
                    'startDate>%s and startDate<%s;', cid, period[0], period[1])


def get_jobs_by_update(db, cid, start, end):

    return db.query('select * from job where companyId=%s and (active is null or active="Y") and '
                    'updateDate>%s and updateDate<%s;', cid, start, end)


def get_job_companies(db):

    results = db.query('select distinct companyId from job;')
    return map(lambda x: x.companyId, results)


def get_sector_id(db, sname, level=1):

    sid = db.get('select id from sector where sectorName=%s and level=%s;', sname, level)
    if sid:
        return sid.id


def get_sector_from_tag(db, tid):

    sid = db.get('select id from sector where tagId=%s and (active="Y" or active is null);', tid)
    if sid and sid.id:
        return sid.id
    return False


def get_tag_from_sector(db, sid):

    return db.get('select tagId from sector where id=%s;', sid).tagId


def get_user_organization(db, uid):

    oid = db.get('select organizationId from user_organization_rel where userId=%s', uid)
    return oid.organizationId if oid else None


def get_top(db):

    return db.query('select id, code from company where (active="Y" or active is null) '
                    'order by createTime desc limit 1000;')


def get_top_yellow(db, month=3):

    return db.query('select company.id as id, company.code as code from company, company_tag_rel, tag '
                    'where company.createTime>date_add(curdate(), interval -%s day) and '
                    '(company.active="Y" or company.active is null) and '
                    '(company.companyStatus is null or company.companyStatus!=2020) and '
                    'company_tag_rel.tagId=tag.id and company_tag_rel.companyId=company.id and tag.type=11100 '
                    'order by company.createTime desc limit 1000;', month*30)


def get_company_count(db):

    return db.get('select count(distinct id) as count from company where (active="Y" or active is null);').count


def update_company_context(db, scid, content, features, confidence=1, type=30000):

    db.execute('insert into source_context (sourceCompanyId, type, content, features, confidence, createTime) '
               'values (%s, %s, %s, %s, %s, now())', scid, type, content, features, confidence)


def update_company_score(db, cid, score, type=37010):

    if db.get('select count(*) as count from company_scores where companyId=%s and type=%s', cid, type).count > 0:
        db.execute('update company_scores set score=%s, modifyTime=now() '
                   'where companyId=%s and type=%s', score, cid, type)
    else:
        db.execute('insert into company_scores (companyId, type, score, createTime, modifyTime) '
                   'values (%s, %s, %s, now(), now());', cid, type, score)


def clear_push_pool(db):

    db.execute('delete from push_pool where companyId>0 and verify!="Y";')


def update_push_pool(db, cid, sid):

    if db.get('select count(*) c from push_pool where companyId=%s and sectorId=%s;', cid, sid).c == 0:
        db.execute('insert into push_pool (companyId, sectorId, createTime) values (%s, %s, now())', cid, sid)


def update_coldcall_user(db, ccid, uid, uidentify):

    if db.get('select count(*) as count from coldcall_user_rel where coldcallId=%s and userIdentify=21020',
              ccid).count > 0:
        return
    db.execute('insert into coldcall_user_rel (coldcallId, userId, userIdentify, createTime, modifyTime) '
               'values (%s, %s, %s, now(), now())', ccid, uid, uidentify)
    db.execute('insert into coldcall_forward (coldcallId, toUserId, createTime) '
               'values (%s, %s, now());', ccid, uid)
    # db.execute('update coldcall set assignee=%s where id=%s;', uid, ccid)


def update_investor_outstanding_companies(db, iid, cids, type):

    if not cids:
        return
    db.execute('delete from investor_company_rel where investorId=%s and type=%s', iid, type)
    for index, cid in enumerate(cids):
        db.execute('insert into investor_company_rel (investorId, companyId, type, sort, createTime) '
                   'values (%s, %s, %s, %s, now());', iid, cid, type, len(cids)-index)


def update_investor_chart(db, iid, type, file):

    if len(db.query('select * from investor_chart where investorId=%s and type=%s', iid, type)) > 0:
        db.execute('update investor_chart set file=%s, modifyTime=now() '
                   'where investorId=%s and type=%s;', file, iid, type)
    else:
        db.execute('insert into investor_chart (investorId, type, file, createTime, modifyTime) '
                   'values (%s, %s, %s, now(), now());', iid, type, file)


def clear_yellow_label(db):

    # yellow = dbutil.get_yellow_tags(db)
    yellow = [309126, 309127, 309128, 309129]
    clear_label(db, *yellow)
    db.execute('update artifact set androidExplosion = "N" where androidExplosion="Y" and id>0;')


def clear_label(db, *tids):

    tids = list(tids)
    db.execute('delete from company_tag_rel where tagId in %s and (verify is null or verify="N");', tids)
    db.execute('delete from company_tag_rel where tagId in %s and createUser=139 and modifyUser is null;', tids)


def clear_company_tag(db, cid, tid):

    db.execute('delete from company_tag_rel where companyId=%s and tagId=%s', cid, tid)


def clear_tag(db, tid, strict=False):

    if not strict:
        db.execute('update company_tag_rel set active="N" where (verify is null or verify!="Y") and tagId=%s;', tid)
    else:
        db.execute('update company_tag_rel set active="N", modifyUser=139 where tagId=%s;', tid)


def clear_company_common_tag(db, tid, check_point):

    db.execute('update company_tag_rel set active="N" where verify="P" and tagId=%s '
               'and modifyTime<%s;', tid, check_point)


def update_company_tag(db, cid, tid, weight, verify="N", active="Y"):

    if active == 'D':
        return False

    existed = db.get('select * from company_tag_rel where companyId=%s and tagId=%s;', cid, tid)
    if existed:
        # verified vip tag
        if (existed.verify and existed.verify == "Y") and existed.confidence >= 3:
            return False
        # sb. deleted
        if (existed.verify and existed.verify == "Y") and (existed.active and existed.active == "N"):
            return False
        # sb. verified
        elif (existed.verify and existed.verify == "Y") and (existed.active is None or existed.active == "Y"):
            db.execute('update company_tag_rel set confidence=%s where companyId=%s and tagId=%s;', weight, cid, tid)
            return False
        # m.daniel thought this was NOT a proper tag
        elif (existed.verify is None or existed.verify != "Y") and (existed.active and existed.active == "N"):
            db.execute('update company_tag_rel set confidence=%s, verify=%s, active=%s, modifyTime=now() '
                       'where companyId=%s and tagId=%s;', weight, verify, active, cid, tid)
            return True
        # was a tag
        elif (existed.verify is None or existed.verify != "Y") and (existed.active and existed.active == "Y"):
            db.execute('update company_tag_rel set confidence=%s, verify=%s, active=%s, modifyTime=now() '
                       'where companyId=%s and tagId=%s;', weight, verify, active, cid, tid)
            return True
        # update a hidden tag
        elif existed.active and existed.active == "H":
            db.execute('update company_tag_rel set confidence=%s, verify=%s, active=%s, modifyTime=now() '
                       'where companyId=%s and tagId=%s;', weight, verify, active, cid, tid)
            return True
    else:
        db.execute('insert into company_tag_rel (companyId, tagId, confidence, active, '
                   'createTime, modifyTime, createUser) '
                   'values (%s, %s, %s, %s, now(), now(), 139);', int(cid), int(tid), weight, active)
        return True


def update_company_tag_comment(db, cid, tid, relate_type, relate_id, detail_id=None):

    # message and comments
    comments = ''
    if tid == 309126:
        msg = u'%s旗下产品%s近期下载量激增' % (get_company_name(db, cid), get_artifact_name(db, relate_id))
        comments = {
            16010: '360',
            16020: 'baidu',
            16030: 'wandoujia',
            16040: 'myapp'
        }.get(detail_id, '')
    elif tid == 579409:
        msg = u'%s旗下一款iOS应用进入总榜前50名' % get_company_name(db, cid)
        comments = get_artifact_name(db, relate_id)
    elif tid == 579410:
        msg = u'%s旗下一款iOS应用进入分榜前50名' % get_company_name(db, cid)
        comments = get_artifact_name(db, relate_id)
    elif tid == 589015:
        msg = u'%s, %s开启了新一轮融资' % (get_company_brief(db, cid), get_company_name(db, cid))
    else:
        msg = u'发现了新的公司'
    # update
    if detail_id:
        comment = json.dumps({'message': msg, 'relate_type': relate_type, 'relate_id': relate_id,
                              'detail_id': detail_id, 'comments': comments})
    else:
        comment = json.dumps({'message': msg, 'relate_type': relate_type, 'relate_id': relate_id})
    db.execute('update company_tag_rel set comment=%s, modifyTime=now() '
               'where companyId=%s and tagId=%s;', comment, cid, tid)


def update_tags_rel(db, id1, id2, weight=1, trtype=54020):

    if id1 == id2:
        return
    if len(db.query('select * from tags_rel '
                    'where tagId=%s and tag2Id=%s and type=%s;', int(id1), int(id2), trtype)) == 0:
        db.execute('insert into tags_rel (tagId, tag2Id, confidence, type, createTime, modifyTime) '
                   'values (%s, %s, %s, %s, now(), now())', int(id1), int(id2), round(weight, 4), trtype)
    else:
        db.execute('update tags_rel set confidence=%s, modifyTime=now() '
                   'where type=%s and tagId=%s and tag2Id=%s', round(weight, 4), trtype, int(id1), int(id2))


def update_tag_weight(db, tag):

    term_weight = db.get('select weight from thesaurus where termName=%s;', tag.strip())
    term_weight = term_weight.weight if term_weight else 0
    print term_weight, tag
    db.execute('update tag set weight=%s, modifyTime=now() where name=%s;', term_weight, tag.strip())


def update_tag_type(db, tag, ttype, verify='Y', with_tag_id=False):

    tid = get_tag_id(db, tag)[0] if not with_tag_id else tag
    db.execute('update tag set type=%s, verify=%s, modifyTime=now() where id=%s;', ttype, verify, tid)


def get_company_comps(db, cid):

    return [comps.cid for comps in db.query('select company2Id cid from companies_rel where companyId=%s '
                                            'and (active="Y" or active is null) order by distance desc;', cid)]


def get_comps_update_need(db, cid):

    # if sb has modified comps of a company within one month, no need to modify
    return db.get('select count(*) c from companies_rel where companyId=%s and modifyUser is not null '
                  'and modifyUser!=139 and modifyTime>date_add(curdate(), interval - 30 day);', cid).c == 0


def get_filtered_company_comps(db, cid, tid):

    return [comps.cid for comps in db.query('select company2Id cid from companies_rel cr, company_tag_rel ctr '
                                            'where cr.companyId=%s and (cr.active="Y" or cr.active is null) and '
                                            'company2Id=ctr.companyId and tagId=%s order by distance desc;', cid, tid)]


def update_company_rels(db, cid, updates, rm_old=True, need_feedback=False, feedback_threshold=0):

    """
    update company-company relations with updates for company cid
    :param db:
    :param cid:
    :param updates: list of (relevant_company_id, weight) tuples
    :return:
    """
    if not updates:
        return
    new_companies = set()
    insertsql, updatesql = [], []
    for cid2, weight in updates:
        if cid2 in new_companies:
            continue
        new_companies.add(cid2)
        if cid2 == cid:
            continue
        if len(db.query('select * from companies_rel where companyId=%s and company2Id=%s;', int(cid), int(cid2))) == 0:
            insertsql.append((int(cid), int(cid2), weight))
        else:
            updatesql.append((weight, int(cid), int(cid2)))
    db.executemany('insert into companies_rel (companyId, company2Id, distance, active, createTime, modifyTime) '
                   'values (%s, %s, %s, "Y", now(), now())', insertsql)
    db.executemany('update companies_rel set distance=%s, modifyTime=now() '
                   'where companyId=%s and company2Id=%s and (verify is null or verify="N");', updatesql)

    original_companies = map(lambda x: x.company2Id,
                             db.query('select company2Id from companies_rel where companyId=%s', cid))
    if rm_old:
        dead_companies = [c for c in original_companies if c not in new_companies]
        for c in dead_companies:
            db.execute('delete from companies_rel where companyId=%s and company2Id=%s '
                       'and (verify!="Y" or verify is null);', int(cid), int(c))
    if need_feedback:
        return [item[1] for item in insertsql if item[2] > feedback_threshold]


def update_source_android(db, aid, source, download, growth):

    if db.get('select count(*) as count from source_summary_android '
              'where artifactId=%s and source=%s;', aid, source).count > 0:
        db.execute('update source_summary_android set download=%s, growth=%s, modifyTime=now() '
                   'where artifactId=%s and source=%s;', download, growth, aid, source)
    else:
        db.execute('insert into source_summary_android (artifactId, source, download, growth, createTime, modifyTime) '
                   'values (%s, %s, %s, %s, now(), now())', aid, source, download, growth)


def get_android_explosion(db):

    results = db.query('select * from ('
                       'select distinct c.id cid, a.id aid, source_summary_android.source source '
                       'from artifact a, company c, source_summary_android '
                       'where source_summary_android.artifactId=a.id and a.companyId=c.id and '
                       '(a.active is null or a.active="Y") and (c.active is null or c.active="Y") and '
                       'source_summary_android.modifyTime > date_add(now(), interval -7 day) and '
                       'source_summary_android.download > 1000 and growth > 10 order by cid, growth desc)t '
                       'group by cid;')
    return [(int(row.cid), int(row.aid), 10.0001, int(row.source)) for row in results]


def get_fast_iter_artifact(db):

    last_month = datetime.now() - timedelta(days=30)
    results = db.query('select cm.companyId, 1.0*count(distinct cm.id)/(count(distinct a.id)+1) c '
                       'from company_message cm, artifact a where a.companyId=cm.companyId and '
                       'trackdimension in (2001, 2002, 2003) and cm.createTime>%s and cm.active!="N" '
                       'and (a.active is null or a.active="Y") and a.type in (4040, 4050) '
                       'group by cm.companyId having c>=3;', last_month)
    return [(row.companyId, row.c) for row in results]


def get_recommendation_waste(db, uid):

    return db.get('select count(*) as c from recommendation where userId=%s and hasRead="N";', uid).c


def update_recommendation(db, uid, cid, confidence=0.95, update_read='N'):

    if db.get('select count(*) as c from recommendation where userId=%s and companyId=%s;', uid, cid).c > 0:
        db.execute('update recommendation set confidence=%s, hasRead=%s where userId=%s and companyId=%s;',
                   confidence, update_read, uid, cid)
    else:
        db.execute('insert into recommendation (userId, companyId, confidence, createTime, hasRead) '
                   'values (%s, %s, %s, now(), "N");', uid, cid, confidence)


def could_recommend(db, uid, cid):

    # shut down
    status = db.get('select companyStatus from company where id=%s;', cid)
    if status and status.companyStatus in (2020, 2025):
        return False
    # has been recommended before
    # if db.get('select count(*) as c from recommendation where userId=%s and companyId=%s;', uid, cid).c > 0:
    #     return False
    # has been rejected
    if db.get('select count(*) c from recommendation where userId=%s and companyId=%s and reject="Y";', uid, cid).c > 0:
        return False
    # is following
    if db.get('select count(*) c from user_company_subscription where userId=%s and companyId=%s;', uid, cid).c > 0:
        return False
    # in a list
    if db.get('select count(*) as c from mylist_company_rel, user_mylist_rel where user_mylist_rel.userId=%s and '
              'user_mylist_rel.mylistId=mylist_company_rel.mylistId '
              'and mylist_company_rel.companyId=%s;', uid, cid).c > 0:
        return False
    # organization's deal
    if db.get('select count(*) as c from user_organization_rel, deal where deal.companyId=%s and '
              'user_organization_rel.userId=%s '
              'and deal.organizationId=user_organization_rel.organizationId;', cid, uid).c > 0:
        return False
    return True


def mark_read_recommendations(db, uid=None):

    if not uid:
        db.execute('update recommendation set hasRead="Y" where hasRead="P" and id>0;')
    else:
        db.execute('update recommendation set hasRead="Y" where hasRead="P" and userId=%s;', uid)


def mark_sourcing_done(db):

    db.execute('update sourcing_company_user_rel set followType=1040 where followType=1000 and id>0;')


def update_collection(db, colid, cid, sort_value=0.5, verify="N", user=None, create=None):

    active = db.get('select active from company where id=%s', cid)
    if active and active.active and active.active != 'Y':
        return 0
    if db.get('select count(*) as count from collection_company_rel '
              'where collectionId=%s and companyId=%s', colid, cid).count == 0:
        db.execute('insert into collection_company_rel '
                   '(collectionId, companyId, sort, verify, active, createTime, modifyTime, createUser) '
                   'values (%s, %s, %s, %s, "Y", now(), now(), %s)', colid, cid, sort_value, verify, user)
        set_collection_mark(db, colid, "Y")
        return 1
    else:
        if create:
            db.execute('update collection_company_rel set sort=%s, createTime=now(), modifyUser=%s '
                       'where collectionId=%s and companyId=%s', sort_value, user, colid, cid)
        else:
            db.execute('update collection_company_rel set sort=%s, modifyTime=now(), modifyUser=%s '
                       'where collectionId=%s and companyId=%s', sort_value, user, colid, cid)
        return 0


def exist_collection_company(db, colid, cid):

    return db.get('select count(*) c from collection_company_rel where collectionId=%s and companyId=%s '
                  'and (active is null or active="Y");', colid, cid).c > 0


def set_collection_mark(db, colid, mark):

    db.execute('update collection set mark=%s, modifyTime=now() where id=%s', mark, colid)


def set_collection_process_status(db, colid, status=1):

    db.execute('update collection set processStatus=%s where id=%s;', status, colid)


def update_collection_user(db, colid, uid, user=None):

    if len(db.query('select * from collection_user_rel where collectionId=%s and userId=%s;', colid, uid)) == 0:
        db.execute('insert into collection_user_rel (collectionId, userId, active, createUser, createTime, modifyTime) '
                   'values (%s, %s, "Y", %s, now(), now());', colid, uid, user)


def get_collection_companies(db, colid):

    return [x.companyId for x in db.query('select distinct companyId '
                                          'from collection_company_rel where collectionId=%s;', colid)]


def clear_collection(db, colid, update=False, olds=None):

    if not update:
        db.execute('delete collection_timeline.* from collection_timeline, collection_company_rel '
                   'where collection_timeline.collectionCompanyId=collection_company_rel.id '
                   'and collection_company_rel.collectionId=%s;', colid)
        db.execute('delete from collection_company_rel '
                   'where collectionId=%s and (verify is null or verify="N");', colid)
        # db.execute('update collection_company_rel set active="N" where collectionId=%s', colid)
    else:
        if not olds:
            olds = []
        for old in olds:
            colcid = db.get('select id from collection_company_rel '
                            'where collectionId=%s and companyId=%s', colid, old).id
            # db.execute('delete from collection_timeline where collectionCompanyId=%s;', colcid)
            # db.execute('update collection_company_rel set active="N" where id=%s;', colcid)
            db.execute('delete from collection_company_rel where id=%s and (verify is null or verify="N");', colcid)


def rm_collection_company(db, colid, cid):

    db.execute('update collection_company_rel set active="N", modifyTime=now() '
               'where collectionId=%s and companyId=%s;', colid, cid)


def update_company_sector(db, cid, sid, confidence):

    if db.get('select count(*) as count from company_sector where companyId=%s and verify="Y";', cid).count > 0:
        return
    if db.get('select count(company_sector.id) as count from company_sector, sector '
              'where company_sector.companyId=%s and company_sector.sectorId=sector.id '
              'and sector.level=1', cid).count > 0:
        db.execute('update company_sector set sectorId=%s, confidence=%s, modifyTime=now() where companyId=%s;',
                   sid, confidence, cid)
    else:
        db.execute('insert into company_sector '
                   '(companyId, sectorId, verify, active, createTime, modifyTime, confidence) '
                   'values (%s, %s, "N", "Y", now(), now(), %s);', cid, sid, confidence)


# def update_screenshot(db, aid, gid):
#
#     if len(db.query('select * from artifact_pic where artifactId=%s', aid)) == 0:
#         db.execute('insert into artifact_pic (artifactId, link, active, createTime, modifyTime, createUser) '
#                    'values (%s, %s, %s, now(), now(), %s)', aid, gid, 'Y', -1)
#     else:
#         db.execute('update artifact_pic set link=%s, modifyTime=now() where artifactId=%s', gid, aid)


# def update_netloc_title(db, netloc, title, short_domain):
#
#     if len(db.query('select * from news_domain where netloc=%s', netloc)) == 0:
#         db.execute('insert into news_domain (netloc, domain, title) values (%s, %s, %s)',
#                    netloc, short_domain, title)
#     else:
#         db.execute('update news_domain set title=%s where netloc=%s', title, netloc)


# def update_global_term(db, tw_smooth):
#
#     db.execute("update thesaurus set weight=%s, modifyTime=now() where weight='' and termType=35020;", tw_smooth)
#     db.execute("update thesaurus set weight=%s, modifyTime=now() where weight<%s and termType=35020;",
#                tw_smooth, tw_smooth)
#     db.execute("update thesaurus set weight=1, modifyTime=now() where weight!=1 and termType=35010;")


# def update_term(db, term, weight):
#
#     if len(db.query('select * from thesaurus where termName=%s', term)) == 0:
#         db.execute('insert into thesaurus (termName, termType, weight, createTime, modifyTime) '
#                    'values (%s, 35000, %s, now(), now())', term, weight)
#     elif len(db.query('select * from thesaurus where termName=%s and termType=35020', term)) == 1:
#         db.execute('update thesaurus set weight=%s, modifyTime=now() '
#                    'where termName=%s', weight, term)


# def update_pending_terms(db, terms):
#
#     for term in terms:
#         if len(db.query('select * from thesaurus where termName=%s;', term)) == 0:
#             db.execute('insert into thesaurus (termName, termType, weight, createTime, modifyTime) '
#                        'values (%s, 35000, 0, now(), now())', term)


def update_recruit_summary(db, cid, field, dic):

    # todo
    field += 2500
    keys, values = [], []
    for k, v in dic.items():
        keys.append(k)
        values.append(v)
    tmp = ', '.join(['%s' for _ in xrange(len(values))])
    values.append(cid)
    values.append(field)
    if db.get('select * from company_recruit_summary where companyId=%s and field=%s', cid, field):
        keys = ['%s=%%s' % k for k in keys]
        db.execute('update company_recruit_summary set %s, modifyTime=now() '
                   'where companyId=%%s and field=%%s' % ', '.join(keys), *values)
    else:
        keys = ', '.join(keys)
        query = 'insert into company_recruit_summary (%s, companyId, field, createTime, modifyTime) ' \
                'values (%s, %%s, %%s, now(), now());' % (keys, tmp)
        db.execute(query, *values)

    # set the major
    db.execute('update company_recruit_summary set isMajor="N" where companyId=%s and field!=%s', cid, field)


def update_tags_global_novelty(db):

    """
    update novelty of tags,
    currently measured by idf
    :return: None
    """
    size_d = float(db.get('select count(distinct companyId) as count from company_tag_rel '
                          'where (active is null or active!="N");').count)
    idf = {result.tagId: round(log10(size_d/result.count), 4)
           for result in db.query('SELECT tagId, count(tagId) as count FROM company_tag_rel '
                                  'where (active is null or active!="N") and type!=10012 group by tagId;')}
    db.executemany('update tag set novelty=%s, modifyTime=now() where id=%s;',
                   map(lambda x: (x[1], x[0]), idf.iteritems()))
    # for tag in db.query('select id from tag where type=11012;'):
    #     db.execute('update tag set novelty=10 where id=%s;', tag.id)


def insert_source_company(db, name, description):

    return db.execute('insert into source_company (name, description, source, createTime) '
                      'values (%s, %s, 13002, now())', name.strip(), description)


def exist_coldcall_link(db, cid):

    """
    check whether a coldcall is extracted and linked to companies
    """
    return len(db.query('select * from coldcall_source_company_rel where coldcallId=%s', cid)) > 0


def insert_coldcall_sc_link(db, ccid, scid):

    db.execute('insert into coldcall_source_company_rel (coldcallId, sourceCompanyId) values (%s, %s)', ccid, scid)


def insert_company_candidate(db, scid, cid, confidence):

    db.execute('insert into company_candidate (sourceCompanyId, companyId, confidence) values (%s, %s, %s)',
               scid, cid, confidence)


def miss_screen_shot(db, cid):

    aids = map(lambda x: x.id, db.query('select distinct id from artifact where companyId=%s and type=4010;', cid))
    return [aid for aid in aids
            if db.get('select count(*) as count from artifact_pic where artifactId=%s', aid).count == 0]


def rm_old_context(db, cid):

    for scid in db.query('select id from sourceCompany where companyId=%s;', cid):
        db.execute('delete from source_context where sourceCompanyId=%s and type=30000;', scid.id)


def rm_old_context_source(db, scid):

    db.execute('delete from source_context where sourceCompanyId=%s', scid)


def rm_pending_terms(db):

    db.execute('delete from thesaurus where termType=35000;')


def rm_dead_tags(db, cid, new_tags):

    """
    remove tags that are no longer relevant to company cid
    :param new_tags: ids of tags that are relevant to cid this time
    :return:
    """
    yellows = get_yellow_tags(db)
    original_tags = map(lambda x: x.tagId, db.query('select tagId from company_tag_rel '
                                                    'where companyId=%s and (verify!="Y" or verify is null) '
                                                    'and tagId not in %s;', cid, yellows))
    dead_tags = [tag for tag in original_tags if tag not in new_tags]
    for tid in dead_tags:
        db.execute('update company_tag_rel set active="N" where companyId=%s and tagId=%s;', int(cid), int(tid))


def rm_old_tags(db):

    """
    remove tags that are no longer used
    :param db:
    :return:
    """
    all_tags = set(map(lambda x: x.id, db.query('select id from tag;')))
    for tag in all_tags:
        if len(db.query('select * from company_tag_rel where tagId=%s;', tag)) == 0:
            db.execute('delete from tags_rel where tagId=%s', tag)
            db.execute('delete from tags_rel where tag2Id=%s', tag)
            db.execute('delete from tag where id=%s and (verify!="Y" or verify is null);', tag)
            print 'tag removed', tag


def rm_junk_tags(db):

    """
    remove tags whose type is 11001
    """
    for tag in db.query('select id from tag where type=11001;'):
        db.execute('update company_tag_rel set active="N" where tagId=%s and (verify is null or verify="N");', tag.id)


def rm_few_tags(db, threshold=8):

    all_tags = set(map(lambda x: x.id, db.query('select id from tag where type<11500;')))
    deleted = []
    for tag in all_tags:
        if db.get('select count(*) as count from tag where id=%s and verify="Y";', tag).count > 0:
            continue
        if len(db.query('select * from company_tag_rel where tagId=%s and '
                        '(active is null or active="Y");', tag)) < threshold:
            db.execute('update company_tag_rel set active="N" where tagId=%s and (verify is null or verify="N");', tag)
            if db.get('select count(*) as count from company_tag_rel where tagId=%s;', tag).count < threshold:
                tag_verify = db.get('select verify from tag where id=%s', tag).verify
                if (not tag_verify) or tag_verify == 'N':
                    db.execute('update tag set type=11002 where id=%s;', tag)
            else:
                ttype = db.get('select type from tag where id=%s', tag).type
                if ttype and ttype == 11002:
                    db.execute('update tag set type=11000, modifyTime=now() where id=%s;', tag)
    return deleted


def rm_1char_tags(db):

    one_chars = [x.id for x in db.query('select distinct id from tag where char_length(name)<2 or name is null;')]
    # names = [x.name for x in db.query('select distinct name from tag where char_length(name)<2 or name is null;')]
    for tag in one_chars:
        if db.execute('delete from company_tag_rel where tagId=%s and (verify!="Y" or verify is null);', tag):
            db.execute('delete from tags_rel where tagId=%s', tag)
            db.execute('delete from tags_rel where tag2Id=%s', tag)
            db.execute('delete from tag where id=%s;', tag)
    return one_chars


def rm_waste_tags(db):

    names = [x.termName for x in db.query('select distinct termName from thesaurus where termType=35001;')]
    for name in names:
        tid = db.get('select id from tag where name=%s;', name)
        if (not tid) or (not tid.id):
            continue
        tid = tid.id
        db.execute('delete from company_tag_rel where tagId=%s and (verify!="Y" or verify is null);', tid)
        db.execute('delete from tags_rel where tagId=%s', tid)
        db.execute('delete from tags_rel where tag2Id=%s', tid)
        try:
            db.execute('delete from tag where id=%s and (verify!="Y" or verify is null);', tid)
        except Exception, e:
            db.execute('update tag set type=11001 where id=%s', tid)


def exist_task_deal(db, cid, uid, self_sensitive=True, organization_processing=True):

    """
    check whether a company is assigned to a user as a task
    self_sensitive is about whether user uid relevant to this deal, or this deal has been assigned
    organization_processing is about where this deal is being processed by this organization
    """
    if db.get('select count(*) as c from company where companyStatus=2020 and id=%s', cid).c == 1:
        return True
    if organization_processing:
        oid = get_user_organization(db, uid)
        if oid:
            processing = db.get('select count(*) as count from deal where companyId=%s and status>19000 '
                                'and organizationId=%s;', cid, oid).count > 0
            if processing:
                return True
    if self_sensitive:
        return db.get('select count(*) as count from deal, deal_user_rel where deal.companyId=%s '
                      'and deal.id=deal_user_rel.dealId and deal_user_rel.userId=%s;', cid, uid).count > 0
    else:
        return db.get('select count(*) as count from deal, deal_user_rel where deal.companyId=%s '
                      'and deal.id=deal_user_rel.dealId;', cid).count > 0


def get_deal(db, cid, oid):

    results = db.query('select * from deal where companyId=%s and organizationId=%s', cid, oid)
    if len(results) > 0:
        return results[0].id
    return db.execute('insert into deal (companyId, organizationId, status, priority, '
                      'declineStatus, currency, createTime, modifyTime, createUser) '
                      'values (%s, %s, 19000, 20010, 18010, 0, now(), now(), 139);', cid, oid)


def get_deal_info(db, did):

    return db.get('select * from deal where id=%s', did)


def get_deal_tags(db, did):

    return [item.name for item in db.query('select tag.name as name from deal_tag_rel, tag '
                                           'where deal_tag_rel.dealTagId=tag.id and dealId=%s;', did)]


def get_deal_assignee(db, did):

    return [item.userId for item in db.query('select userId from deal_assignee where dealId=%s;', did)]


def get_deal_sponsor(db, did):

    return [item.sponsor for item in db.query('select sponsor from deal where id=%s;', did)]


def update_deal_user(db, did, uid):

    db.execute('insert into deal_user_rel (userId, dealId, userIdentify, type, createTime, modifyTime)'
               'values (%s, %s, 21020, 23030, now(), now())', uid, did)


def re_link(db, tid1, tid2=None):

    """
    remove tid1, and link its content to tid2
    """
    if not tid2:
        db.execute('delete from company_tag_rel where tagId=%s;', tid1)
        db.execute('delete from tags_rel where tagId=%s or tag2Id=%s;', tid1, tid1)
        db.execute('delete from tag where id=%s;', tid1)
    else:
        db.execute('update company_tag_rel set tagId=%s, modifyTime=now() where tagId=%s;', tid2, tid1)
        db.execute('update tags_rel set tagId=%s where tagId=%s', tid2, tid1)
        db.execute('update tags_rel set tag2Id=%s where tag2Id=%s', tid2, tid1)
        db.execute('delete from tag where id=%s', tid1)

        dups = db.query('select companyId, tagId, count(*) as c from company_tag_rel '
                        'group by companyId, tagId having c>1;')
        for dup in dups:
            for ctrid in db.query('select id from company_tag_rel where companyId=%s and tagId=%s order by modifyTime;',
                                  dup.companyId, dup.tagId)[1:]:
                db.execute('delete from company_tag_rel where id=%s;', ctrid.id)


def mark_android_explosion(db, aid):

    db.execute('update artifact set androidExplosion="Y" where id=%s;', aid)


def get_company_feature_tags(db, cid):

    return [c.tagId for c in db.query('select tagId from company_tag_rel where companyId=%s '
                                      'and (active is null or active="Y" or active="H");', cid)]


def get_topic_dimension_tags(db, tpid):

    resutls = {}
    for item in db.query('select tagType, tagId from topic_dimension, topic_dimension_tag where '
                         'topic_dimension.id=topicDimensionId and topicId=%s and topic_dimension.type=7010;', tpid):
        resutls.setdefault(item['tagType'], []).append(item['tagId'])
    return resutls


def get_topic_search_terms(db, tpid):

    return [item.name for item in db.query('select name from topic_dimension '
                                           'where type=7020 and name is not null and topicId=%s;', tpid)]


def get_topic_auto_pubilsh_status(db, tpid):

    return db.get('select autoPublish from topic where id=%s;', tpid).autoPublish


def get_topic_info(db, tpid):

    return db.get('select * from topic where id=%s;', tpid)


def get_topic_relevant_tags(db, tpid):

    return [t.tagId for t in db.query('select distinct tagId from topic_tag_rel '
                                      'where topicId=%s and (active is null or active="Y")', tpid)]


def get_topic_corresponding_tags(db):

    return {
        tp.id: tp.name for tp in db.query('select rel.topicId id, tag.name name from topic_tag_rel rel, tag '
                                          'where (rel.active is null or rel.active="Y") and tagId=tag.id;')
    }


def get_topic_company_active(db, cid):

    return db.get('select count(*) c from topic_company where active="Y" and companyId=%s;', cid).c > 0


def get_topic_messages(db, tpid, start):

    return db.query('select * from topic_message where topicId=%s and active="Y" and publishTime>%s;', tpid, start)


def get_topic_message(db, tpm):

    return db.get('select * from topic_message where id=%s;', tpm)


def get_topic_companies(db, tpid, start=None):

    if start:
        return db.query('select * from topic_company where topicId=%s and active="Y" and publishTime>%s;', tpid, start)
    return db.query('select * from topic_company where topicId=%s and active="Y";', tpid)


def get_topic_message_company_publish(db, tpc):

    tpm = db.get('select tpm.publishTime publishTime from topic_message tpm, topic_message_company_rel rel '
                 'where topicCompanyId=%s and tpm.id=topicMessageId and (rel.active is null or rel.active="Y") '
                 'and (tpm.active is null or tpm.active="Y") order by tpm.publishTime desc limit 1;', tpc.id)
    return tpm.publishTime if tpm else tpc.publishTime


def get_topic_message_companies(db, tpmid):

    cids = db.query('select tpc.companyId cid from topic_message_company_rel rel, topic_company tpc '
                    'where rel.topicMessageId=%s and (rel.active is null or rel.active="Y") '
                    'and rel.topicCompanyId=tpc.id;', tpmid)
    return [c.cid for c in cids]


def get_general_topics(db, topic_type=901):

    return [(item.id, item.autoPublish) for item in
            db.query('select id, autoPublish from topic where general="Y" '
                     'and (active!="N" or active is null) and type=%s;', topic_type)]


def get_all_topics(db):

    return [t.id for t in db.query('select * from topic where (active is null or active="Y");')]


def get_industries(db):

    return [(item.id, item.autoPublish) for item in
            db.query('select * from industry where (active!="N" or active is null);')]


def get_industry_tag(db, idid):

    industry = db.get('select tagId from industry where id=%s;', idid)
    return industry.tagId if industry and industry.tagId else None


def get_industry_tags(db):

    return [t.tagId for t in db.query('select distinct tagId from industry where tagId is not null and tagId!=0;')]


def get_industry_info(db, idid):

    return db.get('select * from industry where id=%s;', idid)


def get_industry_companies(db, idid, start=None):

    if start:
        return db.query('select * from industry_company '
                        'where industryId=%s and active="Y" and publishTime>%s;', idid, start)
    return db.query('select * from industry_company where industryId=%s and active="Y";', idid)


def get_company_industries(db, cid, mutiple=False):

    if not mutiple:
        return db.query('select * from industry_company where companyId=%s and active="Y";', cid)
    return db.query('select distinct industryId from industry_company where companyId in %s and active="Y";', cid)


def update_industry_company(db, idid, cid, active='P', confidence=0.5, source=None, modify=139):

    time.sleep(0.001)
    if db.get('select count(*) as c from industry_company where industryId=%s and companyId=%s;', idid, cid).c > 0:
        db.execute('update industry_company set modifyTime=now(), confidence=%s '
                   'where industryId=%s and companyId=%s;', confidence, idid, cid)
        return db.get('select id from industry_company where industryId=%s and companyId=%s;', idid, cid).id
    else:
        return db.execute('insert into industry_company (industryId, companyId, createTime, modifyTime, '
                          'publishTime, active, createUser, confidence, source, modifyUser) '
                          'values (%s, %s, now(), now(), now(3), %s, 139, %s, %s, %s);',
                          idid, cid, active, confidence, source, modify)


def get_industry_news(db, idid, active='Y', limit=100):

    return [idn.newsId for idn in db.query('select * from industry_news where industryId=%s and active=%s '
                                           'order by newsTime desc limit %s;', idid, active, limit)]


def update_industry_news(db, idid, nid, active, date=None):

    time.sleep(0.001)
    if db.get('select count(*) as c from industry_news where industryId=%s and newsId=%s;', idid, nid).c > 0:
        idn = db.get('select * from industry_news where industryId=%s and newsId=%s;', idid, nid)
        if idn.createUser != 139 or (idn.modifyUser and idn.modifyUser != 139):
            return idn.id
        else:
            db.execute('update industry_news set modifyTime=now(), active=%s '
                       'where industryId=%s and newsId=%s;', active, idid, nid)
    else:
        return db.execute('insert into industry_news '
                          '(industryId, newsId, createTime, modifyTime, publishTime, active, createUser, newsTime)'
                          ' values (%s, %s, now(), now(), now(3), %s, 139, %s);', idid, nid, active, date)


def update_topic_message(db, tpid, msg, active='P', relate_type=None, relate_id=None, detail_id=None, comments=None):

    time.sleep(0.001)
    if not relate_id:
        return db.execute('insert into topic_message '
                          '(topicId, message, createTime, modifyTime, publishTime, createUser, active) '
                          'values (%s, %s, now(), now(), now(3), 139, %s)', tpid, msg, active)

    if db.get('select count(*) as c from topic_message '
              'where topicId=%s and relateType=%s and relateId=%s;', tpid, relate_type, str(relate_id)).c > 0:
        db.execute('update topic_message set modifyTime=now(), message=%s '
                   'where topicId=%s and relateType=%s and relateId=%s;', msg, tpid, relate_type, str(relate_id))
        return
    detail_id = str(detail_id) if detail_id else None
    return db.execute('insert into topic_message (topicId, message, createTime, modifyTime, publishTime, createUser, '
                      'active, relateType, relateId, detailId, comments) '
                      'values (%s, %s, now(), now(), now(3), 139, %s, %s, %s, %s, %s);',
                      tpid, msg, active, relate_type, relate_id, detail_id, comments)


def update_topic_message_withoutdup(db, tpid, msg, active='P', relate_type=None, relate_id=None, detail_id=None):

    time.sleep(0.001)
    if (not relate_id) and db.get('select count(*) c from topic_message where topicId=%s '
                                  'and relateType=%s and detailId=%s', tpid, relate_type, detail_id).c > 0:
        db.execute('update topic_message set modifyTime=now(), message=%s '
                   'where topicId=%s and relateType=%s and detailId=%s;', msg, tpid, relate_type, str(detail_id))
        return
    elif db.get('select count(*) as c from topic_message '
                'where topicId=%s and relateType=%s and relateId=%s;', tpid, relate_type, relate_id).c > 0:
        db.execute('update topic_message set modifyTime=now(), message=%s '
                   'where topicId=%s and relateType=%s and relateId=%s;', msg, tpid, relate_type, str(relate_id))
        return
    return db.execute('insert into topic_message (topicId, message, createTime, modifyTime, publishTime, createUser, '
                      'active, relateType, relateId, detailId) '
                      'values (%s, %s, now(), now(), now(3), 139, %s, %s, %s, %s);',
                      tpid, msg, active, relate_type, str(relate_id), detail_id)


def update_topic_company(db, tpid, cid, active='P', confidence=0.5):

    time.sleep(0.001)
    if db.get('select count(*) as c from topic_company where topicId=%s and companyId=%s;', tpid, cid).c > 0:
        db.execute('update topic_company set modifyTime=now(), confidence=%s '
                   'where topicId=%s and companyId=%s;', confidence, tpid, cid)
        return db.get('select id from topic_company where topicId=%s and companyId=%s;', tpid, cid).id
    else:
        return db.execute('insert into topic_company '
                          '(topicId, companyId, createTime, modifyTime, publishTime, active, createUser, confidence) '
                          'values (%s, %s, now(), now(), now(3), %s, 139, %s);', tpid, cid, active, confidence)


def exist_topic_company(db, tpid, cid):

    return db.get('select count(*) as c from topic_company where topicId=%s and companyId=%s;', tpid, cid).c > 0


def update_topic_message_company(db, tpm, tpc):

    if db.get('select count(*) c from topic_message_company_rel '
              'where topicMessageId=%s and topicCompanyId=%s;', tpm, tpc).c == 0:
        db.execute('insert into topic_message_company_rel (topicMessageId, topicCompanyId, createTime) '
                   'values (%s, %s, now());', tpm, tpc)


def get_all_company_messages(db, dimension=None, start=None):

    if not dimension:
        return db.iter('select * from company_message where active="Y";')
    if start:
        return db.query('select * from company_message where trackdimension=%s and createTime>=%s;', dimension, start)
    return db.query('select * from company_message where active="Y" and trackdimension=%s;', dimension)


def get_company_messages(db, cid, active=None, start_period=None):

    if not active:
        return db.query('select * from company_message where companyId=%s '
                        'and createTime>"2017-06-01" and trackDimension!=6001;', cid)
    elif not start_period:
        return db.query('select * from company_message where companyId=%s and active=%s;', cid, active)
    return db.query('select * from company_message where companyId=%s and active=%s and publishTime>%s;',
                    cid, active, start_period)


def get_company_message(db, cmid):

    return db.get('select * from company_message where id=%s;', cmid)


def update_investor_message(db, iid, msg, track_dimension, relate_type=None, relate_id=None, active='P', comments=None):

    time.sleep(0.001)
    if not relate_type:
        return db.execute('insert into investor_message (investorId, message, trackDimension, '
                          'createTime, modifyTime, publishTime, createUser, active, comments) '
                          'values (%s, %s, %s, now(), now(), now(3), 139, %s, %s);',
                          iid, msg, track_dimension, active, comments)
    if db.get('select count(*) as c from investor_message where investorId=%s and '
              'relateType=%s and relateId=%s;', iid, relate_type, relate_id).c > 0:
        db.execute('update investor_message set message=%s, modifyTime=now(), trackDimension=%s '
                   'where investorId=%s and relateType=%s and relateId=%s;',
                   msg, track_dimension, iid, relate_type, relate_id)
        return
    else:
        return db.execute('insert into investor_message (investorId, message, trackDimension, relateType, relateId, '
                          'createTime, modifyTime, publishTime, createUser, active, comments) '
                          'values (%s, %s, %s, %s, %s, now(), now(), now(3), 139, %s, %s);',
                          iid, msg, track_dimension, relate_type, relate_id, active, comments)


def get_investor_message(db, iid, track_dimension):

    return db.query('select * from investor_message where investorId=%s and trackDimension=%s;', iid, track_dimension)


def update_investor_message_detail(db, imid, detail):

    db.execute('update investor_message set detailId=%s where id=%s;', detail, imid)


def update_company_message(db, cid, msg, track_dimension, relate_type=None, relate_id=None, active='P', comments=None):

    time.sleep(0.001)
    if not relate_type:
        return db.execute('insert into company_message (companyId, message, trackDimension, '
                          'createTime, modifyTime, publishTime, createUser, active, comments) '
                          'values (%s, %s, %s, now(), now(), now(3), 139, %s, %s);',
                          cid, msg, track_dimension, active, comments)
    if db.get('select count(*) as c from company_message where companyId=%s and trackDimension=%s and '
              'relateType=%s and relateId=%s;', cid, track_dimension, relate_type, relate_id).c > 0:
        db.execute('update company_message set message=%s, modifyTime=now() where companyId=%s and '
                   'trackDimension=%s and relateType=%s and relateId=%s;',
                   msg, cid, track_dimension, relate_type, relate_id)
        return
    else:
        return db.execute('insert into company_message (companyId, message, trackDimension, relateType, relateId, '
                          'createTime, modifyTime, publishTime, createUser, active, comments) '
                          'values (%s, %s, %s, %s, %s, now(), now(), now(3), 139, %s, %s);',
                          cid, msg, track_dimension, relate_type, relate_id, active, comments)


def update_detail_company_message(db, cid, msg, track_dimension, relate_type, relate_id, detail_id=None, comments=None):

    time.sleep(0.001)
    if db.get('select count(*) as c from company_message where companyId=%s and trackDimension=%s and '
              'relateType=%s and relateId=%s and detailId=%s;',
              cid, track_dimension, relate_type, relate_id, detail_id).c > 0:
        db.execute('update company_message set message=%s, modifyTime=now() where companyId=%s and '
                   'trackDimension=%s and relateType=%s and relateId=%s and detailId=%s;',
                   msg, cid, track_dimension, relate_type, relate_id, detail_id)
        return
    else:
        return db.execute('insert into company_message (companyId, message, trackDimension, relateType, relateId, '
                          'createTime, modifyTime, publishTime, createUser, detailId, comments) '
                          'values (%s, %s, %s, %s, %s, now(), now(), now(3), 139, %s, %s);',
                          cid, msg, track_dimension, relate_type, relate_id, detail_id, comments)


def update_daily_company_message(db, cid, msg, track_dimension, relate_type, relate_id, yesterday,
                                 detail_id=None, comments=None):

    time.sleep(0.001)
    if db.get('select count(*) as c from company_message where companyId=%s and trackDimension=%s and '
              'relateType=%s and relateId=%s and createTime>%s;',
              cid, track_dimension, relate_type, relate_id, yesterday).c > 0:
        db.execute('update company_message set message=%s, detailId=%s, modifyTime=now() where companyId=%s and '
                   'trackDimension=%s and relateType=%s and relateId=%s;',
                   msg, detail_id, cid, track_dimension, relate_type, relate_id)
        return
    else:
        return db.execute('insert into company_message (companyId, message, trackDimension, relateType, relateId, '
                          'createTime, modifyTime, publishTime, createUser, detailId, comments) '
                          'values (%s, %s, %s, %s, %s, now(), now(), now(3), 139, %s, %s);',
                          cid, msg, track_dimension, relate_type, relate_id, detail_id, comments)


def update_continuous_company_message(db, cid, msg, track_dimension, relate_type, relate_id,
                                      continuous_gap=7, detail_id=None, comments=None):

    last_check = datetime.now() - timedelta(days=continuous_gap)
    if detail_id:
        if db.get('select count(*) c from company_message where companyId=%s and trackDimension=%s and relateType=%s '
                  'and relateId=%s and detailId=%s and modifyTime>%s;',
                  cid, track_dimension, relate_type, relate_id, detail_id, last_check).c > 0:
            db.execute('update company_message set modifyTime=now(), message=%s where companyId=%s '
                       'and trackDimension=%s and relateType=%s and relateId=%s and detailId=%s and modifyTime>%s;',
                       msg, cid, track_dimension, relate_type, relate_id, detail_id, last_check)
        else:
            db.execute('insert into company_message (companyId, message, trackDimension, relateType, relateId, '
                       'createTime, modifyTime, publishTime, createUser, detailId, comments) '
                       'values (%s, %s, %s, %s, %s, now(), now(), now(3), 139, %s, %s);',
                       cid, msg, track_dimension, relate_type, relate_id, detail_id, comments)
    else:
        if db.get('select count(*) c from company_message where companyId=%s and trackDimension=%s and relateType=%s '
                  'and relateId=%s and modifyTime>%s;',
                  cid, track_dimension, relate_type, relate_id, last_check).c > 0:
            db.execute('update company_message set modifyTime=now(), message=%s where companyId=%s '
                       'and trackDimension=%s and relateType=%s and relateId=%s and modifyTime>%s;',
                       msg, cid, track_dimension, relate_type, relate_id, last_check)
        else:
            db.execute('insert into company_message (companyId, message, trackDimension, relateType, relateId, '
                       'createTime, modifyTime, publishTime, createUser, detailId, comments) '
                       'values (%s, %s, %s, %s, %s, now(), now(), now(3), 139, %s, %s);',
                       cid, msg, track_dimension, relate_type, relate_id, detail_id, comments)


def get_new_company_message(db, cid, msg, dimension):

    cm = db.get('select * from company_message where companyId=%s and trackDimension=%s order by id desc limit 1;',
                cid, dimension)
    if cm:
        return cm.id
    else:
        return db.execute('insert into company_message (companyId, message, trackDimension, relateType, '
                          'createTime, modifyTime, publishTime, createUser, active) values '
                          '(%s, %s, %s, 100, now(), now(), now(3), 139, "Y");', cid, msg, dimension)


def get_news_company_message(db, cid, nid):

    return db.get('select * from company_message where companyId=%s and relateId=%s and active="Y" limit 1;', cid, nid)


def update_last_message_time(db, tpid):

    last = db.get('select publishTime from topic_message '
                  'where topicId=%s and active="Y" order by publishTime desc limit 1;', tpid)
    if last:
        db.execute('update topic set lastMessageTime=%s where id=%s', last.publishTime, tpid)


def update_industry_last_message_time(db, idid):

    last_news = db.get('select publishTime from industry_news where industryId=%s and active="Y" '
                       'order by publishTime desc limit 1;', idid)
    last_company = db.get('select publishTime from industry_company where industryId=%s and active="Y" '
                          'order by publishTime desc limit 1;', idid)
    if last_news:
        last_news = last_news.publishTime
    if last_company:
        last_company = last_company.publishTime
    if last_company or last_news:
        publish = max(filter(lambda x: x, [last_news, last_company]))
        db.execute('update industry set lastMessageTime=%s where id=%s', publish, idid)


def update_extract_source_company(db, stype, extract_source, cid, relate_id=None, only_insert=True,
                                  comments=None, allow_no_publish=False):

    if (not allow_no_publish) and (get_company_active(db, cid) != 'Y'):
        return
    if (not only_insert) and db.get('select count(*) c from company_extract_source where type=%s and extractSource=%s '
                                    'and companyId=%s and relateId=%s;', stype, extract_source, cid, relate_id).c > 0:
        return
    db.execute('insert into company_extract_source '
               '(companyId, type, extractSource, active, createTime, createUser, modifyTime, relateId, comments) '
               'values (%s, %s, %s, "Y", now(3), 139, now(3), %s, %s);',
               cid, stype, extract_source, relate_id, comments)


def get_sourcing_company(db, start, module=None):

    if not module:
        return [c.companyId for c in db.query('select distinct companyId from sourcing_company '
                                              'where modifyTime>%s and comments is null', start)]
    if module == 'full' or module == 'all':
        return [(c.companyId, c.comments) for c in db.query('select distinct companyId, comments from sourcing_company '
                                                            'where modifyTime>%s and comments is not null', start)]
    return [(c.companyId, c.comments) for c in db.query('select distinct companyId, comments from sourcing_company '
                                                        'where modifyTime>%s and comments like "%%%s%%";',
                                                        start, module)]


def exist_extract_source(db, cid, source=67003, start=None):

    if not start:
        start = datetime.now() - timedelta(days=1)
    return db.get('select count(*) c from company_extract_source '
                  'where companyId=%s and type=%s and createTime>%s;', cid, source, start).c > 0


def clear_sourcing_company(db):

    allowed_no_publishes = [sc.companyId for sc in db.query('select distinct companyId from sourcing_company '
                                                            'where comments=71001 order by id desc limit 2000;')]
    for c in db.query('select company.id cid from company, sourcing_company where companyId=company.id and '
                      '((company.active!="Y" and company.active is not null) '
                      'or company.companyStatus in (2020, 2025));'):
        if c.cid in allowed_no_publishes:
            continue
        db.execute('delete from sourcing_company where companyId=%s;', c.cid)
        db.execute('delete from company_extract_source where companyId=%s;', c.cid)
        db.execute('delete from sourcing_company_user_rel where companyId=%s;', c.cid)
    for c in db.query('select company.id cid from company, corporate where company.corporateId=corporate.id '
                      'and corporate.locationId>370;'):
        db.execute('delete from sourcing_company where companyId=%s;', c.cid)
        db.execute('delete from company_extract_source where companyId=%s;', c.cid)
        db.execute('delete from sourcing_company_user_rel where companyId=%s;', c.cid)


def update_sourcing_company(db, cid, repeat_min_date=None):

    # default sourcing company, could be pushed to anyone
    if not repeat_min_date:
        repeat_min_date = datetime.now()
    if db.get('select count(*) c from sourcing_company where companyId=%s and modifyTime>%s;',
              cid, repeat_min_date).c > 0:
        return
    if db.get('select count(*) c from sourcing_company where companyId=%s;', cid).c > 0:
        db.execute('update sourcing_company set modifyTime=now(), comments=null where companyId=%s;', cid)
    else:
        db.execute('insert into sourcing_company (companyId, active, createTime, modifyTime, createUser) '
                   'values (%s, "Y", now(), now(), 139)', cid)


def update_custom_sourcing_company(db, cid, module, repeat_min_date=None):

    if not repeat_min_date:
        repeat_min_date = datetime.now()
    sourced = db.get('select * from sourcing_company where companyId=%s and modifyTime>%s;', cid, repeat_min_date)
    if sourced and (sourced.comments is None):
        return
    if db.get('select count(*) c from sourcing_company where companyId=%s;', cid).c > 0:
        comments = sourced.comments.split(',')
        comments.append(module)
        db.execute('update sourcing_company set modifyTime=now(), comments=%s where companyId=%s;',
                   cid, ','.join(set([str(c) for c in comments])))
    else:
        db.execute('insert into sourcing_company (companyId, active, createTime, modifyTime, createUser, comments) '
                   'values (%s, "Y", now(), now(), 139, %s)', cid, module)


def update_sourcing_user(db, cid, uid, repeat_min_date=None, gongshang='N'):

    if not repeat_min_date:
        repeat_min_date = datetime.now() - timedelta(days=7)
    if db.get('select count(*) c from sourcing_company_user_rel where companyId=%s and userId=%s and createTime>%s;',
              cid, uid, repeat_min_date).c > 0:
        db.execute('update sourcing_company_user_rel set modifyTime=now() where companyId=%s and userId=%s;', cid, uid)
    else:
        db.execute('insert into sourcing_company_user_rel '
                   '(companyId, userId, active, createTime, modifyTime, followType, sourceGongshang ) '
                   'values (%s, %s, "Y", now(), now(), 1000, %s);', cid, uid, gongshang)


def get_saoanzi_item(db, cid, check_date, active='Y'):

    item = db.get('select id from saoanzi_item where companyId=%s and createTime>=%s;', cid, check_date)
    if item:
        return item.id
    else:
        return db.execute('insert into saoanzi_item (companyId, active, createTime) '
                          'values (%s, %s, now());', cid, active)


def get_daily_saoanzi_items(db, start, active='Y'):

    if not active:
        return db.query('select * from saoanzi_item where createTime>%s;', start)
    return db.query('select * from saoanzi_item where createTime>=%s and active=%s;', start, active)


def get_daily_saoanzi_sources(db, start):

    return db.query('select sis.*, si.companyId, ss.name source '
                    'from saoanzi_item_source sis, saoanzi_item si, saoanzi_source ss '
                    'where sis.saoanziItemId=si.id and sis.saoanziSourceId=ss.id and sis.createTime>%s;', start)


def update_saoanzi_item_status(db, siid, active):

    db.execute('update saoanzi_item set active=%s where id=%s;', active, siid)
    db.execute('update saoanzi_item_source set active=%s where saoanziItemId=%s;', active, siid)
    db.execute('update saoanzi_item_cate set active=%s where saoanziItemId=%s;', active, siid)


def get_saoanzi_item_sources(db, siid):

    return db.query('select s.* from saoanzi_source s, saoanzi_item_source sis where sis.saoanziItemId=%s '
                    'and sis.saoanziSourceId=s.id;', siid)


def update_saoanzi_item_source(db, siid, source, relate_type=None, relate_id=None, detail=None):

    if db.get('select id from saoanzi_item_source where saoanziItemId=%s and saoanziSourceId=%s;', siid, source):
        return
    db.execute('insert into saoanzi_item_source '
               '(saoanziSourceId, saoanziItemId, relateType, relateId, detailId, active, createTime) '
               'values (%s, %s, %s, %s, %s, "Y", now());',
               source, siid, relate_type, relate_id, detail)


def update_saoanzi_item_cate(db, siid, cateid):

    if db.get('select id from saoanzi_item_cate where saoanziItemId=%s and saoanziCateId=%s;', siid, cateid):
        return
    return db.execute('insert into saoanzi_item_cate (saoanziItemId, saoanziCateId, active, createTime) '
                      'values (%s, %s, "Y", now());', siid, cateid)


def update_saoanzi_source_summary(db, today, check_time):

    sources_today = []
    for sis in db.query('select saoanziSourceId source, count(*) c from saoanzi_item_source '
                        'where createTime>=%s and active="Y" group by saoanziSourceId;', today):
        db.execute('update saoanzi_source set todayCnt=%s, lastSourceTime=%s where id=%s;',
                   sis.c, check_time - timedelta(minutes=randint(1, 5)), sis.source)
        sources_today.append(sis.source)
    if sources_today:
        db.execute('update saoanzi_source set todayCnt=0, lastSourceTime=%s where id not in %s;',
                   check_time, sources_today)
    else:
        db.execute('update saoanzi_source set todayCnt=0, lastSourceTime=%s where id>0;', check_time)


def update_saoanzi_cate_summary(db, today, check_time):

    cates_today = []
    for sis in db.query('select saoanziCateId cate, count(*) c from saoanzi_item_cate '
                        'where createTime>=%s and active="Y" group by saoanziCateId;', today):

        db.execute('update saoanzi_cate set todayCnt=%s, lastSourceTime=%s where id=%s;',
                   sis.c, check_time, sis.cate)
        cates_today.append(sis.cate)
    if not cates_today:
        db.execute('update saoanzi_cate set todayCnt=0, lastSourceTime=%s where id>0;', check_time)
    else:
        db.execute('update saoanzi_cate set todayCnt=0, lastSourceTime=%s where id not in %s;', check_time, cates_today)


def update_saoanzi_user_summary(db, uid, cnt, check_time):

    db.execute('update user_saoanzi_conf set todayCnt=%s, lastSourceTime=%s where userId=%s;', cnt, check_time, uid)


def update_saoanzi_user_source_summary(db, uid, anzis, check_time, today):

    if not anzis:
        db.execute('update user_saoanzi_source_conf set todayCnt=0, lastSourceTime=%s '
                   'where userId=%s;', check_time, uid)
        return
    user_sources = [conf.saoanziSourceId for conf in db.query('select distinct saoanziSourceId '
                                                              'from user_saoanzi_source_conf where userId=%s;', uid)]
    for sis in db.query('select saoanziSourceId source, count(*) c from saoanzi_item_source '
                        'where createTime>=%s and active="Y" and saoanziItemId in %s group by saoanziSourceId;',
                        today, list(anzis)):
        db.execute('update user_saoanzi_source_conf set todayCnt=%s, lastSourceTime=%s '
                   'where userId=%s and saoanziSourceId=%s;', sis.c, check_time, uid, sis.source)
        if sis.source in user_sources:
            user_sources.remove(sis.source)
    for user_source in user_sources:
        db.execute('update user_saoanzi_source_conf set todayCnt=0, lastSourceTime=%s '
                   'where userId=%s and saoanziSourceId=%s;', check_time, uid, user_source)


def get_saoanzi_users(db):

    return [u.uid for u in db.query('select distinct conf.userId uid from user_saoanzi_conf conf, organization org '
                                    'where org.serviceStatus="Y" and conf.active="Y" and conf.organizationId=org.id;')]


def get_all_digital_token(db):

    return [dt.id for dt in db.query('select * from digital_token;')]


def get_digital_token_info(db, dtid):

    return db.get('select * from digital_token where id=%s;', dtid)


def get_digital_token_market_info(db, dtid):

    return db.get('select * from digital_token_market where digitalTokenId=%s order by modifyTime desc limit 1;', dtid)


if __name__ == '__main__':

    print __file__
    import db as dbconfig
    db = dbconfig.connect_torndb()
    print get_company_index_type(db, 473378)
    # print get_company_comps(db, 258945)
    # get_android_explosion(db)
    # get_company_yellow_time_deduction(db, 189284)
    # print get_artifact_idname_from_cid(db, 228890, True)
    # mark_read_recommendations(db)
    # print could_recommend(db, 219, 11040)
    # print get_company_location(db, 261)
    # print get_nocomps_company(db)
    # print rm_few_tags(db)
    # print rm_1char_tags(db)
    # print get_user_task_volumn(db, 18)
    # print get_company_create_date(db, 261), type(get_company_create_date(db, 261))
    # print get_company_establish_date(db, 293)
    # print get_company_tags_idname(db, 19461)
    # print get_company_tags_yellow(db, 154481)
    # update_topic_message_withoutdup(db, 52, u'主题酒店运营商, 椰子悬空酒店开启了新一轮融资', "Y", 80,
    #                                 get_company_latest_fa(db, 262405), detail_id=262405)
    # update_company_message_without_dup(db, 268470, u'', 8001, 80, get_company_latest_fa(db, 268470))
    # print get_company_index_type(db, 170155)
    # rm_old_tags(db)
    # update_tags_global_novelty(db)
    # print get_company_tags_info(db, 261)
    # print get_terms_by(db, 35010)
    # print get_top_yellow(db, 5)
    # print get_company_source(db, 261)
    # print get_funding_by_date(db, ('2016-12-01', '2017-03-01'))[0]
    db.close()
