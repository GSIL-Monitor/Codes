# -*- coding: utf-8 -*-
import os, sys
import datetime
import traceback
import track_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("track_investor_message", stream=True)
logger = loghelper.get_logger("track_investor_message")


def process(conn, mongo, investor_message_id):
    if investor_message_id is None:
        return
    message = conn.get("select * from investor_message where id=%s", investor_message_id)
    if message is None:
        return
    if message["active"] != 'Y':
        return

    logger.info("track investor_message_id: %s", investor_message_id)

    # 推送给用户
    investor_id = message["investorId"]
    track_dimension = message["trackDimension"]

    track_sub_type = conn.get("select st.* from track_sub_type st join track_type t on st.trackTypeId=t.id "
                              "where st.trackDimension=%s and t.type=82002 and st.active='Y' and t.active='Y' limit 1",
                              track_dimension)
    if track_sub_type is None:
        return

    # 公司所在的分组
    track_groups = track_util.get_track_groups(conn, track_dimension, investor_id=investor_id)
    for g in track_groups:
        track_group_id = g["id"]
        user_ids = track_util.get_track_user_ids_by_track_group(conn, track_group_id)
        for user_id in user_ids:
            track_util.push_message_to_user(mongo, g, user_id, message)


def delete(mongo, investor_message_id):
    mongo.message.user_message2.delete_many({"investorMessageId": investor_message_id})


if __name__ == '__main__':
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    process(conn, mongo, 17008)
    # delete(mongo, 17008)
