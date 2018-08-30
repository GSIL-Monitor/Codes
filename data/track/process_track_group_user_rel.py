# -*- coding: utf-8 -*-
import os, sys
import datetime

import track_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("process_track_group_user_rel", stream=True)
logger = loghelper.get_logger("process_track_group_user_rel")


def create(_id):
    logger.info("create start, id=%s", _id)
    conn = db.connect_torndb()
    rel = conn.get("select * from track_group_user_rel where id=%s", _id)
    if rel is None or rel["active"] != 'Y':
        conn.close()
        return

    track_group_id = rel["trackGroupId"]
    user_id = rel["userId"]

    track_group = conn.get("select * from track_group where id=%s", track_group_id)
    if track_group is None or track_group["active"] != 'Y':
        conn.close()
        return

    messages = track_util.get_messages_by_track_group(conn, track_group)
    conn.close()

    mongo = db.connect_mongo()
    for message in messages:
        track_util.push_message_to_user(mongo, track_group, user_id, message)
    mongo.close()
    logger.info("create end.")


def delete(_id):
    logger.info("delete start, id=%s", _id)
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    # 删除分组某个用户消息
    item = conn.get("select * from track_group_user_rel where id=%s", _id)
    if item is None or item["active"] != 'N':
        conn.close()
        mongo.close()
        return

    track_group_id = item["trackGroupId"]
    user_id = item["userId"]
    mongo.message.user_message2.delete_many({"trackGroupId": track_group_id, "userId": user_id})

    track_group = conn.get("select * from track_group where id=%s", track_group_id)
    if track_group is None:
        conn.close()
        mongo.close()
        return

    # 删除-1,-2,-3冗余数据
    messages = track_util.get_messages_by_track_group(conn, track_group)
    user_ids = [user_id]
    track_util.purge_redundant_user_message(mongo, track_group, user_ids, messages)

    mongo.close()
    conn.close()
    logger.info("delete end.")


if __name__ == '__main__':
    # 测试
    create(4)
    # delete(3)
    pass
