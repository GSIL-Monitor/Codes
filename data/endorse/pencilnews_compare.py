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
loghelper.init_logger("pencilnews_compare", stream=True)
logger = loghelper.get_logger("pencilnews_compare")

conn = db.connect_torndb()


def process(table):

    nrows = table.nrows
    for i in range(0, nrows):
        if i == 0:
            continue
        row = table.row_values(i)
        try:
            name = row[0].strip()
            fullname = row[1].strip().replace("(", u"（").replace(")",u"）")
            # logger.info("%s, %s", name, fullname)
            if check(i, name, fullname) is False:
                logger.info("line: %s, name: %s, fullname: %s", i, name, fullname)
        except:
            traceback.print_exc()
            pass
        # logger.info("")


def check(i, name, fullname):
    if fullname != "":
        corps = find_corporate(fullname)
        if len(corps) == 0:
            return False
        return True
    else:
        companies = find_company(name)
        if len(companies) == 0:
            return False
        return True


def find_corporate(fullname):
    corps = conn.query("select * from corporate cp join company c on c.corporateId=cp.id "
                       "where (cp.active is null or cp.active='Y') "
                       "and (c.active is null or c.active='Y')"
                       "and cp.fullname=%s", fullname)
    if len(corps)>0:
        return corps;
    corps = conn.query("select cp.* from corporate_alias a join corporate cp on a.corporateId=cp.id "
                       "join company c on c.corporateId=cp.id "
                      " where (cp.active is null or cp.active='Y') and "
                      "(a.active is null or a.active='Y') and "
                      "(c.active is null or c.active='Y') and "
                      "a.name=%s", fullname)
    return corps


def find_company(name):
    companyies = conn.query("select * from company where"
                            " (active is null or active='Y') and"
                            " name=%s", name)
    if len(companyies) > 0:
        return companyies
    companyies = conn.query("select * from company c join company_alias a on c.id=a.companyId"
                            " where"
                            " (a.active is null or a.active='Y') and"
                            " (c.active is null or c.active='Y') and"
                            " a.name=%s", name)
    return companyies


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "usage: python pencilnews_compare.py <filename>"
        exit()
    filename = sys.argv[1]
    data = xlrd.open_workbook(filename)
    process(data.sheets()[0])