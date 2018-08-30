# -*- coding: utf-8 -*-
import os, sys
import datetime
import xlrd
import traceback
import re
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("ether", stream=True)
logger = loghelper.get_logger("ether")


def main():
    investors = {}
    data = xlrd.open_workbook("files/ether_limited.xlsx")
    table = data.sheets()[0]
    nrows = table.nrows
    for i in range(1, nrows):
        row = table.row_values(i)
        name = row[0].strip()
        gongshang = row[1].strip()
        if investors.has_key(name):
            investors[name].append(gongshang)
        else:
            investors[name] = [gongshang]

    logger.info("cnt: %s", len(investors.keys()))
    for key, gongshangs in investors.items():
        names = key.split("/")
        flag = False
        for name in names:
            flag = find_investor(name)
            if flag is True:
                break
        if flag is False:
            logger.info("%s, %s", key, len(gongshangs))


def find_investor(name):
    item = conn.get("select * from investor where name=%s and (active is null or active='Y')", name)
    if item is not None:
        return True
    item = conn.get("select * from investor_alias a join investor i on a.investorId=i.id "
                    "where a.name=%s and (a.active is null or a.active='Y') "
                    "and (i.active is null or i.active='Y') limit 1", name)
    if item is not None:
        return True

    return False


if __name__ == "__main__":
    conn = db.connect_torndb()
    main()