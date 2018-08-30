# -*- coding: utf-8 -*-
import os, sys
import json
import datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("user_migrate", stream=True)
logger = loghelper.get_logger("user_migrate")


def migrate(conn, new_user_id, user_id):
    tables = [
        "user_sector",
        "user_preference",
        "user_save_search",
        "collection_user_rel", # 集合
        "user_mylist_rel",   # 收藏
        "user_news_mark",    # 新闻
        "user_company_subscription", # 公司订阅
        "user_topic_subscription", # 主题订阅
        "user_investor_subscription", # 机构订阅
        "recommendation", # 推荐
        "bookmark", # 收藏（新）
        "bookmark_item", # 收藏（新）
    ]

    mongo_tables = [
        ("message", "user_message")
    ]

    for t in tables:
        sql = "update " + t + " set userId=" + str(new_user_id) + " where userId=" + str(user_id)
        logger.info(sql)
        conn.update(sql)

    mongo = db.connect_mongo()
    for d,t in mongo_tables:
        mongo[d][t].update({"userId":user_id},{"$set":{"userId":new_user_id}})
    mongo.close()


def create_user(conn, item):
    SALT = "24114581331805856724"

    # disable old user
    user_id = item["userId"]
    conn.update("update user set active='D', phoneVerify='N', emailVerify='N' where id=%s", user_id)

    # user
    phoneVerify = 'N'
    if item["phone"] is not None and item["phone"].strip != "":
        phoneVerify = 'Y'

    emailVerify = 'N'
    if item["email"] is not None and item["email"].strip != "":
        emailVerify = 'Y'

    new_user_id = conn.insert("insert user(username,position,email,phone,userIdentify,loginFailTimes,"
                              "phoneVerify,emailVerify,active,verifiedInvestor,createTime) values"
                              "(%s,%s,%s,%s,%s,0,"
                              "%s,%s,'Y','N',now())",
                              item["username"], item.get("position"), item["email"], item["phone"], item["userIdentify"],
                                phoneVerify, emailVerify
                              )
    password = util.md5str(SALT + str(new_user_id) + item["password"])
    conn.update("update user set password=%s where id=%s", password, new_user_id)

    # organization (personal)
    org_id = conn.insert("insert organization(name,type,status,grade,active,createUser,createTime,modifyUser,modifyTime) "
                         "values(%s, 17010,31010,33020,'Y',%s,now(),%s,now())",
                         item["username"], new_user_id, new_user_id)

    # user_organization_rel
    conn.insert("insert user_organization_rel(userId,organizationId,active,createTime) values(%s,%s,'Y',now())",
                new_user_id, org_id)
    return new_user_id


def check(item):
    user_id = item["userId"]
    phone = item["phone"]
    email = item["email"]

    if phone is not None and phone.strip() != "":
        conn = db.connect_torndb()
        u = conn.get("select * from user where id!=%s and phone=%s and (phoneVerify='Y' or phoneVerify='O') limit 1",
                     user_id, phone)
        conn.close()
        if u is not None:
            return 1

    if email is not None and email.strip() != "":
        conn = db.connect_torndb()
        u = conn.get("select * from user where id!=%s and email=%s and (emailVerify='Y' or emailVerify='O') limit 1",
                     user_id, email)
        conn.close()
        if u is not None:
            return 2

    return 0


def main():
    mongo = db.connect_mongo()
    items = mongo.task.user_migrate.find({"processStatus": 1})
    for item in items:
        logger.info("userId: %s", item["userId"])
        flag = check(item)
        if flag == 1:
            mongo.task.user_migrate.update_one({"_id": item["_id"]},
                                               {"$set": {"processStatus": 3, "comments": "phone exists!"}})
            continue
        if flag == 2:
            mongo.task.user_migrate.update_one({"_id": item["_id"]},
                                               {"$set": {"processStatus": 3, "comments": "email exists!"}})
            continue
        conn = db.connect_torndb()
        conn.execute("set autocommit = 0")
        new_user_id = create_user(conn, item)
        migrate(conn, new_user_id, item["userId"])
        conn.execute("set autocommit = 1")
        conn.close()
        mongo.task.user_migrate.update_one({"_id":item["_id"]},{"$set":{"processStatus":2, "newUserId": new_user_id}})
    mongo.close()


if __name__ == '__main__':
    while True:
        logger.info("Start...")
        main()
        logger.info("End.")
        time.sleep(60)