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
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("ether", stream=True)
logger = loghelper.get_logger("ether")


def main():
    investors = {}
    investors_cnt = {}
    limited = {}
    data = xlrd.open_workbook("files/ether_2016_funding1.xlsx")
    table = data.sheets()[0]
    nrows = table.nrows
    for i in range(1, nrows):
        row = table.row_values(i)
        try:
            if int(row[4]) != 1:
                continue
        except:
            continue
        name = row[10].strip()
        name1 = row[11].strip()
        name2 = row[12].strip()
        # logger.info("%s, %s, %s", name, name1, name2)
        if name != "":
            tmp = name.split("/")
            name = tmp[0]
            if not investors.has_key(name):
                investors[name] = {}
                investors_cnt[name] = 1
            else:
                investors_cnt[name] += 1
            if name1 != "" and name1 != name:
                if not investors[name].has_key(name1):
                    investors[name][name1] = 1

        if name2 != "":
            if not limited.has_key(name2):
                limited[name2] = {}

    logger.info("investors cnt: %s", len(investors.keys()))
    logger.info("limited cnt: %s", len(limited.keys()))

    for key, values in investors.items():
        found = False
        names = [key]
        for name, value in values.items():
            names.append(name)

        for name in names:
            flag = find_investor(name)
            if flag:
                found = True
                break

        if found is False:
            logger.info("%s, %s", investors_cnt[key], ",".join(names))

    # logger.info("-----------")
    #
    # for name, values in limited.items():
    #     flag = find_investor(name)
    #     if flag is False:
    #         logger.info(name)


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