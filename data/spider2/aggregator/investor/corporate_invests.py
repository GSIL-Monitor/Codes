# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import datetime, time
import json, re, copy
#可能是corporate 对外投资情况的程序

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, config
import db, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

# logger
loghelper.init_logger("corporate_invests", stream=True)
logger = loghelper.get_logger("corporate_invests")


def stat():
    sql = '''select co.fullName,c.name,c.code,c.corporateid
    from corporate co join company c
    on c.corporateid=co.id
    where (co.active='Y' or co.active is null)
    and  (c.active='Y' or c.active is null)
    '''
    conn = db.connect_torndb()
    results = conn.query(sql)
    conn.close()
    fullnames = [i['fullName'] for i in results]

    mongo = db.connect_mongo()
    import pandas as pd
    df1 = pd.DataFrame(results)
    df2 = pd.DataFrame(list(mongo.info.gongshang.find({'name': {'$in': fullnames}}, {'name': 1, 'invests': 1})))
    df2['cnt'] = df2.apply(lambda x: len(x.invests) if isinstance(x.invests, list) else 0, axis=1)
    df2['investsName'] = df2.apply(
        lambda x: ','.join([i['name'] for i in x.invests]) if isinstance(x.invests, list) else '', axis=1)

    dfMerge = pd.merge(df1, df2, left_on='fullName', right_on='name')
    dfMerge = dfMerge[dfMerge.cnt > 0]

    sql = '''select ca.name
    from corporate_alias ca join corporate co
    on co.id=ca.corporateid
    where (co.active!='N' or co.active is null)
    and (ca.active='Y' or ca.active is null)
    and ca.type=12010
    '''
    corporateAliases = [i['name'] for i in conn.query(sql)]

    def investsName2(x):
        if isinstance(x.invests, list):
            investsName = [i['name'] for i in x['invests']]
            sql = '''select ca.name
            from corporate_alias ca join corporate co
            on co.id=ca.corporateid
            where 
            co.id=%s and
            (co.active='Y' or co.active is null)
            and (ca.active='Y' or ca.active is null)
            and ca.type=12010
            '''
            thisCorporateAliases = [i['name'] for i in conn.query(sql, x['corporateid'])]
            existName = [i for i in investsName if i in corporateAliases and i not in thisCorporateAliases]
            return existName
        else:
            return []

    dfMerge['investsName2'] = dfMerge.apply(investsName2, axis=1)
    dfMerge['cnt2'] = dfMerge.apply(lambda x: len(x.investsName2) if isinstance(x.investsName2, list) else 0, axis=1)
    dfMerge['investsName2desc'] = dfMerge.apply(lambda x: ','.join(x.investsName2), axis=1)

    for c in dfMerge.columns:
        def illegal(row):
            import re
            content = row[c]
            if content is not None:
                ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
                try:
                    content = ILLEGAL_CHARACTERS_RE.sub(r'', content)
                except:
                    pass
            return content

        # print 'c:',c
        dfMerge[c] = dfMerge.apply(illegal, axis=1)

    dfMerge = dfMerge.drop(['_id'], axis=1)
    # dfMerge[dfMerge.cnt > 0].to_excel('export.xlsx', index=0)

    dfMerge.to_excel('export.xlsx', index=0)
