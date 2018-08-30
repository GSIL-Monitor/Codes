# -*- coding: utf-8 -*-
import os, sys

reload(sys)

sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

#logger
loghelper.init_logger("import_deals", stream=True)
logger = loghelper.get_logger("import_deals")

if __name__ == '__main__':
    conn = db.connect_torndb()
    conn.execute("update deal set status=19000")
    dfile = open("xiniu_deals.txt")
    content = dfile.read()
    dfile.close()
    deals = content.split("******")
    for deal in deals:
        t = deal.split("|||")
        code = t[0]
        if code == "":
            continue
        status = int(t[1])
        assignee_email = t[2]
        sponsor_email = t[3]
        assigneeId = None
        sponsorId = None
        if assignee_email != "":
            user = conn.get("select * from user where email=%s", assignee_email)
            if user:
                assigneeId = user["id"]
        if sponsor_email != "":
            user = conn.get("select * from user where email=%s", sponsor_email)
            if user:
                sponsorId = user["id"]
        logger.info("%s, %s, %s, %s",code,status,assigneeId,sponsorId)

        c = conn.get("select * from company where code=%s", code)
        if c is None:
            continue
        d = conn.get("select * from deal where organizationId=1 and companyId=%s",c["id"])
        if d is None:
            logger.info("Deal not found!")
        else:
            conn.update("update deal set declineStatus=18010,status=%s,assignee=%s,sponsor=%s where id=%s",
                        status, assigneeId, sponsorId, d["id"])
    conn.close()