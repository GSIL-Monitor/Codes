# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("patch_member_desc", stream=True)
logger = loghelper.get_logger("patch_member_desc")

conn = None


'''
杜强，烯牛数据CTO。
格式就是：名字+，+项目名称+职位+。
'''
def main():
    conn = db.connect_torndb()
    members = conn.query("select * from member where (description is null or description='') "
                         "and (active is null or active!='N') "
                         "order by id desc")
    for member in members:
        member_id = member["id"]
        rels = list(conn.query("select * from company_member_rel where (active is null or active='Y') and "
                         "memberId=%s and position is not null and position !=''",
                               member_id))
        if len(rels) == 1:
            position = rels[0]["position"]
            if position is not None and position != "":
                company = conn.get("select * from company where id=%s",rels[0]["companyId"])
                if company["active"] in [None,'Y']:
                    description = u"%s，%s%s。" % (member["name"], company["name"], rels[0]["position"])
                    logger.info(description)
                    conn.update("update member set description=%s where id=%s", description, member_id)
                    exit(0)
    conn.close()


if __name__ == "__main__":
    main()