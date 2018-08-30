# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_message_negative", stream=True)
logger = loghelper.get_logger("patch_message_negative")


conn = db.connect_torndb()
mongo = db.connect_mongo()


def main():
    items = conn.query("select id from company_message where negative='Y' and active='Y'")
    for item in items:
        logger.info(item)
        mongo.message.user_message2.update_many({"companyMessageId": item["id"]},{"$set":{"negative":"Y"}})
        # exit()


if __name__ == "__main__":
    main()