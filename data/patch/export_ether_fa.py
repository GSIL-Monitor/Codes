# -*- coding: utf-8 -*-
import os, sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("export_ether_fa", stream=True)
logger = loghelper.get_logger("export_ether_fa")


def main():
    mongo = db.connect_mongo()
    items = mongo.fa.ether.find({"createTime":{"$gt":datetime.datetime.strptime("2017-08-01", '%Y-%m-%d')}, "publishDate":{"$ne":0}}).sort("createTime",1)
    mongo.close()
    for item in items:
        logger.info("|%s|%s|%s|%s|%s",
                    #item["createTime"].split(" ")[0],
                    #item["publishDate"].split(" ")[0],
                    datetime.datetime.strftime(item["createTime"], '%Y/%m/%d'),
                    datetime.datetime.strftime(item["publishDate"], '%Y/%m/%d'),
                    item["name"], item["fullName"], item["abstract"])

if __name__ == "__main__":
    main()
