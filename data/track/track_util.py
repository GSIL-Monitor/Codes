# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson.objectid import ObjectId

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper

#logger
loghelper.init_logger("track_util", stream=True)
logger = loghelper.get_logger("track_util")


def get_messages_by_track_group(conn, track_group):
    track_group_id = track_group["id"]

    if track_group["type"] == 82001:
        # 公司
        messages = conn.query("select m.* from company_message m "
                              "join company c on c.id=m.companyId "
                              "join track_group_item_rel item_rel on m.companyId=item_rel.companyId "
                              "join track_group_dimension dim on m.trackDimension=dim.trackDimension "
                              "join track_sub_type st on m.trackDimension=st.trackDimension and st.active='Y' "
                              "join track_type t on st.trackTypeId=t.id and t.active='Y' and t.type=82001 "
                              "where "
                              "(c.active is null or c.active='Y') and "
                              "m.active='Y' and "
                              "item_rel.active='Y' and "
                              "dim.active='Y' and "
                              "item_rel.trackGroupId=%s and "
                              "dim.trackGroupId=%s",
                              track_group_id, track_group_id)

    elif track_group["type"] == 82002:
        # 投资机构
        messages = conn.query("select m.* from investor_message m "
                              "join investor i on i.id=m.investorId "
                              "join track_group_item_rel item_rel on m.investorId=item_rel.investorId "
                              "join track_group_dimension dim on m.trackDimension=dim.trackDimension "
                              "join track_sub_type st on m.trackDimension=st.trackDimension and st.active='Y' "
                              "join track_type t on st.trackTypeId=t.id and t.active='Y' and t.type=82002 "
                              "where "
                              "(i.active is null or i.active='Y') and "
                              "i.online='Y' and "
                              "m.active='Y' and "
                              "item_rel.active='Y' and "
                              "dim.active='Y' and "
                              "item_rel.trackGroupId=%s and "
                              "dim.trackGroupId=%s",
                              track_group_id, track_group_id)
    else:
        messages = []
    return messages


def get_messages_by_track_group_and_dimension(conn, track_group, track_dimension):
    track_group_id = track_group["id"]

    if track_group["type"] == 82001:
        # 公司
        messages = conn.query("select m.* from company_message m "
                              "join company c on c.id=m.companyId "
                              "join track_group_item_rel item_rel on m.companyId=item_rel.companyId "
                              "join track_sub_type st on m.trackDimension=st.trackDimension and st.active='Y' "
                              "join track_type t on st.trackTypeId=t.id and t.active='Y' and t.type=82001 "
                              "where "
                              "(c.active is null or c.active='Y') and "
                              "m.active='Y' and "
                              "item_rel.active='Y' and "
                              "item_rel.trackGroupId=%s and "
                              "m.trackDimension=%s",
                              track_group_id, track_dimension)

    elif track_group["type"] == 82002:
        # 投资机构
        messages = conn.query("select m.* from investor_message m "
                              "join investor i on i.id=m.investorId "
                              "join track_group_item_rel item_rel on m.investorId=item_rel.investorId "
                              "join track_sub_type st on m.trackDimension=st.trackDimension and st.active='Y' "
                              "join track_type t on st.trackTypeId=t.id and t.active='Y' and t.type=82002 "
                              "where "
                              "(i.active is null or i.active='Y') and "
                              "i.online='Y' and "
                              "m.active='Y' and "
                              "item_rel.active='Y' and "
                              "item_rel.trackGroupId=%s and "
                              "m.trackDimension=%s",
                              track_group_id, track_dimension)
    else:
        messages = []
    return messages


