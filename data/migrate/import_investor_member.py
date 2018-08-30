# -*- coding: utf-8 -*-
import os, sys
import md5
import json
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("import_investor_member", stream=True)
logger = loghelper.get_logger("import_investor_member")


mongo = db.connect_mongo()


def get_md5_str(data):
    m = md5.new()
    m.update(data)
    return m.hexdigest()


def main():
    f = open("investor_member.txt")

    i = 0
    for line in f:
        i += 1
        if i % 3 != 2:
            continue
        data = line.strip()
        url = "http://vip.api.qimingpian.com/d/person"
        data_md5 = get_md5_str(data)
        data_json = json.loads(data, "utf8")

        item = mongo.raw.qmp.find_one({"datamd5": data_md5})
        if item is None:
            logger.info(data)
            result = {
                "url": url,
                "postdata": {},
                "data": data_json,
                "createTime": datetime.datetime.utcnow(),
                "datamd5": data_md5,
            }
            mongo.raw.qmp.insert_one(result)
            # break

    f.close()


if __name__ == '__main__':
    main()