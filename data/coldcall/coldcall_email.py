# -*- coding: utf-8 -*-
import os, sys
import re
import html2text
import email_reader
from pymongo import MongoClient
import gridfs
import mimetypes
import json
from kafka import (KafkaClient, SimpleProducer)
from random import choice

reload(sys)

sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import config
import loghelper
import db
import util

#logger
loghelper.init_logger("coldcall_email", stream=True)
logger = loghelper.get_logger("coldcall_email")

#mongo
mongo = db.connect_mongo()
imgfs = gridfs.GridFS(mongo.gridfs)

#mysql
conn = None

#kafka
(kafka_url) = config.get_kafka_config()
kafka = KafkaClient(kafka_url)
# HashedPartitioner is default
kafka_producer = SimpleProducer(kafka)

def find_user(org_id, email):
    user = conn.get("select * from user u \
                        join user_email e on u.id=e.userId \
                        join user_organization_rel o on u.id=o.userId \
                    where \
                        o.organizationId=%s and \
                        e.email=%s and e.verify=true \
                        limit 1",
                    org_id, email)
    if user is not None:
        return user["userId"]

    user = conn.get("select u.* from user u join user_organization_rel r on u.id=r.userId "
                    "where r.organizationid=%s and u.email=%s limit 1")
    if user is not None:
        return user["id"]

    return None


def get_investment_manager_ids(org_id):
    # TODO 特殊处理，排除tony@gobivc.com 625，他在香港，不看大陆案子。如何统一处理?
    users = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                       "join user_role role on u.id=role.userId "
                       "where r.organizationid=%s and role.role=25040 and u.id!=625", org_id)
    user_ids = []
    for user in users:
        user_ids.append(user["id"])
    return user_ids


if __name__ == '__main__':
    logger.info("coldcall email start")
    try:
        re_name = re.compile('([\[\(] *)?(RE?S?|FYI|RIF|I|FS|VB|RV|ENC|ODP|PD|YNT|ILT|SV|VS|VL|AW|WG|ΑΠ|ΣΧΕΤ|ΠΡΘ|תגובה|הועבר|主题|转发|FWD?) *([-:;)\]][ :;\])-]*|$)|\]+ *$', re.IGNORECASE)

        conn = db.connect_torndb()
        orgs = conn.query("select * from organization o, organization_conf c where o.id=c.id and coldcall=true")
        for org in orgs:
            print org["id"], org["name"]
            msgs = email_reader.receive(org["coldcall_imap_server"], org["coldcall_imap_port"],
                                        org["coldcall_username"],org["coldcall_password"])
            for msg in msgs:
                if msg["to"].strip().lower() != org["coldcall_username"].lower():
                    continue

                if msg["html"] is not None:
                    parser = html2text.HTML2Text()
                    parser.ignore_emphasis=True
                    parser.single_line_break=True
                    msg["html_text"] = parser.handle(msg["html"])
                else:
                    msg["html_text"] = None

                logger.info(msg["subject"])
                logger.info(msg["from"])
                logger.info(msg["to"])
                logger.info(msg["cc"])
                #logger.info(msg["body"])
                #logger.info(msg["html_text"])
                logger.info("attachments=%d" % len(msg["attachments"]))
                for attach in msg["attachments"]:
                    logger.info(attach.name)

                name = re_name.sub('', msg["subject"]).strip()
                name_md5 = util.md5str(name)
                cc = conn.get("select * from coldcall where organizationId=%s and nameMd5=%s limit 1", org["id"], name_md5)
                if cc is not None:
                    logger.info("%s Exists!" % name)
                    continue

                content = msg["html_text"]
                if content is None:
                    content = msg["body"]
                if content is None:
                    content = ""
                content = content.strip()

                cc_id = conn.insert("insert coldcall(name,nameMd5,content,organizationId,coldcallType,createTime) \
                                    values(%s,%s,%s,%s,24010,now())",
                                    name,
                                    name_md5,
                                    content,
                                    org["id"]
                                    )

                sponsor_id = find_user(org["id"], msg["from"])
                logger.info("sponsor_id=%s" % sponsor_id)
                assignee_id = find_user(org["id"], msg["cc"])
                logger.info("assignee_id=%s" % assignee_id)

                if sponsor_id is not None:
                    conn.insert("insert coldcall_user_rel(coldcallId,userId,userIdentify,createTime) \
                                values(%s,%s,%s,now())",
                                cc_id,sponsor_id,21030)

                if assignee_id is None:
                    ids = get_investment_manager_ids(org["id"])
                    assignee_id = choice(ids)

                if assignee_id is not None:
                    conn.insert("insert coldcall_user_rel(coldcallId,userId,userIdentify,createTime) \
                                values(%s,%s,%s,now())",
                                cc_id,assignee_id,21020)
                    conn.insert("insert coldcall_forward(coldcallId,fromUserId,toUserId,createTime) \
                                values(%s,%s,%s,now())",
                                cc_id,sponsor_id,assignee_id)

                for attach in msg["attachments"]:
                    if attach.name is not None and attach.name.strip() != "":
                        name = attach.name.strip()
                        if not name.lower().endswith("pdf") and \
                           not name.lower().endswith("ppt") and \
                           not name.lower().endswith("pptx") and \
                           not name.lower().endswith("doc") and \
                           not name.lower().endswith("docx") and \
                           not name.lower().endswith("xls") and \
                           not name.lower().endswith("xlsx"):
                            continue

                        (content_type,encoding) = mimetypes.guess_type(name)
                        if content_type is None:
                            content_type = "application/octet-stream"
                        logo_id = imgfs.put(attach.getvalue(), content_type=content_type, filename=name)
                        logger.info("gridfs logo_id=%s" % logo_id)
                        conn.insert("insert coldcall_file(coldcallId,filename,link) values(%s,%s,%s)",
                                    cc_id,name,logo_id)

                msg = {"type":"coldcall", "id":cc_id}
                logger.info(json.dumps(msg))
                try:
                    kafka_producer.send_messages("coldcall", json.dumps(msg))
                except:
                    kafka_producer.send_messages("coldcall", json.dumps(msg))

    except Exception,e :
        logger.exception(e)
    finally:
        conn.close()