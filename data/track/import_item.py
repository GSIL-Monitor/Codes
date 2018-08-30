# -*- coding: utf-8 -*-
import os, sys
import xlrd
import requests
import time, datetime
import traceback
import json
from kafka import (SimpleClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util, config

#logger
loghelper.init_logger("import_item", stream=True)
logger = loghelper.get_logger("import_item")


def init_kafka():
    (url) = config.get_kafka_config()
    kafka = SimpleClient(url)
    kafka_producer = SimpleProducer(kafka)
    return kafka_producer


def send_message(topic, type, action, _id):
    kafka_producer = init_kafka()
    msg = {"action":action, "id": _id, "type": type}
    while True:
        try:
            kafka_producer.send_messages(topic, json.dumps(msg))
            logger.info(msg)
            break
        except Exception,e :
            logger.exception(e)
            time.sleep(5)
            kafka_producer = init_kafka()


def process(_id):
    conn = db.connect_torndb()
    items = conn.query("select * from track_import where processStatus=83001")
    for item in items:
        try:
            import_items(conn, item)
        except:
            traceback.print_exc()
            conn.update("update track_import set processStatus=%s where id=%s",
                        83002, item["id"])
    conn.close()


def import_items(conn, track_import):
    logger.info("start import %s", track_import["filename"])
    file_id = track_import["fileId"]
    url = "http://www.xiniudata.com/file/" + file_id
    saved_name = "logs/" + util.id_generator(16) + ".xlsx"

    r = requests.get(url)
    with open(saved_name, "wb") as fp:
        fp.write(r.content)

    w = xlrd.open_workbook(saved_name, on_demand=True)
    table = w.sheets()[0]
    nrows = table.nrows
    for i in range(0, nrows):
        if i == 0:
            continue
        row = table.row_values(i)
        try:
            if track_import["type"] == 82001:
                name = None
                if len(row) >= 1:
                    name = row[0].strip()
                full_name = None
                if len(row) >= 2:
                    full_name = row[1].strip()
                if (name is None or name=="") and (full_name is None or full_name==""):
                    continue

                logger.info("import company, name: %s, fullname: %s", name, full_name)
                import_one_project(conn, track_import, name, full_name)
            elif track_import["type"] == 82002:
                if len(row) == 0:
                    continue
                name = row[0].strip()
                if name is None or name == "":
                    continue
                logger.info("import investor, name: %s", name)
                import_one_investor(conn, track_import, name)
        except:
            traceback.print_exc()

    cnt_result = conn.get("select count(*) cnt from track_import_item where trackImportId=%s", track_import["id"])
    found_cnt_result = conn.get("select count(*) cnt from track_import_item where trackImportId=%s and status=84001",
                                track_import["id"])
    dup_cnt_result = conn.get("select count(*) cnt from track_import_item where trackImportId=%s and status=84002",
                                track_import["id"])
    unmatch_cnt_result = conn.get("select count(*) cnt from track_import_item where trackImportId=%s and status>84002",
                                track_import["id"])
    conn.update("update track_import set processStatus=%s, cnt=%s, dupCnt=%s, unMatchCnt=%s, foundCnt=%s "
                "where id=%s",
                83003,
                cnt_result["cnt"],
                dup_cnt_result["cnt"],
                unmatch_cnt_result["cnt"],
                found_cnt_result["cnt"],
                track_import["id"])

    os.remove(saved_name)
    logger.info("end import.")


def import_one_project(conn, track_import, name, full_name):
    cs = None
    company_id = None

    if full_name is not None and full_name != "":
        cs = conn.query("select c.* from company c "
                        "join corporate cp on c.corporateId=cp.id "
                        "where "
                        "(c.active is null or c.active='Y') and "
                        "(cp.active is null or cp.active='Y') and "
                        "cp.fullName=%s",
                        full_name)

        if len(cs) == 0:
            cs = conn.query("select c.* from company c "
                            "join corporate cp on c.corporateId=cp.id "
                            "join corporate_alias a on cp.id=a.corporateId "
                            "where "
                            "(c.active is null or c.active='Y') and "
                            "(cp.active is null or cp.active='Y') and "
                            "(a.active is null or a.active='Y') and "
                            "a.name=%s",
                            full_name)

    if cs is None or len(cs) == 0:
        cs = conn.query("select * from company where (active is null or active='Y') and name=%s", name)
        if len(cs) == 0:
            cs = conn.query("select c.* from company c "
                            "join company_alias a on a.companyId=c.id "
                            "where "
                            "(c.active is null or c.active='Y') and "
                            "(a.active is null or a.active='Y') and "
                            "a.name=%s",
                            name)

    flag = True
    if cs is None or len(cs) == 0:
        status = 84003
        flag = False
    elif len(cs) > 1:
        last_corporate_id = None
        for c in cs:
            corporate_id = c["corporateId"]
            if last_corporate_id is not None and last_corporate_id != corporate_id:
                status = 84003
                flag = False
                break
            else:
                last_corporate_id = corporate_id

    if flag:
        track_group_id = track_import["trackGroupId"]
        for c in cs:
            company_id = c["id"]
            item = conn.get("select * from track_group_item_rel where "
                            "active='Y' and "
                            "trackGroupId=%s and "
                            "companyId=%s "
                            "limit 1",
                            track_group_id, company_id)
            if item is None:
                _id = conn.insert("insert track_group_item_rel(trackGroupId, companyId, active, createUser,createTime, modifyUser, modifyTime) "
                            "values(%s,%s,'Y',%s,now(),%s,now())",
                            track_group_id, company_id, track_import["createUser"], track_import["createUser"])
                # 消息
                send_message("track_conf", "track_group_item_rel", "create", _id)
                status = 84001
            else:
                status = 84002

            logger.info("status: %s, companyId: %s", status, company_id)
            conn.insert("insert track_import_item(trackImportId, name, fullName, status, companyId, active) "
                        "values(%s,%s,%s,%s,%s,'Y')",
                        track_import["id"],
                        name,
                        full_name,
                        status,
                        company_id)
    else:
        conn.insert("insert track_import_item(trackImportId, name, fullName, status, companyId, active) "
                    "values(%s,%s,%s,%s,%s,'Y')",
                    track_import["id"],
                    name,
                    full_name,
                    status,
                    company_id)
        logger.info("status: %s", status)


def import_one_investor(conn, track_import, name):
    investor_id = None

    cs = conn.query("select * from investor where "
                    "(active is null or active='Y') and "
                    "online='Y' and "
                    "name=%s",
                    name)

    if len(cs) == 0:
        cs = conn.query("select distinct i.* from investor i "
                        "join investor_alias a on i.id=a.investorId "
                        "where "
                        "(i.active is null or i.active='Y') and "
                        "i.online='Y' and "
                        "(a.active is null or a.active='Y') and "
                        "a.name=%s",
                        name)

    if cs is None or len(cs) == 0:
        status = 84003
    elif len(cs) > 1:
        status = 84003
    else:
        c = cs[0]
        track_group_id = track_import["trackGroupId"]
        investor_id = c["id"]
        item = conn.get("select * from track_group_item_rel where "
                        "active='Y' and "
                        "trackGroupId=%s and "
                        "investorId=%s "
                        "limit 1",
                        track_group_id, investor_id)
        if item is None:
            _id = conn.insert(
                "insert track_group_item_rel(trackGroupId, investorId, active, createUser,createTime, modifyUser, modifyTime) "
                "values(%s,%s,'Y',%s,now(),%s,now())",
                track_group_id, investor_id, track_import["createUser"], track_import["createUser"])
            # 消息
            send_message("track_conf", "track_group_item_rel", "create", _id)

            status = 84001
        else:
            status = 84002

    conn.insert("insert track_import_item(trackImportId, name, fullName, status, investorId, active) "
                "values(%s,%s,%s,%s,%s,'Y')",
                track_import["id"],
                name,
                None,
                status,
                investor_id)


if __name__ == '__main__':
    # process(0)
    # send_message("track_conf", "track_group_item_rel", "create", 18)
    pass
