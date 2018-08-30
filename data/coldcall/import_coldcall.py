# -*- coding: utf-8 -*-
import os, sys
import re
import requests
import html2text
import email_reader
from pymongo import MongoClient
import gridfs
import mimetypes
import json
from kafka import (KafkaClient, SimpleProducer)

reload(sys)

sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import config
import loghelper
import db
import util

#logger
loghelper.init_logger("import_coldcall", stream=True)
logger = loghelper.get_logger("import_coldcall")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
imgfs = gridfs.GridFS(mongo.gridfs)

#mysql
conn = None

#kafka
(kafka_url) = config.get_kafka_config()
kafka = KafkaClient(kafka_url)
# HashedPartitioner is default
kafka_producer = SimpleProducer(kafka)

organizationId = 1

def find_user(org_id, email):
    if email is None:
        return None

    user = conn.get("select * from user u \
                        join user_email e on u.id=e.userId \
                        join user_organization_rel o on u.id=o.userId \
                    where \
                        o.organizationId=%s and \
                        e.email=%s and e.verify=true \
                        limit 1",
                    org_id, email)
    if user is None:
        return None
    return user["userId"]

if __name__ == '__main__':
    logger.info("Import coldcall start")

    try:
        re_name = re.compile('([\[\(] *)?(RE?S?|FYI|RIF|I|FS|VB|RV|ENC|ODP|PD|YNT|ILT|SV|VS|VL|AW|WG|ΑΠ|ΣΧΕΤ|ΠΡΘ|תגובה|הועבר|主题|转发|FWD?) *([-:;)\]][ :;\])-]*|$)|\]+ *$', re.IGNORECASE)

        conn = db.connect_torndb()
        r = requests.get("http://121.199.60.106:8000/api/project/sync/coldcall.json")
        result = r.json()
        list = result["list"]
        #logger.info(list)
        for vo in list:
            logger.info(vo["name"])
            name = re_name.sub('', vo["name"]).strip()
            name_md5 = util.md5str(name)
            cc = conn.get("select * from coldcall where organizationId=%s and nameMd5=%s limit 1", organizationId, name_md5)
            if cc is not None:
                logger.info("%s Exists!" % name)
                continue

            content = vo["content"].strip()
            coldcallType = vo["coldcallType"]
            cc_id = conn.insert("insert coldcall(name,nameMd5,content,organizationId,coldcallType,createTime) \
                                    values(%s,%s,%s,%s,%s,now())",
                                    name,
                                    name_md5,
                                    content,
                                    organizationId,
                                    coldcallType
                                )

            sponsor_id = find_user(organizationId, vo["sponsor_email"])
            logger.info("sponsor_id=%s" % sponsor_id)
            assignee_id = find_user(organizationId, vo["assignee_email"])
            logger.info("assignee_id=%s" % assignee_id)

            if sponsor_id is not None:
                conn.insert("insert coldcall_user_rel(coldcallId,userId,userIdentify,createTime) \
                            values(%s,%s,%s,now())",
                            cc_id,sponsor_id,21030)

            if assignee_id is not None:
                conn.insert("insert coldcall_user_rel(coldcallId,userId,userIdentify,createTime) \
                            values(%s,%s,%s,now())",
                            cc_id,assignee_id,21020)

            for f in vo["files"]:
                filename = f["filename"]
                url = f["url"]
                r = requests.get(url)
                content_type = "application/octet-stream"
                logo_id = imgfs.put(r.content, content_type=content_type, filename=filename)
                logger.info("gridfs logo_id=%s" % logo_id)
                conn.insert("insert coldcall_file(coldcallId,filename,link) values(%s,%s,%s)",
                            cc_id,filename,logo_id)

                msg = {"type":"coldcall", "id":cc_id}
                logger.info(json.dumps(msg))
                try:
                    kafka_producer.send_messages("coldcall", json.dumps(msg))
                except:
                    kafka_producer.send_messages("coldcall", json.dumps(msg))

            break   #test!
    except Exception,e :
        logger.exception(e)
    finally:
        conn.close()