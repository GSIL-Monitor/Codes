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
import itertools
from math import pow
from datetime import datetime

import numpy as np

era = {
    50: [122, 109, 114, 202, 211],
    70: [125, 116, 134, 2164, 220],
    80: [479, 2265, 235, 464]
}


def get_fundings():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    rn = lambda x: db.get('select * from dictionary where typeValue=1 and value=%s', x).name
    with codecs.open('dumps/style', 'w', 'utf-8') as fo:
        for iid in itertools.chain(*era.values()):
            iname = dbutil.get_investor_name(db, iid)
            fo.write('\n\n%s\n' % iname)
            cinfo = get_investor_portfolio_companies(db, mongo, iid)
            finfo = get_investor_portfolio_statistic(db, iid)
            # 1 行业
            fo.write(u'1. 行业\n')
            for tag, weight in cinfo.get('tags'):
                fo.write('\t%s\t%s\n' % (tag, weight))
            # 3 阶段
            fo.write(u'3. 阶段\n')
            for r, weight in sorted(finfo.get('round').items(), key=lambda x: x[0]):
                fo.write('\t%s\t%s\n' % (rn(r), weight))
            # 4 连续投资
            fo.write(u'4. 连续投资一家公司的公司数量\t%s\n' % finfo.get('dups'))
            # 5
            fo.write(u'5. 出手次数\t%s\n' % finfo.get('total'))
            # 6 再融资
            fo.write(u'6. 机构首次投资某公司后，该公司后续融资次数\n')
            for t, count in sorted(finfo.get('posts').items(), key=lambda x: x[0]):
                fo.write(u'\t再融%s次公司数量\t%s\n' % (t, count))
            # 9 news count
            fo.write(u'9. 2017年以来相关新闻数量\t%s\n' % cinfo.get('news'))
            # 11 location
            fo.write(u'11. 投资企业地域分布比例\n')
            for l, weight in sorted(cinfo.get('location').items(), key=lambda x: -x[1]):
                fo.write('\t%s\t%s\n' % (l, weight))
            # 12 alone
            fo.write(u'12. 单独投资率\t%s\n' % finfo.get('alone'))
    with codecs.open('dumps/style.irr', 'w', 'utf-8') as fo:
        for iid in itertools.chain(*era.values()):
            iname = dbutil.get_investor_name(db, iid)
            for funding in get_investor_portfolio_return(db, iid):
                fo.write('%s\t%s' % (iname, funding))


def get_investor_portfolio_statistic(db, iid):

    statistic = {}
    pfls = db.query('select company.id cid, funding.* '
                    'from company, funding, funding_investor_rel rel, corporate cp '
                    'where rel.investorId=%s and funding.corporateId = company.corporateId '
                    'and (company.active is null or company.active="Y") '
                    'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                    'and rel.fundingId=funding.id and (funding.active is null or funding.active="Y") '
                    'and (rel.active is null or rel.active="Y") '
                    'and funding.fundingDate>="2013-01-01" and funding.fundingDate<="2018-06-01" '
                    'order by fundingDate asc;', iid)
    total = len(pfls)
    # round
    rnds = db.query('select distinct funding.round r, count(*) c '
                    'from company, funding, funding_investor_rel rel, corporate cp '
                    'where rel.investorId=%s and funding.corporateId = company.corporateId '
                    'and (company.active is null or company.active="Y") '
                    'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                    'and rel.fundingId=funding.id and (funding.active is null or funding.active="Y") '
                    'and (rel.active is null or rel.active="Y") '
                    'and funding.fundingDate>="2013-01-01" and funding.fundingDate<="2018-06-01" '
                    'group by funding.round;', iid)
    rounds = {r.r: round(r.c*1.0/total, 4) for r in rnds}
    statistic['round'] = rounds
    # 连续投资
    dups = db.query('select distinct company.id, count(*) c '
                    'from company, funding, funding_investor_rel rel, corporate cp '
                    'where rel.investorId=%s and funding.corporateId = company.corporateId '
                    'and (company.active is null or company.active="Y") '
                    'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                    'and rel.fundingId=funding.id and (funding.active is null or funding.active="Y") '
                    'and (rel.active is null or rel.active="Y") '
                    'and funding.fundingDate>="2013-01-01" and funding.fundingDate<="2018-06-01" '
                    'group by company.id having c>1;', iid)
    statistic['dups'] = len(dups)
    # total
    statistic['total'] = total
    # next round
    cach = set()
    posts = {}
    for pfl in pfls:
        if pfl.companyId in cach:
            continue
        cach.add(pfl.companyId)
        post_fundings = db.query('select funding.* '
                                 'from company, funding, corporate cp '
                                 'where funding.corporateId = company.corporateId '
                                 'and (company.active is null or company.active="Y") '
                                 'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                                 'and (funding.active is null or funding.active="Y") and company.id=%s '
                                 'and funding.fundingDate>%s order by fundingDate desc;',
                                 pfl.companyId, pfl.fundingDate)
        if len(post_fundings) == 0:
            continue
        posts[len(post_fundings)] = posts.get(len(post_fundings), 0) + 1
    statistic['posts'] = posts
    # invest alone
    fids = [pfl.id for pfl in pfls]
    alones = db.query('select fundingId, count(*) c from funding_investor_rel where fundingId in %s and '
                      '(active is null or active="Y") group by fundingId having c=1;', fids)
    statistic['alone'] = round(len(alones) * 1.0 / total, 2)
    return statistic


