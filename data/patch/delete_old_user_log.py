# -*- coding: utf-8 -*-
import os, sys
import datetime, time
from bson import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("delete_old_user_log", stream=True)
logger = loghelper.get_logger("delete_old_user_log")

mongo = db.connect_mongo()


def main():
    cnt = 0
    d = datetime.datetime.strptime("2018-03-01", "%Y-%m-%d")
    while True:
        items = mongo.log.user_log.find().sort("_id",1).limit(1000)
        cnt += 1000
        logger.info("cnt: %s", cnt)
        for item in items:
            _id = item["_id"]
            gen_time = _id.generation_time.replace(tzinfo=None)
            # logger.info("gen time: %s", gen_time)
            if gen_time < d:
                mongo.log.user_log.remove({"_id": _id})
            else:
                exit()



if __name__ == "__main__":
    main()