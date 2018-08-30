# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("migrate_fa_id", stream=True)
logger = loghelper.get_logger("migrate_fa_id")


rules = {
    13100: 1,
    13101: 2,
    13102: 3,
    13103: 4,
    13104: 5,
    13105: 6,
    13800: 7
}

def process_funding():
    conn = db.connect_torndb()
    for key, value in rules.items():
        conn.update("update funding set faId=%s where fa=%s", value, key)
    conn.close()


def process_company_fa():
    conn = db.connect_torndb()
    for key, value in rules.items():
        conn.update("update company_fa set faId=%s where source=%s", value, key)
    conn.close()


def process_fa_advisor():
    conn = db.connect_torndb()
    for key, value in rules.items():
        conn.update("update fa_advisor set faId=%s where source=%s", value, key)
    conn.close()


if __name__ == '__main__':
    process_funding()
    process_company_fa()
    process_fa_advisor()