def get_investor_portfolio_companies(db, mongo, iid):

    companies = {}
    pfls = db.query('select distinct company.id cid '
                    'from company, funding, funding_investor_rel rel, corporate cp '
                    'where rel.investorId=%s and funding.corporateId = company.corporateId '
                    'and (company.active is null or company.active="Y") '
                    'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                    'and rel.fundingId=funding.id and (funding.active is null or funding.active="Y") '
                    'and (rel.active is null or rel.active="Y") '
                    'and funding.fundingDate>="2013-01-01" and funding.fundingDate<="2018-06-01" '
                    'order by fundingDate asc;', iid)
    cids = [pfl.cid for pfl in pfls]
    # tags
    tags = {}
    for cid in cids:
        for t in dbutil.get_company_tags_info(db, cid, [11012, 11013]):
            tags[t.tid] = tags.get(t.tid, 0) + 1
    normalizer = sum(tags.values())
    ntags = {dbutil.get_tag_name(db, tid): round(count*1.0/normalizer, 4) for tid, count in tags.items()}
    companies['tags'] = sorted(ntags.items(), key=lambda x: -x[1])[:20]
    # count of news
    y2017 = datetime.strptime('2017-01-01', '%Y-%m-%d')
    companies['news'] = len(list(mongo.article.news.find({'investorIds': iid, 'processStatus': 1,
                                                          'date': {'$gte': y2017}})))
    # locations
    locations = [dbutil.get_company_location(db, cid)[1] for cid in cids]
    locations = {l: round(locations.count(l)*1.0/len(locations), 4) for l in set(locations)}
    companies['location'] = locations
    return companies


def get_investor_portfolio_return(db, iid):

    pfls = db.query('select company.id cid, funding.* '
                    'from company, funding, funding_investor_rel rel, corporate cp '
                    'where rel.investorId=%s and funding.corporateId = company.corporateId '
                    'and (company.active is null or company.active="Y") '
                    'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                    'and rel.fundingId=funding.id and (funding.active is null or funding.active="Y") '
                    'and (rel.active is null or rel.active="Y") '
                    'and funding.fundingDate>="2013-01-01" and funding.fundingDate<="2018-06-01" '
                    'order by fundingDate asc;', iid)
    cach = set()
    for pfl in pfls:
        if pfl.corporateId in cach:
            continue
        cach.add(pfl.corporateId)
        fdate = pfl.fundingDate
        fprecise = None
        pprecise = None
        if pfl.investment:
            fprecise = {'Y': 1, 'N': 5}.get(pfl.precise, 1)
            investment = int(pfl.investment * fprecise * dbutil.get_currency_rate(db, pfl.currency) / 10000)
        else:
            investment = u'未知'
        post_fundings = db.query('select funding.* '
                                 'from company, funding, corporate cp '
                                 'where funding.corporateId = company.corporateId '
                                 'and (company.active is null or company.active="Y") '
                                 'and company.corporateId=cp.id and (cp.active is null or cp.active="Y") '
                                 'and (funding.active is null or funding.active="Y") and company.id=%s '
                                 'and funding.fundingDate>%s order by fundingDate desc;',
                                 pfl.companyId, pfl.fundingDate)
        psinvestment = u'未知'
        psinvestmentdate = u'无'
        if post_fundings and post_fundings[0].investment:
            pprecise = {'Y': 1, 'N': 5}.get(post_fundings[0].precise, 1)
            psinvestment = int(post_fundings[0].investment * pprecise * dbutil.get_currency_rate(db, post_fundings[0].currency) / 10000)
        if post_fundings:
            psinvestmentdate = post_fundings[0].fundingDate
        if (investment != u'未知') and (psinvestment != u'未知') and (psinvestment > investment):
            timediff = round((psinvestmentdate - fdate).days/365.0, 2)
            increment = psinvestment*1.0/investment
            if timediff == 0:
                irr = u'无'
            elif timediff == 1:
                irr = round(increment - 1, 4)
            else:
                irr = round(pow(increment, 1/timediff), 4) - 1
        else:
            irr = u'无'
            timediff = 0
        all_precise = (fprecise is not None) and (fprecise == 1) and (pprecise is not None) and (pprecise == 1)
        yield '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (dbutil.get_company_name(db, pfl.cid), investment, fdate,
                                                        len(post_fundings), psinvestment, psinvestmentdate,
                                                        irr, all_precise, timediff)


def do_irr():

    data = [line.strip().split('\t') for line in codecs.open('files/qingshan', encoding='utf-8')]
    investors = {item[0] for item in data}
    # all, precise, no boom
    d1, d2, d3 = {}, {}, {}
    for item in [i for i in data if i[7] != u'无']:
        d1.setdefault(item[0], []).append((int(item[2]), float(item[7])))
    for item in [i for i in data if i[7] != u'无' and i[8] == 'True' and float(i[7]) < 500]:
        d2.setdefault(item[0], []).append((int(item[2]), float(item[7])))
    for item in [i for i in data if i[7] != u'无' and float(i[7]) < 500]:
        d3.setdefault(item[0], []).append((int(item[2]), float(item[7])))
    for iv in investors:
        print iv,\
            round(np.average([i[1] for i in d3.get(iv)], weights=[i[0] for i in d3.get(iv)]), 4), \
            round(np.average([i[1] for i in d2.get(iv)], weights=[i[0] for i in d2.get(iv)]), 4)


if __name__ == '__main__':

    print __file__
    do_irr()
    # get_fundings()
