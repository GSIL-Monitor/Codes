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

from neo4j.v1 import GraphDatabase, basic_auth


class Investment(object):

    def __init__(self):

        self.neo4j = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))
        self.db = dbcon.connect_torndb()

    def build_graph(self):

        session = self.neo4j.session()

        # insert investments
        for funding in dbutil.get_funding_by_date(self.db, ('2016-01-01', '2017-03-01')):
            if funding.active and funding.active == 'N':
                continue
            finfo = self.db.query('select funding_investor_rel.*, investor.name as iname '
                                  'from funding_investor_rel, investor '
                                  'where (funding_investor_rel.active is null or funding_investor_rel.active="Y") '
                                  'and investorId=investor.id and (investor.active is null or investor.active="Y") '
                                  'and fundingId=%s;', funding.id)
            if not finfo:
                continue
            cinfo = self.db.query('select distinct tagId from company_tag_rel, tag where companyId=%s and '
                                  'tagId=tag.id and (company_tag_rel.active is null or company_tag_rel.active="Y") '
                                  'and tag.type in (11011, 11012);', funding.companyId)
            fround = int(funding.round)/10 if funding.round else 0
            # TODO no more company id
            iid, cid = funding.id, funding.companyId
            session.run('MERGE (i:Investment {id: {iid}}) '
                        'MERGE (c:Company {id: {cid}}) '
                        'MERGE (i) -[:invest]-> (c) '
                        'SET i.date = {date}, i.round = {round} '
                        'RETURN i, c',
                        {'iid': iid, 'date': funding.fundingDate.strftime('%Y%m%d'),
                         'round': fround, 'cid': cid})
            for c in cinfo:
                session.run('MERGE (c:Company {id: {cid}}) '
                            'MERGE (t:Tag {id: {tag}}) '
                            'MERGE (c) -[:tag]-> (t) ', {'cid': cid, 'tag': c.tagId})
            for f in finfo:
                session.run('MERGE (i:Investment {id: {iid}}) '
                            'MERGE (iv:Investor {id: {iname}}) '
                            'MERGE (iv) -[:participate]-> (i)', {'iid': iid, 'iname': f.iname})

        # investor relation
        for investor in session.run('MATCH (iv:Investor)-[:participate]-(i) '
                                    'WITH iv, count(i) as count WHERE count > 5 RETURN iv.id as iid'):
            candidates = session.run('MATCH (ier)-[:participate]-(i1), (ier2)-[:participate]-(i2) '
                                     'WHERE ier.id={investor} and abs(i1.round-i2.round)<2 '
                                     'WITH ier2, count(i2) as co WHERE co>5 '
                                     'order by co desc return ier2, co limit 10')


if __name__ == '__main__':

    i = Investment()
    i.build_graph()