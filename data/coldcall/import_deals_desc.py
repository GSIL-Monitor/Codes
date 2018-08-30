# -*- coding: utf-8 -*-
import os, sys

reload(sys)

sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

#logger
loghelper.init_logger("import_deals_desc", stream=True)
logger = loghelper.get_logger("import_deals_desc")

if __name__ == '__main__':
    conn = db.connect_torndb()
    dfile = open("xiniu_deals.txt")
    content = dfile.read()
    dfile.close()
    deals = content.split("******")
    for deal in deals:
        t = deal.split("|||")
        code = t[0]
        if code == "":
            continue
        assignee_email = t[2]
        desc = t[7].strip()
        comment = t[8].strip()
        mt = t[9]

        assigneeId = None
        if assignee_email != "":
            user = conn.get("select * from user where email=%s", assignee_email)
            if user:
                assigneeId = user["id"]

        if assigneeId is None:
            continue

        c = conn.get("select * from company where code=%s", code)
        if c is None:
            continue
        d = conn.get("select * from deal where organizationId=1 and companyId=%s",c["id"])
        if d is None:
            logger.info("Deal not found!")
        else:
            if desc != "":
                n = conn.get("select * from deal_note where dealId=%s and userId=%s and note=%s", d["id"], assigneeId, desc)
                if n is None:
                    logger.info("dealId=%s, assigneeId=%s", d["id"], assigneeId)
                    conn.insert("insert deal_note(dealId,userId,note,iom,active,createTime) values(%s,%s,%s,'N','Y',%s)",
                                d["id"],assigneeId,desc,mt)
            if comment != "":
                n = conn.get("select * from deal_note where dealId=%s and userId=%s and note=%s", d["id"], assigneeId, comment)
                if n is None:
                    logger.info("dealId=%s, assigneeId=%s", d["id"], assigneeId)
                    conn.insert("insert deal_note(dealId,userId,note,iom,active,createTime) values(%s,%s,%s,'N','Y',%s)",
                                d["id"],assigneeId,comment,mt)

    conn.close()