def get_messages_by_item(conn, track_group, id):
    track_group_id = track_group["id"]

    if track_group["type"] == 82001:
        # 公司
        messages = conn.query("select m.* from company_message m "
                              "join company c on c.id=m.companyId "
                              "join track_group_dimension dim on m.trackDimension=dim.trackDimension "
                              "join track_sub_type st on m.trackDimension=st.trackDimension and st.active='Y' "
                              "join track_type t on st.trackTypeId=t.id and t.active='Y' and t.type=82001 "
                              "where "
                              "(c.active is null or c.active='Y') and "
                              "m.active='Y' and "
                              "dim.active='Y' and "
                              "dim.trackGroupId=%s and "
                              "c.id=%s",
                              track_group_id, id)

    elif track_group["type"] == 82002:
        # 投资机构
        messages = conn.query("select m.* from investor_message m "
                              "join investor i on i.id=m.investorId "
                              "join track_group_dimension dim on m.trackDimension=dim.trackDimension "
                              "join track_sub_type st on m.trackDimension=st.trackDimension and st.active='Y' "
                              "join track_type t on st.trackTypeId=t.id and t.active='Y' and t.type=82002 "
                              "where "
                              "(i.active is null or i.active='Y') and "
                              "i.online='Y' and "
                              "m.active='Y' and "
                              "dim.active='Y' and "
                              "dim.trackGroupId=%s and "
                              "i.id=%s",
                              track_group_id, id)
    else:
        messages = []
    return messages


def get_track_groups(conn, track_dimension, company_id=None, investor_id=None):
    if company_id is not None:
        column = "companyId"
        value = company_id
    elif investor_id is not None:
        column = "investorId"
        value = investor_id
    else:
        return []
    items = conn.query("select g.* from track_group g "
                       "join track_group_item_rel item_rel on g.id=item_rel.trackGroupId "
                       "join track_group_dimension dim on g.id=dim.trackGroupId "
                       "where "
                       "g.active='Y' and "
                       "item_rel.active='Y' and "
                       "item_rel." + column + "=%s and "
                       "dim.trackDimension=%s",
                       value, track_dimension)
    return items


def get_track_user_ids_by_track_group(conn, track_group_id):
    user_ids = []
    track_group = conn.get("select * from track_group where id=%s", track_group_id)
    if track_group is None:
        return user_ids

    if track_group["userId"] is not None:
        user_ids.append(track_group["userId"])
        return user_ids
    elif track_group["organizationId"] is not None:
        items = conn.query("select distinct user_rel.userId as userId from track_group_user_rel user_rel "
                           "where "
                           "user_rel.active='Y' and "
                           "user_rel.trackGroupId=%s",
                           track_group_id)
        user_ids = [item["userId"] for item in items]
    return user_ids


def adjust_publish_time(mongo, track_group_id, user_id, publish_time):
    while True:
        m = mongo.message.user_message2.find_one({
            "userId": user_id,
            "trackGroupId": track_group_id,
            "publishTime": publish_time
        })
        if m is not None:
            publish_time += datetime.timedelta(milliseconds=1)
        else:
            break
    return publish_time


def from_utc8_to_utc0(d):
    return d + datetime.timedelta(hours=-8)


def push_company_message_to_user(mongo, track_group_org_or_private, track_group_id, user_id, message):
    publish_time = from_utc8_to_utc0(message["publishTime"])
    publish_time = adjust_publish_time(mongo, track_group_id, user_id, publish_time)

    company_message_id = int(message["id"])
    user_message = mongo.message.user_message2.find_one({
        "userId": user_id,
        "trackGroupId": track_group_id,
        "companyMessageId": company_message_id
    })
    if user_message is None:
        data = {
            "type": 5010,
            "userId": int(user_id),
            "trackGroupId": int(track_group_id),
            "trackGroupOrgOrPrivate": track_group_org_or_private ,
            "companyMessageId": company_message_id,
            "companyId": int(message["companyId"]),
            "relateType": int(message["relateType"]),
            "trackDimension": int(message["trackDimension"]),
            "relateId": message["relateId"],
            "detailId":message["detailId"],
            "publishTime": publish_time,
            "createTime": datetime.datetime.utcnow(),
            "active": "Y",
            "negative": message["negative"]
        }
        mongo.message.user_message2.insert_one(data)


def push_investor_message_to_user(mongo, track_group_org_or_private, track_group_id, user_id, message):
    publish_time = from_utc8_to_utc0(message["publishTime"])
    publish_time = adjust_publish_time(mongo, track_group_id, user_id, publish_time)

    investor_message_id = int(message["id"])
    user_message = mongo.message.user_message2.find_one({
        "userId": user_id,
        "trackGroupId": track_group_id,
        "investorMessageId": investor_message_id
    })
    if user_message is None:
        data = {
            "type": 5030,
            "userId": int(user_id),
            "trackGroupId": int(track_group_id),
            "trackGroupOrgOrPrivate": track_group_org_or_private,
            "investorMessageId": investor_message_id,
            "investorId": int(message["investorId"]),
            "relateType": int(message["relateType"]),
            "trackDimension": int(message["trackDimension"]),
            "relateId": message["relateId"],
            "detailId":message["detailId"],
            "publishTime": publish_time,
            "createTime": datetime.datetime.utcnow(),
            "active": "Y"
        }
        mongo.message.user_message2.insert_one(data)


