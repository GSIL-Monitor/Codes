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
import util, oss2_helper

sys.path.append(os.path.join(sys.path[0], '../export'))
import export_util

sys.path.append(os.path.join(sys.path[0], '../../api/api/data'))
import data_code

# logger
loghelper.init_logger("flasky_funding_export", stream=True)
logger = loghelper.get_logger("flasky_funding_export")

conn = db.connect_torndb_proxy()
mongo = db.connect_mongo()


def run():
    collection = mongo.task.data_report

    while True:
        items = collection.find({'processStatus': 0}).limit(10)

        for item in items:
            try:
                startDate, endDate = item['param']['startDate'], item['param']['endDate']
                logger.info('processing %s ~ %s.xlsx' % (startDate, endDate))
                df, columns = data_code.run2(conn, mongo, startDate=startDate, endDate=endDate,param=item['param'])
                df.to_excel('test.xlsx', index=0, columns=columns, encoding="utf-8")
                path = os.path.join(sys.path[0], 'test.xlsx')

                fileid = util.get_uuid()

                oss = oss2_helper.Oss2Helper("xiniudata-report")
                fp = file(path, "rb")
                oss.put(fileid, fp, headers={"Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                             "x-oss-meta-filename": 'funding_news_report_%s~%s.xlsx' % (startDate, endDate)})
                fp.close()

                logger.info('uploaded funding_news_report_%s ~ %s.xlsx' % (startDate, endDate))
                collection.update_one({'_id': item['_id']},
                                      {'$set': {'processStatus': 1, 'link': 'http://www.xiniudata.com/file/report/%s' % fileid}})
            except Exception as e:
                logger.info(e)

        logger.info('sleep')
        time.sleep(30)



if __name__ == '__main__':
    logger.info('start')
    run()
