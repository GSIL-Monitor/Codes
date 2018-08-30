# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
from bson.objectid import ObjectId
import json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
import config
import image_helper
import url_helper
#logger
loghelper.init_logger("report_export", stream=True)
logger = loghelper.get_logger("report_export")

#parse data from qimingpian directly, bamy called it step 1 to checkout company

typemap = {
    78001: "行业研报",
    78002: "A股招股书",
    78003: "新三板招股书"
}


if __name__ == '__main__':
    logger.info("Begin...")
    # noo = 0
    conn = db.connect_torndb()
    fp2 = open("report.txt", "w")
    while True:
        (num0, num1, num2, num3, num4, num5, num6, num7) = (0, 0, 0, 0, 0, 0, 0, 0)
        mongo = db.connect_mongo()
        collection = mongo.article.report

        while True:
            # items = list(collection.find({"_id" : ObjectId("5ab855c51045403176b867a4")}).limit(100))
            items = list(collection.find({}))
            logger.info("items : %s", len(items))
            n = 0
            for item in items:
                n+=1
                title = item["title"]
                link = "http://www.xiniudata.com/file/report/%s/%s" % (item["fileid"], item["filename"])
                type = typemap[item["type"]]
                pdfCreationDate = item["pdfCreationDate"]

                line = "%s<<<%s<<<%s<<<%s<<<%s\n" % (n, title, pdfCreationDate, type, link)
                fp2.write(line)
            break
            # if len(items) == 0:
            #     break


        # break
        logger.info("%s - %s - %s - %s - %s - %s - %s - %s", num0, num1, num2, num3, num4, num5, num6, num7)
        fp2.close()
        mongo.close()
        conn.close()
        # time.sleep(10*60)
        break
