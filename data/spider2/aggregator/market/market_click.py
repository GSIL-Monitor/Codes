# -*- coding: utf-8 -*-
import os, sys, time

import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper



#logger
loghelper.init_logger("mcheck", stream=True)
logger = loghelper.get_logger("mcheck")

def click(companyId, userId):
    conn = db.connect_torndb()
    artifacts = conn.query("select * from artifact where (active is null or active='Y') and companyId=%s and "
                           "modifyUser is null", companyId)
    a_4010 = [a["id"] for a in artifacts if a["type"] == 4010]
    a_4040 = [a["id"] for a in artifacts if a["type"] == 4040]
    a_4050 = [a["id"] for a in artifacts if a["type"] == 4050]
    a_4020 = [a["id"] for a in artifacts if a["type"] == 4020]
    a_4030 = [a["id"] for a in artifacts if a["type"] == 4030]
    checkflag = False
    if len(a_4010) < 3:  m_click(a_4010,userId, "artifact")
    else: checkflag = True
    if len(a_4040) < 5:  m_click(a_4040, userId, "artifact")
    else: checkflag = True
    if len(a_4050) < 5:  m_click(a_4050, userId, "artifact")
    else: checkflag = True
    if len(a_4020) < 2:  m_click(a_4020, userId, "artifact")
    else: checkflag = True
    if len(a_4030) < 2:  m_click(a_4030, userId, "artifact")
    else: checkflag = True


    memberRels = conn.query("select * from company_member_rel where (active is null or active='Y') and companyId=%s",
                            companyId)
    m_ids = [mr["memberId"] for mr in memberRels]
    m_click(m_ids, userId, "member")
    conn.close()
    return  checkflag

def m_click(ids, userId, type):
    conn = db.connect_torndb()
    for id in ids:
        if type == "artifact":
            conn.update("update artifact set modifyUser=%s where id=%s",userId, id)
        else:
            conn.update("update member set modifyUser=%s where id=%s", userId, id)
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        companyId = int(sys.argv[1])
        userId = int(sys.argv[2])
        flag = click(companyId, userId)
        if flag is True:
            logger.info("need to take a further look at %s", companyId)
    else:
        pass