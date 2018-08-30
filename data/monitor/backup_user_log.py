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
    d = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    while True:
        items = mongo.log.user_log.find().sort("_id", 1).limit(1000)
        for item in items:
            _id = item["_id"]
            gen_time = _id.generation_time.replace(tzinfo=None)
            # logger.info("gen time: %s", gen_time)
            if gen_time < d:
                mongo.log.user_log_backup.insert_one(item)
                mongo.log.user_log.remove({"_id": _id})
                exit()
            else:
                break


if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)