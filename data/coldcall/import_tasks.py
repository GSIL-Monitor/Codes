# -*- coding: utf-8 -*-
import os, sys

reload(sys)

sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

#logger
loghelper.init_logger("import_tasks", stream=True)
logger = loghelper.get_logger("import_tasks")

if __name__ == '__main__':
    conn = db.connect_torndb()
    dfile = open("xiniu_tasks.txt")
    content = dfile.read()
    dfile.close()
    tasks = content.split("******")
    for task in tasks:
        t = task.split("|||")
        code = t[0]
        if code == "":
            continue
        email = t[1]
        startDate = t[2]
        toDate = t[3]
        content = t[4]

        userId = None
        if email != "":
            user = conn.get("select * from user where email=%s", email)
            if user:
                userId = user["id"]
        if userId is None:
            continue

        c = conn.get("select * from company where code=%s", code)
        if c is None:
            continue
        d = conn.get("select * from deal where organizationId=1 and companyId=%s",c["id"])
        if d is None:
            continue
        dealId = d["id"]
        logger.info("%s, %s, %s, %s, %s",dealId,userId,startDate,toDate,content)

        note = conn.get("select * from deal_note where dealId=%s and userId=%s and createTime=%s",dealId,userId,toDate)
        if note is None:
            conn.insert("insert deal_note set dealId=%s,userId=%s,note=%s,fromDate=%s,toDate=%s,iom='Y',active='Y',createTime=%s,modifyTime=%s",
                        dealId,userId,content,startDate,toDate,toDate,toDate)
    conn.close()