# -*- coding: utf-8 -*-
import os, sys
import traceback
import time, datetime

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, email_helper

#logger
loghelper.init_logger("openapi_testuser_downgrade", stream=True)
logger = loghelper.get_logger("openapi_testuser_downgrade")

emails = [
        "arthur@xiniudata.com",
    ]


def main():
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    orgs = conn.query("select * from org_openapi_conf where (active is null or active='Y') and trial='Y'")
    for org in orgs:
        accesskeyid = org["accesskeyid"]
        cnt = mongo.log.openapi_log.find({"accesskeyid": accesskeyid, "code":0}).count()
        logger.info("orgId: %s, cnt: %s", org["organizationId"], cnt)
        conn.update("update org_openapi_conf set usedCnt=%s where id=%s", cnt, org["id"])

        if cnt + 1000 > org["maxTest"]:
            w = mongo.log.openapi_warning.find_one({"orgId": org["organizationId"]}, sort=[('time', -1)])
            if w is None or (datetime.datetime.utcnow() - w["time"]).days >= 1:
                o = conn.get("select * from organization where id=%s", org["organizationId"])
                title = "%s-api访问次数即将耗尽" % o["name"]
                logger.info(title)
                content = title + "。\n"
                content += "可访问次数： %s, 已使用次数: %s。\n" % (org["maxTest"], cnt)
                content += "请尽快联系客户！"
                mongo.log.openapi_warning.insert_one(
                    {"orgId": org["organizationId"], "time": datetime.datetime.utcnow(), "description": title})
                for email in emails:
                    email_helper.send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", email,
                                           title, content)

        if cnt > org["maxTest"]:
            conn.update("update org_openapi_conf set active='N' where id=%s", org["id"])
            o = conn.get("select * from organization where id=%s", org["organizationId"])
            title = "%s-api访问次数已耗尽" % o["name"]
            logger.info(title)
            content = title + "。\n"
            content += "可访问次数： %s, 已使用次数: %s。\n" % (org["maxTest"], cnt)
            content += "请尽快联系客户！"
            mongo.log.openapi_warning.insert_one(
                {"orgId": org["organizationId"], "time": datetime.datetime.utcnow(), "description": title})
            for email in emails:
                email_helper.send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", email,
                                       title, content)


    mongo.close()
    conn.close()


if __name__ == '__main__':
    while True:
        logger.info("Start...")
        main()
        logger.info("End.")
        time.sleep(60)