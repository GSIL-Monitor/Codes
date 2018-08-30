# -*- coding: utf-8 -*-
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper, hz, desc_helper

#logger
loghelper.init_logger("Member_data_clean", stream=True)
logger = loghelper.get_logger("Member_data_clean")

if __name__ == "__main__":
    conn = db.connect_torndb()
    start = 0
    while True:
        membertitles = list(conn.query("select * from company_member_rel where (active is null or active='Y') and (type not in (5010,5020,5030,5040) or type is null) order by id limit %s, 1000", start))
        if len(membertitles) == 0:
            break
        for title in membertitles:
            type = name_helper.position_check(title["position"])
            logger.info("%s->%s", title["position"], type)
            conn.update("update company_member_rel set type=%s,modifyTime=now(),modifyUser=139 where id=%s", type, title["id"])

        #break

    while True:
        membertitles = list(conn.query("select * from source_company_member_rel where type not in (5010,5020,5030,5040) or type is null order by id limit %s, 1000", start))
        if len(membertitles) == 0:
            break
        for title in membertitles:
            type = name_helper.position_check(title["position"])
            logger.info("%s->%s", title["position"], type)
            conn.update("update source_company_member_rel set type=%s,modifyTime=now() where id=%s", type, title["id"])

            # break

    conn.close()