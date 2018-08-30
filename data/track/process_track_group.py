# -*- coding: utf-8 -*-
import os, sys
import datetime

import track_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("process_track_group", stream=True)
logger = loghelper.get_logger("process_track_group")


def create(_id):
    # 无需处理
    return


def delete(_id):
    logger.info("delete start, id=%s", _id)
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    # 删除分组所有消息
    mongo.message.user_message2.delete_many({"trackGroupId": _id})

    track_group_id = _id
    track_group = conn.get("select * from track_group where id=%s", track_group_id)
    if track_group is None or track_group["active"] != 'N':
        conn.close()
        mongo.close()
        return

    # 删除-1,-2,-3冗余数据
    messages = track_util.get_messages_by_track_group(conn, track_group)
    user_ids = track_util.get_track_user_ids_by_track_group(conn, track_group_id)
    track_util.purge_redundant_user_message(mongo, track_group, user_ids, messages)

    mongo.close()
    conn.close()
    logger.info("delete end.")


if __name__ == '__main__':
    # 测试
    # delete(7)
    pass
