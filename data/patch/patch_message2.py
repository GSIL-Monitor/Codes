# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_message2", stream=True)
logger = loghelper.get_logger("patch_message2")


conn = db.connect_torndb()
mongo = db.connect_mongo()


def main():
    items = mongo.message.user_message2.find({"type":5030, "trackDimension":8001})
    for item in items:
        if item["detailId"] is None:
            company_fa_id = item["relateId"]
            company_fa = conn.get("select * from company_fa where id=%s", company_fa_id)
            if company_fa is not None:
                company_id = company_fa["companyId"]
                mongo.message.user_message2.update_one({"_id": item["_id"]},{"$set":{"detailId": str(company_id)}})


if __name__ == "__main__":
    main()