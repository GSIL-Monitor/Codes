# -*- coding: utf-8 -*-
import os, sys
import xlrd

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("import_hyfl", stream=True)
logger = loghelper.get_logger("import_hyfl")

conn = db.connect_torndb()

def glfl():
    TYPE = 73010
    # 管理分类
    data = xlrd.open_workbook("hy/glhy.xlsx")
    table = data.sheets()[0]
    nrows = table.nrows

    l1Id = None
    l2Id = None
    l3Id = None
    l4Id = None
    for i in range(2, nrows):
        row = table.row_values(i)
        l1 = row[0]
        l2 = row[1]
        l3 = row[2]
        l4 = row[3]
        name = row[4].strip()
        desc = row[5].strip()

        if l1 != "" and l2 == "" and l3 == "" and l4 == "":
            logger.info("level1. %s, name: %s", l1, name)
            l1Id = save(TYPE, 1, None, l1, name)
        elif l1 == "" and l2 != "" and l3 == "" and l4 == "":
            logger.info("level2. %s, name: %s", l2, name)
            l2Id = save(TYPE, 2, l1Id, l2, name)
        elif l1 == "" and l2 == "" and l3 != "" and l4 == "":
            logger.info("level3. %s, name: %s", l3, name)
            l3Id = save(TYPE, 3, l2Id, l3, name)
        elif l1 == "" and l2 == "" and l3 == "" and l4 != "":
            logger.info("level4. %s, name: %s", l4, name)
            l4Id = save(TYPE, 4, l3Id, l4, name)
        elif l1 == "" and l2 == "" and l3 != "" and l4 != "":
            logger.info("level3: %s, level4. %s, name: %s", l3, l4, name)
            l3Id = save(TYPE, 3, l2Id, l3, name)
            l4Id = save(TYPE, 4, l3Id, l4, name)
        elif l1 != "" and l2 != "" and l3 != "" and l4 != "":
            logger.info("level1: %s, level2: %s, level3: %s, level4. %s, name: %s", l1, l2, l3, l4, name)
            l1Id = save(TYPE, 1, None, l1, name)
            l2Id = save(TYPE, 2, l1Id, l2, name)
            l3Id = save(TYPE, 3, l2Id, l3, name)
            l4Id = save(TYPE, 4, l3Id, l4, name)
        else:
            logger.info("Wrong!!!!!!!! l1: %s, l2: %s, l3: %s, l4: %s, name: %s", l1, l2, l3, l4, name)

def tzfl():
    # 投资分类
    TYPE = 73020
    # 管理分类
    data = xlrd.open_workbook("hy/tzhy.xlsx")
    table = data.sheets()[0]
    nrows = table.nrows

    l1Id = None
    l2Id = None
    l3Id = None
    l4Id = None
    for i in range(2, nrows):
        row = table.row_values(i)
        l1 = row[0]
        l1_name = row[1].strip()
        l2 = row[2]
        l2_name = row[3].strip()
        l3 = row[4]
        l3_name = row[5].strip()
        l4 = row[6]
        l4_name = row[7].strip()

        logger.info("level1: %s, level2: %s, level3: %s, level4. %s", l1, l2, l3, l4)
        if l1 != "":
            l1Id = save(TYPE, 1, None, l1, l1_name)
        if l2 != "":
            l2Id = save(TYPE, 2, l1Id, l2, l2_name)
        if l3 != "":
            l3Id = save(TYPE, 3, l2Id, l3, l3_name)
        if l4 != "":
            l4Id = save(TYPE, 4, l3Id, l4, l4_name)


def save(type, level, fId, code, name):
    item = conn.get("select * from hyfl where type=%s and code=%s and level=%s", type, code, level)
    if item is None:
        _id = conn.insert("insert hyfl(type,level,fId,code,name,createTime,modifyTime) values("
                          "%s, %s, %s, %s, %s, now(),now())",
                          type, level, fId, code, name)
    else:
        _id = item["id"]
    return _id


def xsb(filename):
    data = xlrd.open_workbook(filename)
    gl_table = data.sheets()[0]
    xsb1(gl_table, 73010)

    tz_table = data.sheets()[1]
    xsb1(tz_table, 73020)


def xsb1(table, hy_type):
    nrows = table.nrows
    for i in range(4, nrows):
        row = table.row_values(i)
        stock_symbol = str(int(row[0]))
        l1 = row[2]
        if type(row[2]) == int or type(row[2]) == float:
            l1 = str(int(l1))
        l2 = str(int(row[4]))
        l3 = str(int(row[6]))
        l4 = str(int(row[8]))
        logger.info("%s, %s, %s, %s, %s", stock_symbol, l1, l2, l3, l4)
        save_stock_hyfl(hy_type, stock_symbol, l1, 1)
        save_stock_hyfl(hy_type, stock_symbol, l2, 2)
        save_stock_hyfl(hy_type, stock_symbol, l3, 3)
        save_stock_hyfl(hy_type, stock_symbol, l4, 4)


def save_stock_hyfl(hy_type, stock_symbol, hyfl_code, level):
    fl = conn.get("select * from hyfl where type=%s and code=%s and level=%s", hy_type, hyfl_code, level)
    if fl is None:
        logger.info("Can't find code %s", hyfl_code)
        exit()
    save_stock_hyfl1(stock_symbol, fl["id"])


def save_stock_hyfl1(stock_symbol, hyfl_id):
    item = conn.get("select * from stock_hyfl where stockSymbol=%s and hyflId=%s",
                    stock_symbol, hyfl_id)
    if item is None:
        conn.insert("insert stock_hyfl(stockSymbol, hyflId, createTime, modifyTime) values("
                    "%s, %s, now(),now())",
                    stock_symbol, hyfl_id)
        pass


def zhuban(filename):
    data = xlrd.open_workbook(filename)
    for i in range(len(data.sheets())):
        table = data.sheets()[i]
        zhuban1(table)


def zhuban1(table):
    nrows = table.nrows
    for i in range(0, nrows):
        row = table.row_values(i)
        _hy_code = row[2].strip()
        if len(_hy_code)>2:
            continue
        if len(_hy_code) != 0:
            hy_code = _hy_code
        stock_symbol = row[4].strip()
        logger.info("%s -> %s", stock_symbol, hy_code)
        l2 = conn.get("select * from hyfl where type=73010 and code=%s and level=2", hy_code)
        if l2 is None:
            logger.info("Can't find code %s!", hy_code)
            exit()
        l1 = conn.get("select * from hyfl where id=%s and level=1", l2["fId"])

        save_stock_hyfl1(stock_symbol, l1["id"])
        save_stock_hyfl1(stock_symbol, l2["id"])


if __name__ == '__main__':
    # glfl()
    # tzfl()
    # xsb("hy/xsb_fl_201710.xlsx")
    zhuban("hy/zhuban_fl_201710.xlsx")
