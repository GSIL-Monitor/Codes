# -*- coding: utf-8 -*-

import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(sys.path[0], '../../../util'))
sys.path.append(os.path.join(sys.path[0], '../../support'))
import loghelper
import db

sys.path.append(os.path.join(sys.path[0], '../util'))
# import helper
import pandas as pd
import simhash, datetime
import export_util

# logger
loghelper.init_logger("yitai_excel", stream=True)
logger = loghelper.get_logger("yitai_excel")

conn = db.connect_torndb()
mongo = db.connect_mongo()


def yitai_excel(filename):
    import pandas as pd
    df = pd.read_excel(filename)

    df.projectName = df.apply(lambda x: str(x.projectName).strip().replace("(", "（").replace(")", "）").replace(" ", ""),
                              axis=1)
    df.companyname = df.apply(lambda x: str(x.companyname).strip().replace("(", "（").replace(")", "）").replace(" ", ""),
                              axis=1)

    def find_companyid(row):
        companyId = export_util.find_companies_by_full_name_corporate([row.companyname])
        if len(companyId) > 0:
            return companyId[0]
        else:
            return export_util.find_reference([row.projectName])

    df['companyId'] = df.apply(find_companyid, axis=1)

    companyId = list(df[pd.notnull(df.companyId)].companyId)

    results = conn.query('''select c.id companyId,c.corporateId,c.code,c.name xiniuName,c.active
                            from company c 
                            where c.id in %s
                            ''', companyId)

    df2 = pd.DataFrame(results)
    df3 = pd.merge(df, df2, on='companyId', how='left')

    df3['verify'] = df3.apply(lambda x: export_util.getinfo_lite(x.companyId, x.corporateId), axis=1)
    df3 = export_util.illegal_df(df3)
    df3.to_excel('export.xlsx', index=0)


if __name__ == '__main__':
    yitai_excel(u'去脏版合并.xlsx')
