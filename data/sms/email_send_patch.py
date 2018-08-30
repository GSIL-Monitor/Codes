# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import traceback
from mako.template import Template
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import requests, json
from aliyun_monitor import AliyunMonitor

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("email_send_patch", stream=True)
logger = loghelper.get_logger("email_send_patch")


def merge_users(to_list, from_list):
    for user in from_list:
        exist = False
        for u in to_list:
            if user["id"] == u["id"]:
                exist = True
        if exist is False:
            to_list.append(user)

if __name__ == "__main__":
    cnt = 0
    conn = db.connect_torndb()
    orgs = conn.query("select * from organization where "
                      "grade=33010 and trial='Y' and serviceEndDate is not null "
                      "and id not in (7,51,2173)")
    for org in orgs:
        logger.info(org["name"])
        t_users = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                             "where r.organizationId=%s and r.active='Y'",
                             org["id"])
        logger.info("user in trial:")
        for u in t_users:
            role = conn.get("select * from user_role where userId=%s order by role limit 1", u["id"])
            role_id = None
            if role:
                role_id = role["role"]
            logger.info("%s, %s, %s, role: %s", u["id"], u["username"], u["email"], role_id)



        t_users = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                             "where r.organizationId=%s and r.active='N'",
                             org["id"])


        org_users1 = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                                    "join organization o on r.organizationId=o.id "
                                    "where o.grade=33020 and o.id != %s and o.name=%s",
                                    org["id"], org["name"])
        merge_users(t_users,org_users1)

        if org["emailDomain"] is not None and org["emailDomain"].strip() != "":
            org_users2 = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                                "join organization o on r.organizationId=o.id "
                                "where o.grade=33020 and o.id != %s and o.emailDomain=%s",
                                org["id"], org["emailDomain"])
            merge_users(t_users,org_users2)

        logger.info("***user not in trial:")
        for u in t_users:
            logger.info("%s, %s", u["username"], u["email"])
            cnt += 1
        logger.info("--------------------------------------")
    conn.close()

    logger.info("total to send: %s", cnt)
