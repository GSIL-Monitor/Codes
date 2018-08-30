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
from common.algorithm import all_chinese

import codecs
from datetime import datetime
from neo4j.v1 import GraphDatabase, basic_auth
from pymongo.errors import OperationFailure


class InvestmentGraph(object):

    def __init__(self):

        self.neo4j = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "rhino@309"))
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

    def build_graph(self):

        session = self.neo4j.session()

        self.build_fund_organization(session)

        # yuanmas = [a[1] for a in dbutil.get_investor_gongshang_with_ids(self.db, 479)]
        # self.build_gongshang_extend(session, [u'西藏源代码股权投资合伙企业（有限合伙）'])

        # self.build_gongshang(session)

    def build_fund_organization(self, session):

        for iid, alias in dbutil.get_investor_gongshang_with_ids(self.db, *dbutil.get_famous_investors(self.db)):
            gs = self.mongo.info.gongshang.find_one({'name': alias})
            if not gs:
                continue
            self.__merge_gongshang(gs, session)
            self.__merge_investor(iid, alias, session)

    def build_gongshang(self, session):

        insys = self.db.query('select alias.name name from corporate_alias alias, company c '
                              'where alias.corporateId=c.corporateId and (c.active is null or c.active="Y") '
                              'and alias.type=12010 and (alias.active is null or alias.active="Y") '
                              'and c.establishDate>"2008-01-01";')
        insys = [a.name for a in insys]
        done = False
        skip = 75766
        while not done:
            cursor = self.mongo.info.gongshang.find({'name': {'$in': insys}})
            cursor.sort("_id")
            cursor.skip(skip)
            print 'lost in ', skip, datetime.now()
            try:
                for gs in cursor:
                    if skip % 10000 == 0:
                        print 'skip, ', skip, datetime.now()
                    skip += 1
                    try:
                        self.__merge_gongshang(gs, session)
                    except Exception, e:
                        print gs
                        print e
                done = True
            except OperationFailure, e:
                msg = e.message
                if not (msg.startswith("cursor id") and msg.endswith("not valid at server")):
                    raise

    def build_gongshang_extend(self, session, init_gss):

        iteration, extended, processed = 0, set(), set()
        extended.update(init_gss)
        while len(extended) > 0 and iteration < 100:
            print iteration, len(extended)
            processed.update(extended)
            for gse in list(self.mongo.info.gongshang.find({'name': {'$in': list(extended)}})):
                extended.update(self.__merge_gongshang(gse, session))
            extended = extended - processed

    def __merge_investor(self, iid, gs_name, session):

        try:
            i_name = dbutil.get_investor_name(self.db, iid)
            session.run('MERGE (gsc:GongShangCompany {name: {gsc_name}}) '
                        'MERGE (investor: Investor {name: {i_name}}) '
                        'MERGE (investor) -[:distribute]-> (gsc) '
                        'RETURN investor', {'gsc_name': gs_name, 'i_name': i_name})
        except Exception, e:
            print iid, gs_name

    def __merge_gongshang(self, gs, session):

        for share_holder in gs.get('investors', []):
            if (not share_holder.get('name', '0')) or (not all_chinese(share_holder.get('name', '0'))):
                continue
            if len(share_holder.get('name')) > 3:
                session.run('MERGE (gsc:GongShangCompany {name: {gsc_name}}) '
                            ' ON CREATE SET '
                            '  gsc.established = {gsc_establish}, '
                            '  gsc.base = {gsc_base}, '
                            '  gsc.status = {gsc_status} '
                            'MERGE (sh:GongShangCompany {name: {sh_name}}) '
                            'MERGE (gsc) -[:hasShareHolder]-> (sh) '
                            'RETURN gsc, sh',
                            {'gsc_name': gs['name'], 'sh_name': share_holder.get('name'),
                             'gsc_establish': gs.get('establishTime').year if gs.get('establishTime') else 0,
                             'gsc_base': gs.get('base'), 'gsc_status': gs.get('regStatus')})
            else:
                session.run('MERGE (gsc:GongShangCompany {name: {gsc_name}}) '
                            ' ON CREATE SET '
                            '  gsc.established = {gsc_establish}, '
                            '  gsc.base = {gsc_base}, '
                            '  gsc.status = {gsc_status} '
                            'MERGE (p:Person {name: {p_name}}) '
                            'MERGE (gsc) -[:hasShareHolder]-> (p) '
                            'RETURN gsc, p',
                            {'gsc_name': gs['name'], 'p_name': share_holder.get('name'),
                             'gsc_establish': gs.get('establishTime').year if gs.get('establishTime') else 0,
                             'gsc_base': gs.get('base'), 'gsc_status': gs.get('regStatus')})
        return [sh.get('name') for sh in gs.get('investors', [])]
        # return [sh.get('name') for sh in gs.get('investors', [])] + [sh.get('name') for sh in gs.get('invests', [])]

    def find_relevant(self):

        session = self.neo4j.session()
        query = 'MATCH (iv:Investor {name: "源码资本"}) -[:distribute]-> (distributor: GongShangCompany), ' \
                'path=(distributor) -[:hasShareHolder*1..2]- (sh) ' \
                'where sh.name contains "投资" or sh:Person optional match (another: Investor) -[:distribute]-> (sh) ' \
                'return sh, distributor, iv, path, another'

    def get_shareholder(self):

        mongo = dbcon.connect_mongo()
        majias = [line.strip() for line in codecs.open('files/yuanma.log', encoding='utf-8')]
        with codecs.open('files/yuanma.lp', 'w', 'utf-8') as fo:
            for majia in majias:
                investors = mongo.info.gongshang.find_one({'name': majia}).get('investors', [])
                investors = [investor.get('name') for investor in investors]
                fo.write('%s\t%s\n' % (majia, ','.join(investors)))

if __name__ == '__main__':

    ig = InvestmentGraph()
    ig.get_shareholder()
    # ig.build_graph()