def push_message_to_user(mongo, track_group, user_id, message):
    track_group_id = track_group["id"]
    if track_group["userId"] is not None:
        track_group_org_or_private = "private"
    elif track_group["organizationId"] is not None:
        track_group_org_or_private = "org"

    if track_group["type"] == 82001:
        push_company_message_to_user(mongo, track_group_org_or_private, track_group_id, user_id, message)
        push_company_message_to_user(mongo, None, -1, user_id, message)
        if track_group["userId"] is not None:
            push_company_message_to_user(mongo, None, -2, user_id, message)
        if track_group["organizationId"] is not None:
            push_company_message_to_user(mongo, None, -3, user_id, message)
    elif track_group["type"] == 82002:
        push_investor_message_to_user(mongo, track_group_org_or_private, track_group_id, user_id, message)
        push_investor_message_to_user(mongo, None, -1, user_id, message)
        if track_group["userId"] is not None:
            push_investor_message_to_user(mongo, None, -2, user_id, message)
        if track_group["organizationId"] is not None:
            push_investor_message_to_user(mongo, None, -3, user_id, message)


def purge_redundant_user_message(mongo, track_group, user_ids, messages):
    if track_group["userId"] is not None:
        # 清除 -2
        for message in messages:
            for user_id in user_ids:
                message_id = message["id"]
                if track_group["type"] == 82001:
                    um = mongo.message.user_message2.find_one({
                        "companyMessageId": message_id,
                        "userId": user_id,
                        "trackGroupOrgOrPrivate": "private"
                    })
                    if um is None:
                        mongo.message.user_message2.delete_many({
                            "companyMessageId": message_id,
                            "userId": user_id,
                            "trackGroupId": -2
                        })
                elif track_group["type"] == 82002:
                    um = mongo.message.user_message2.find_one({
                        "investorMessageId": message_id,
                        "userId": user_id,
                        "trackGroupOrgOrPrivate": "private"
                    })
                    if um is None:
                        mongo.message.user_message2.delete_many({
                            "investorMessageId": message_id,
                            "userId": user_id,
                            "trackGroupId": -2
                        })
    elif track_group["organizationId"] is not None:
        # 清除 -3
        for message in messages:
            for user_id in user_ids:
                message_id = message["id"]
                if track_group["type"] == 82001:
                    um = mongo.message.user_message2.find_one({
                        "companyMessageId": message_id,
                        "userId": user_id,
                        "trackGroupOrgOrPrivate": "org"
                    })
                    if um is None:
                        mongo.message.user_message2.delete_many({
                            "companyMessageId": message_id,
                            "userId": user_id,
                            "trackGroupId": -3
                        })
                elif track_group["type"] == 82002:
                    um = mongo.message.user_message2.find_one({
                        "investorMessageId": message_id,
                        "userId": user_id,
                        "trackGroupOrgOrPrivate": "private"
                    })
                    if um is None:
                        mongo.message.user_message2.delete_many({
                            "investorMessageId": message_id,
                            "userId": user_id,
                            "trackGroupId": -3
                        })

    # 清除 -1
    for message in messages:
        for user_id in user_ids:
            message_id = message["id"]
            if track_group["type"] == 82001:
                um = mongo.message.user_message2.find_one({
                    "companyMessageId": message_id,
                    "userId": user_id,
                    "trackGroupOrgOrPrivate": {"$ne": None}
                })
                if um is None:
                    mongo.message.user_message2.delete_many({
                        "companyMessageId": message_id,
                        "userId": user_id,
                        "trackGroupId": -1
                    })
            elif track_group["type"] == 82002:
                um = mongo.message.user_message2.find_one({
                    "investorMessageId": message_id,
                    "userId": user_id,
                    "trackGroupOrgOrPrivate": {"$ne": None}
                })
                if um is None:
                    mongo.message.user_message2.delete_many({
                        "investorMessageId": message_id,
                        "userId": user_id,
                        "trackGroupId": -1
                    })
