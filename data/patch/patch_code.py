# -*- coding: utf-8 -*-
import os, sys
import hashlib
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_code", stream=True)
logger = loghelper.get_logger("patch_code")

conn = db.connect_torndb()

def gen_code(_id, name, create_time):
    data = "%s%s%s" % (_id, name, create_time)
    logger.info(data)
    code = hashlib.md5(data).hexdigest()
    return code


def investor():
    _id = 0
    while True:
        items = conn.query("select * from investor where id>%s order by id limit 100", _id)
        if len(items) == 0:
            break

        for item in items:
            _id = item["id"]
            if item["code"] is not None and item["code"].strip() != "":
                continue
            name = item["name"]
            create_time = item["createTime"]
            code = gen_code(_id, name, create_time)
            logger.info(code)
            conn.update("update investor set code=%s where id=%s", code, _id)
        # break


def topic():
    _id = 0
    while True:
        items = conn.query("select * from topic where id>%s order by id limit 100", _id)
        if len(items) == 0:
            break

        for item in items:
            _id = item["id"]
            if item["code"] is not None and item["code"].strip() != "":
                continue
            name = item["name"]
            create_time = item["createTime"]
            code = gen_code(_id, name, create_time)
            logger.info(code)
            conn.update("update topic set code=%s where id=%s", code, _id)
        # break

def industry():
    _id = 0
    while True:
        items = conn.query("select * from industry where id>%s order by id limit 100", _id)
        if len(items) == 0:
            break

        for item in items:
            _id = item["id"]
            if item["code"] is not None and item["code"].strip() != "":
                continue
            name = item["name"]
            create_time = item["createTime"]
            code = gen_code(_id, name, create_time)
            logger.info(code)
            conn.update("update industry set code=%s where id=%s", code, _id)
        # break


if __name__ == "__main__":
    investor()
    topic()
    industry()