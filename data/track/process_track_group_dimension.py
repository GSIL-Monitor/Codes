# -*- coding: utf-8 -*-
import os, sys
import datetime

import track_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("process_track_group_dimension", stream=True)
logger = loghelper.get_logger("process_track_group_dimension")


def create(_id):
    logger.info("create start, id=%s", _id)
    conn = db.connect_torndb()
    dim = conn.get("select * from track_group_dimension where id=%s", _id)
    if dim is None or dim["active"] != 'Y':
        conn.close()
        return

    track_group_id = dim["trackGroupId"]
    track_dimension = dim["trackDimension"]

    track_group = conn.get("select * from track_group where id=%s", track_group_id)
    if track_group is None or track_group["active"] != 'Y':
        conn.close()
        return

    messages = track_util.get_messages_by_track_group_and_dimension(conn, track_group, track_dimension)
    user_ids = track_util.get_track_user_ids_by_track_group(conn, track_group_id)

    conn.close()

    mongo = db.connect_mongo()
    for message in messages:
        for user_id in user_ids:
            track_util.push_message_to_user(mongo, track_group, user_id, message)
    mongo.close()
    logger.info("create end.")


def delete(_id):
    logger.info("create delete, id=%s", _id)
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    # 删除分组某个维度消息
    dim = conn.get("select * from track_group_dimension where id=%s", _id)
    if dim is None or dim["active"] != 'N':
        conn.close()
        mongo.close()
        return

    track_group_id = dim["trackGroupId"]
    track_dimension = dim["trackDimension"]
    mongo.message.user_message2.delete_many({"trackGroupId": track_group_id, "trackDimension": track_dimension})

    track_group = conn.get("select * from track_group where id=%s", track_group_id)
    if track_group is None:
        conn.close()
        mongo.close()
        return

    # 删除-1,-2,-3冗余数据
    messages = track_util.get_messages_by_track_group_and_dimension(conn, track_group, track_dimension)
    user_ids = track_util.get_track_user_ids_by_track_group(conn, track_group_id)
    track_util.purge_redundant_user_message(mongo, track_group, user_ids, messages)

    mongo.close()
    conn.close()
    logger.info("delete end.")


if __name__ == '__main__':
    # delete(23)  # 1001 媒体报道 cnt=88
    # delete(4)   # 2003 发布新版本 cnt=189
    # create(4)
    # create(54)    # 1001
    # delete(107)
    create(107)
    pass
