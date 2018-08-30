# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("migrate_user_datagroup", stream=True)
logger = loghelper.get_logger("migrate_user_datagroup")

conn = db.connect_torndb()
mongo = db.connect_mongo()

user_ids = [
    214,
    215,
    219,
    220,
    221,
    222,
    223,
    224,
    225,
    875,
    1091,
    2706,
    3142,
    3341,
    3477,
    4831,
    6868,
    6936,
    7176,
    7765,
    8986,
    9172,
    9173,
    9255,
    10031,
    10159,
    10424,
    10459,
    10460,
    10481,
    10826,
]


def main():
    for user_id in user_ids:
        user_mongo = mongo["open-maintain"].user.find_one({"userId": user_id})
        if user_mongo is None:
            logger.info("userId: %s", user_id)
            user = conn.get("select * from user where id=%s", user_id)
            user_mongo = {
                "password": user["password"],
                "admin": "N",
                "active": "Y",
                "userId": int(user_id),
                "email": user["email"],
                "orgId": 1,
                "username": user["username"]
            }
            mongo["open-maintain"].user.insert_one(user_mongo)


if __name__ == "__main__":
    main()