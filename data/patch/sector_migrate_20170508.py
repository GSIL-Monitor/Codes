# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("sector_migrate_20170508", stream=True)
logger = loghelper.get_logger("sector_migrate_20170508")

def process():
    conn = db.connect_torndb()
    #删除 B2B sectorId=18
    conn.execute("update user_sector set active='N',modifyUser=-1,modifyTime=now() where sectorId=18")
    conn.close()

    #合并 17->2, 20001->20000, 20002->20003
    replace_sector(17, 2)
    replace_sector(20001, 20000)
    replace_sector(20002, 20003)


def replace_sector(old_sector_id, new_sector_id):
    conn = db.connect_torndb()
    items = conn.query("select * from user_sector where (active is null or active='Y') and sectorId=%s", old_sector_id)
    for item in items:
        user_sector = conn.get("select * from user_sector where (active is null or active='Y') and sectorId=%s "
                               "and userId=%s limit 1", new_sector_id,item["userId"])
        if user_sector is None:
            conn.insert("insert user_sector(sectorId,userId,createUser,modifyUser,createTime,modifyTime) values(%s,%s,-1,-1,now(),now())",
                        new_sector_id, item["userId"])
        conn.execute("update user_sector set active='N',modifyUser=-1,modifyTime=now() where id=%s",item["id"])
    conn.close()


def process_company_sector():
    conn = db.connect_torndb()
    #删除 B2B sectorId=18
    conn.execute("update company_sector set active='N',modifyUser=-1,modifyTime=now() where sectorId=18")
    conn.close()

    #合并 17->2, 20001->20000, 20002->20003
    replace_company_sector(17, 2)
    replace_company_sector(20001, 20000)
    replace_company_sector(20002, 20003)


def replace_company_sector(old_sector_id, new_sector_id):
    conn = db.connect_torndb()
    items = conn.query("select * from company_sector where (active is null or active='Y') and sectorId=%s", old_sector_id)
    for item in items:
        company_sector = conn.get("select * from company_sector where (active is null or active='Y') and sectorId=%s "
                               "and companyId=%s limit 1", new_sector_id,item["companyId"])
        if company_sector is None:
            conn.insert("insert company_sector(sectorId,companyId,createUser,modifyUser,createTime,modifyTime) values(%s,%s,-1,-1,now(),now())",
                        new_sector_id, item["companyId"])
        conn.execute("update company_sector set active='N',modifyUser=-1,modifyTime=now() where id=%s",item["id"])
    conn.close()


if __name__ == "__main__":
    # process()
    process_company_sector()