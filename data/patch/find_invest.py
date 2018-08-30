# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("find_invest", stream=True)
logger = loghelper.get_logger("find_invest")

conn = db.connect_torndb()
mongo = db.connect_mongo()


def main(investor_id):
    investors = conn.query("select * from investor_alias "
                           "where investorId=3888 and type=12010 and "
                           "investorId=%s and (active is null or active='Y')",
                           investor_id)
    names = [u"孙军军"]
    # for investor in investors:
    #     name = investor["name"].strip()
    #     names.append(name)
    #     if u"（" in name:
    #         names.append(name.replace(u"（","(").replace(u"）",")"))

    for name in names:
        logger.info("%s", name)
        items = mongo.info.gongshang.find({"investors.name": name})
        for item in items:
            full_name = item["name"].strip()
            logger.info("   %s", full_name)
            companies = conn.query("select * from corporate cp join company c on c.corporateId=cp.id "
                                   "where (cp.active is null or cp.active='Y') and (c.active is null or c.active='Y') and "
                                   "cp.fullName=%s", full_name)
            for company in companies:
                logger.info("       %s, %s",company["code"], company["name"])


if __name__ == "__main__":
    main(3888)