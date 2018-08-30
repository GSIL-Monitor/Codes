# -*- coding: utf-8 -*-

import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(sys.path[0], '../../../util'))
sys.path.append(os.path.join(sys.path[0], '../../support'))
import loghelper
import db
import email_helper

sys.path.append(os.path.join(sys.path[0], '../util'))
# import helper
import pandas as pd
import simhash, datetime
import util, oss2_helper

sys.path.append(os.path.join(sys.path[0], '../export'))
import export_util

# logger
loghelper.init_logger("digitalToken_market_export", stream=True)
logger = loghelper.get_logger("digitalToken_market_export")

DATE = None


def run_week():
    mongo = db.connect_mongo()
    conn = db.connect_torndb()

    import pandas as pd
    sql = '''select dt.name,symbol,m.digitalTokenId  from digital_token_market m join digital_token dt on dt.id=m.digitalTokenId  order by circulationMarketValue desc limit 100'''
    result = conn.query(sql)
    dtids = [i['digitalTokenId'] for i in result]
    df1 = pd.DataFrame(result)

    collectionfxhmarket = mongo.raw.feixiaohao_market
    datebefore = datetime.datetime.now() + datetime.timedelta(days=-8)
    result = list(
        collectionfxhmarket.find({'digitalTokenId': {'$in': dtids}, 'date': {'$gte': datebefore}}, {'_id': 0}))
    df2 = pd.DataFrame(result)

    df3 = pd.merge(df1, df2, on='digitalTokenId', how='outer')

    fileName = 'digitalToken_market_export.xlsx'
    df3.to_excel(fileName, index=0)

    content = '''<div>Dears,    <br /><br />

    附件是上周的用户搜索记录，搜索量前10的机构为：
    </div>
    '''
    content = 'Automatically generated'

    # send_mail_file(from_alias, reply_alias, reply_email, to, subject, content, file)
    recieveList = ['zhlong', 'songyaodong']
    # recieveList = ['zhlong']

    path = os.path.join(sys.path[0], fileName)
    email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "noreply@xiniudata.com",
                                ';'.join([i + '@xiniudata.com' for i in recieveList]),
                                "虚拟币周报 (%s ~ 至今)" % (datebefore.strftime('%Y-%m-%d')),
                                content, path)

    mongo.close()
    conn.close()


if __name__ == "__main__":
    global DATE
    while True:
        dt = datetime.datetime.now()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE and dt.weekday() == 0:
            run_week()
            DATE = datestr
        time.sleep(60 * 60 * 6)
