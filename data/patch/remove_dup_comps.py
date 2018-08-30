# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("remove_dup_comps", stream=True)
logger = loghelper.get_logger("remove_dup_comps")


def process():
    conn = db.connect_torndb()
    items = conn.query("select companyId,company2id,count(*) cnt from companies_rel where active is null or active='Y' group by companyId,company2id having cnt>1")
    for item in items:
        comps = conn.query("select * from companies_rel where (active is null or active='Y') and"
                           " companyId=%s and company2id=%s", item["companyId"], item["company2id"])
        for comp in comps[1:]:
            logger.info("remove id: %s", comp["id"])
            conn.execute("delete from companies_rel where id=%s", comp["id"])

    conn.close()



if __name__ == "__main__":
    process()