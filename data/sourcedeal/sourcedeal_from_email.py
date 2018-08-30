# -*- coding: utf-8 -*-
import os, sys
import time
import re
import html2text
import email_reader
import gridfs
import mimetypes
from random import choice

reload(sys)

sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db
import util
import oss2_helper

#logger
loghelper.init_logger("sourcedeal_from_email", stream=True)
logger = loghelper.get_logger("sourcedeal_from_email")


def find_user(org_id, email):
    conn = db.connect_torndb()
    user = conn.get("select * from user u \
                        join user_email e on u.id=e.userId \
                        join user_organization_rel o on u.id=o.userId \
                    where \
                        o.organizationId=%s and \
                        e.email=%s and e.verify=true \
                        limit 1",
                    org_id, email)
    conn.close()
    if user is not None:
        return user["userId"]

    conn = db.connect_torndb()
    user = conn.get("select u.* from user u join user_organization_rel r on u.id=r.userId "
                    "where r.organizationid=%s and u.email=%s limit 1",
                    org_id, email)
    conn.close()

    if user is not None:
        return user["id"]

    return None


def get_investment_manager_ids(org_id):
    conn = db.connect_torndb()
    users = conn.query("select u.* from user u join user_organization_rel r on u.id=r.userId "
                       "join user_role role on u.id=role.userId "
                       "where r.organizationid=%s and role.role=25040 and "
                       "(u.active is null or u.active!='D') and "
                       "r.active='Y'",
                       org_id)
    conn.close()
    user_ids = []
    for user in users:
        user_ids.append(user["id"])
    return user_ids


def run():
    try:
        conn = db.connect_torndb()
        orgs = conn.query("select * from organization o, organization_conf c "
                          "where o.id=c.id and coldcall=true")
        conn.close()
        for org in orgs:
            try:
                process(org)
            except Exception, e:
                logger.exception(e)
    except Exception, e:
        logger.exception(e)


def process(org):
    if org["coldcall_imap_server"] is None:
        return

    logger.info("orgId: %s, orgName: %s", org["id"], org["name"])

    re_name = re.compile(
        '([\[\(] *)?(RE?S?|FYI|RIF|I|FS|VB|RV|ENC|ODP|PD|YNT|ILT|SV|VS|VL|AW|WG|ΑΠ|ΣΧΕΤ|ΠΡΘ|תגובה|הועבר|主题|转发|FWD?) *([-:;)\]][ :;\])-]*|$)|\]+ *$',
        re.IGNORECASE)

    while True:
        msgs = email_reader.receive(org["coldcall_imap_server"], org["coldcall_imap_port"],
                                    org["coldcall_username"], org["coldcall_password"], one=True)
        if len(msgs) == 0:
            break

        for msg in msgs:
            if msg["html"] is not None:
                parser = html2text.HTML2Text()
                parser.ignore_emphasis = True
                parser.single_line_break = True
                msg["html_text"] = parser.handle(msg["html"])
            else:
                msg["html_text"] = None

            logger.info(msg["subject"])
            logger.info(msg["from"])
            logger.info(msg["to"])
            logger.info(msg["cc"])
            # logger.info(msg["body"])
            # logger.info(msg["html_text"])
            logger.info("attachments=%d" % len(msg["attachments"]))
            for attach in msg["attachments"]:
                logger.info(attach.name)

            title = re_name.sub('', msg["subject"]).strip()
            title_md5 = util.md5str(title)

            #insert
            conn = db.connect_torndb()
            cc = conn.get("select * from sourcedeal where orgId=%s and titleMd5=%s and origin=%s limit 1",
                          org["id"],
                          title_md5,
                          msg["from"]
                          )
            conn.close()
            if cc is not None:
                logger.info("%s Exists!" % title)
                continue

            content = msg["html_text"]
            if content is None:
                content = msg["body"]
            if content is None:
                content = ""
            content = content.strip()
            if len(content) > 20000:
                content = content[0:20000]

            sponsor_id = find_user(org["id"], msg["from"])
            logger.info("sponsor_id=%s" % sponsor_id)
            assignee_id = find_user(org["id"], msg["cc"])
            logger.info("assignee_id=%s" % assignee_id)

            conn = db.connect_torndb()
            cc_id = conn.insert("insert sourcedeal(title,titleMd5,content,orgId,createTime,origin,assignee,sponsor) \
                                                values(%s,%s,%s,%s,%s,%s,%s,%s)",
                                title,
                                title_md5,
                                content,
                                org["id"],
                                msg["date"],
                                msg["from"],
                                assignee_id,
                                sponsor_id
                                )

            if assignee_id is None:
                ids = get_investment_manager_ids(org["id"])
                assignee_id = choice(ids)
                conn.update("update sourcedeal set assignee=%s where id=%s", assignee_id, cc_id)
                conn.insert("insert sourcedeal_forward(sourcedealId,toUserId,createTime) "
                            "values(%s,%s,%s)",
                            cc_id, assignee_id, msg["date"])
            else:
                conn.insert("insert sourcedeal_forward(sourcedealId,fromUserId,toUserId,createTime) "
                            "values(%s,%s,%s,%s)",
                            cc_id, sponsor_id, assignee_id,msg["date"])

            for attach in msg["attachments"]:
                if attach.name is not None and attach.name.strip() != "":
                    name = attach.name.strip()
                    if not name.lower().endswith("pdf") and \
                            not name.lower().endswith("rar") and \
                            not name.lower().endswith("zip") and \
                            not name.lower().endswith("7z") and \
                            not name.lower().endswith("ppt") and \
                            not name.lower().endswith("pptx") and \
                            not name.lower().endswith("doc") and \
                            not name.lower().endswith("docx") and \
                            not name.lower().endswith("xls") and \
                            not name.lower().endswith("xlsx"):
                        continue

                    (content_type, encoding) = mimetypes.guess_type(name)
                    if content_type is None:
                        content_type = "application/octet-stream"
                    data = attach.getvalue()
                    # mongo = db.connect_mongo()
                    # imgfs = gridfs.GridFS(mongo.gridfs)
                    # logo_id = imgfs.put(data, content_type=content_type, filename=name)
                    # mongo.close()
                    logo_id = util.get_uuid()
                    logger.info("gridfs logo_id=%s" % logo_id)

                    oss2 = oss2_helper.Oss2Helper()
                    headers = {"Content-Type": content_type}
                    oss2.put(str(logo_id), data, headers=headers)

                    conn.insert("insert sourcedeal_file(sourcedealId,filename,fileId,createTime) "
                                "values(%s,%s,%s,%s)",
                                cc_id, name, logo_id, msg["date"])
            conn.close()
            #exit()  #test

if __name__ == '__main__':
    while True:
        try:
            logger.info("Email start...")
            run()
            logger.info("End.")
            time.sleep(60)  # 1 mins
        except KeyboardInterrupt:
            exit(0)