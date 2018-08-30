# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("migrate_ctbb", stream=True)
logger = loghelper.get_logger("migrate_ctbb")


conn = db.connect_torndb()

def migrate_ctbs_user():
    ctbs_users = conn.query("select * from ctbs_user where active='Y'")
    for ctbs_user in ctbs_users:
        if ctbs_user["unionid"] is None:
            continue
        logger.info(ctbs_user)

        ctbsUserId = ctbs_user["id"]
        userId = find_and_create_user(ctbs_user)
        logger.info("userId=%s", userId)

        # migrate_user_search(ctbsUserId, userId)  # 无数据
        migrate_user_visit(ctbsUserId, userId)
        migrate_user_like(ctbsUserId, userId)
        migrate_user_comment(ctbsUserId, userId)
        migrate_user_share(ctbsUserId, userId)
        migrate_user_comment_like(ctbsUserId, userId)


def find_and_create_user(ctbs_user):
    openid = ctbs_user["openid"]
    unionid = ctbs_user["unionid"]
    user_wechat = None

    if user_wechat is None:
        user_wechat = conn.get("select * from user_wechat where unionid=%s and userId is not null order by id desc limit 1", unionid)
    if user_wechat is None:
        user_wechat = conn.get("select * from user_wechat where openid=%s and userId is not null order by id desc limit 1", openid)
    if user_wechat is None:
        user_wechat = conn.get("select * from user_wechat where unionid=%s order by id desc limit 1", unionid)
    if user_wechat is None:
        user_wechat = conn.get("select * from user_wechat where openid=%s order by id desc limit 1", openid)

    if user_wechat is None:
        # create user_wechat
        user_wechat = {
            "userId": None,
            "openid": openid,
            "nickname": ctbs_user["nickName"],
            "sex": ctbs_user["gender"],
            "province": ctbs_user["province"],
            "city": ctbs_user["city"],
            "country": ctbs_user["country"],
            "headimgurl": ctbs_user["avatarUrl"],
            "loginIP": ctbs_user["ip"],
            "unionId": ctbs_user["unionid"],
            "createTime": ctbs_user["createTime"],
            "modifyTime": ctbs_user["modifyTime"]
        }
        _id = conn.insert("insert user_wechat(openid,nickname,sex,province,city,country,headimgurl,"
                          "loginIP,unionId,createTime,modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                          user_wechat["openid"],
                          user_wechat["nickname"],
                          user_wechat["sex"],
                          user_wechat["province"],
                          user_wechat["city"],
                          user_wechat["country"],
                          user_wechat["headimgurl"],
                          user_wechat["loginIP"],
                          user_wechat["unionId"],
                          user_wechat["createTime"],
                          user_wechat["modifyTime"]
        )
        user_wechat["id"] = _id
        logger.info("create user_wechat")
        logger.info(user_wechat)

    if user_wechat["userId"] is None:
        # create user
        _id = conn.insert("insert user(username,active,createTime,modifyTime,loginIP,phoneVerify,emailVerify) "
                          "values(%s,'Y',%s,%s,%s,'N','N')",
                          user_wechat["nickname"],
                          user_wechat["createTime"],
                          user_wechat["modifyTime"],
                          user_wechat["loginIP"]
                          )
        user_wechat["userId"] = _id
        conn.update("update user_wechat set userId=%s where id=%s", _id, user_wechat["id"])
        logger.info("create user")
        logger.info("userId=%s", _id)
        # exit()

    return user_wechat["userId"]


def migrate_user_search(ctbsUserId, userId):
    pass


def migrate_user_visit(ctbsUserId, userId):
    conn.update("update user_visit set userId=%s where ctbsUserId=%s", userId, ctbsUserId)


def migrate_user_like(ctbsUserId, userId):
    conn.update("update user_like set userId=%s where ctbsUserId=%s", userId, ctbsUserId)


def migrate_user_comment(ctbsUserId, userId):
    conn.update("update user_comment set userId=%s where ctbsUserId=%s", userId, ctbsUserId)


def migrate_user_share(ctbsUserId, userId):
    conn.update("update user_share set userId=%s where ctbsUserId=%s", userId, ctbsUserId)


def migrate_user_comment_like(ctbsUserId, userId):
    conn.update("update user_comment_like set userId=%s where ctbsUserId=%s", userId, ctbsUserId)


def check():
    pass


def main():
    migrate_ctbs_user()
    check()


if __name__ == '__main__':
    main()