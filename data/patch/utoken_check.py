# -*- coding: utf-8 -*-
import os, sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_ether_fa", stream=True)
logger = loghelper.get_logger("patch_ether_fa")


def main():
    utokens = {}

    mongo = db.connect_mongo()
    items = list(mongo.xiniudata.user_cookie.find({"type":"utoken", "active":'Y'}))
    for item in items:
        userCookie = item["userCookie"]
        utokenUserId = item["utokenUserId"]
        if utokens.has_key(userCookie):
            logger.info(userCookie)
        else:
            utokens[userCookie] = 1


if __name__ == "__main__":
    main()
