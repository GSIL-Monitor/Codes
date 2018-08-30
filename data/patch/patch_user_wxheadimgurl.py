# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("patch_user_wxheadimgurl", stream=True)
logger = loghelper.get_logger("patch_user_wxheadimgurl")

conn = None


def main():
    conn = db.connect_torndb()
    users = conn.query("select * from user where wxheadimgurl is null")
    for user in users:
        uw = conn.get("select * from user_wechat where userId=%s and headimgurl is not null order by id desc limit 1", user["id"])
        if uw is not None:
            conn.update("update user set wxheadimgurl=%s where id=%s", uw["headimgurl"], user["id"])
    conn.close()


def main2():
    conn = db.connect_torndb()
    users = conn.query("select * from user where username is not null and username=phone")
    for user in users:
        uw = conn.get("select * from user_wechat where userId=%s and headimgurl is not null order by id desc limit 1", user["id"])
        if uw is not None:
            conn.update("update user set username=%s where id=%s", uw["nickname"], user["id"])
    conn.close()


if __name__ == "__main__":
    main()
    main2()