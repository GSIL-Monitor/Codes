# -*- coding: utf-8 -*-
import os, sys
import datetime

import track_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("process_track_group_item_rel", stream=True)
logger = loghelper.get_logger("process_track_group_item_rel")


def create(_id):
    logger.info("create start, id=%s", _id)
    conn = db.connect_torndb()
    rel = conn.get("select * from track_group_item_rel where id=%s", _id)
    if rel is None or rel["active"] != 'Y':
        conn.close()
        return

    track_group_id = rel["trackGroupId"]
    company_id = rel["companyId"]
    investor_id = rel["investorId"]

    track_group = conn.get("select * from track_group where id=%s", track_group_id)
    if track_group is None or track_group["active"] != 'Y':
        conn.close()
        return

    messages = track_util.get_messages_by_item(conn, track_group, company_id or investor_id)
    user_ids = track_util.get_track_user_ids_by_track_group(conn, track_group_id)
    conn.close()

    mongo = db.connect_mongo()
    for message in messages:
        for user_id in user_ids:
            track_util.push_message_to_user(mongo, track_group, user_id, message)
    mongo.close()
    logger.info("create end.")


def delete(_id):
    logger.info("delete start, id=%s", _id)
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    # 删除分组某个公司or机构消息
    item = conn.get("select * from track_group_item_rel where id=%s", _id)
    if item is None or item["active"] != 'N':
        conn.close()
        mongo.close()
        return

    track_group_id = item["trackGroupId"]

    if item["companyId"] is not None:
        item_id = item["companyId"]
        mongo.message.user_message2.delete_many({"trackGroupId": track_group_id, "companyId": item_id})
    elif item["investorId"] is not None:
        item_id = item["investorId"]
        mongo.message.user_message2.delete_many({"trackGroupId": track_group_id, "investorId": item_id})
    else:
        conn.close()
        mongo.close()
        return

    track_group = conn.get("select * from track_group where id=%s", track_group_id)
    if track_group is None:
        conn.close()
        mongo.close()
        return

    # 删除-1,-2,-3冗余数据
    messages = track_util.get_messages_by_item(conn, track_group, item_id)
    user_ids = track_util.get_track_user_ids_by_track_group(conn, track_group_id)
    track_util.purge_redundant_user_message(mongo, track_group, user_ids, messages)

    mongo.close()
    conn.close()
    logger.info("delete end.")


if __name__ == '__main__':
    # 测试
    conn = db.connect_torndb()
    dms = conn.query("select st.* from track_sub_type st join track_type t on t.id=st.trackTypeId "
                     "where t.type=82001")
    for dm in dms:
        track_dimension = dm["trackDimension"]
        if track_dimension != 3201:
            continue
        company = conn.get("select c.id,c.code,c.name,m.publishTime, m.message "
                           "from "
                           "company_message m join company c on m.companyId=c.id "
                           "where "
                           "m.active='Y' and "
                           "(c.active is null or c.active='Y') and "
                           "locationId<371 and "
                           "trackDimension=%s "
                           "and c.id not in (select companyId  from track_group_item_rel where trackGroupId=3)"
                           "order by  m.id desc limit 1",
                           track_dimension)
        if company is not None:
            logger.info("trackDimension:%s, companyId: %s", track_dimension, company["id"])
            _id = conn.insert("insert track_group_item_rel(trackGroupId, companyId, createuser, createTime,modifyUser,modifyTime) "
                              "values(3, %s, 221, now(),221,now())",
                              company["id"])
            create(_id)

    # dms = conn.query("select st.* from track_sub_type st join track_type t on t.id=st.trackTypeId "
    #                  "where t.type=82002")
    # for dm in dms:
    #     track_dimension = dm["trackDimension"]
    #     investor = conn.get("select c.id,c.code,c.name,m.publishTime, m.message "
    #                        "from "
    #                        "investor_message m join investor c on m.investorId=c.id "
    #                        "where "
    #                        "m.active='Y' and "
    #                        "(c.active is null or c.active='Y') and "
    #                        "locationId<371 and "
    #                        "trackDimension=%s "
    #                        "and c.id not in (select investorId  from track_group_item_rel where trackGroupId=6)"
    #                        "order by  m.id desc limit 1",
    #                        track_dimension)
    #     if investor is not None:
    #         logger.info("trackDimension:%s, investorId: %s", track_dimension, investor["id"])
    #         _id = conn.insert(
    #             "insert track_group_item_rel(trackGroupId, investorId, createuser, createTime,modifyUser,modifyTime) "
    #             "values(6, %s, 221, now(),221,now())",
    #             investor["id"])
    #         create(_id)
    # delete(9)
    pass
