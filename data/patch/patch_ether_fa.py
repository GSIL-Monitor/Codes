# -*- coding: utf-8 -*-
import os, sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_ether_fa", stream=True)
logger = loghelper.get_logger("patch_ether_fa")


# 删除重复的FA信息
def main():
    conn = db.connect_torndb()
    items = conn.query("select companyId,count(*) cnt from company_fa where companyId is not null and source=13100 "
                       "and (active is null or active='Y')"
                       "group by companyId having cnt>1")
    for item in items:
        fas = conn.query("select * from company_fa where companyId=%s and source=13100 "
                         "and (active is null or active='Y') "
                         "order by publishDate desc", item["companyId"])
        for fa in fas[1:]:
            logger.info("delete company_fa id: %s", fa["id"])
            conn.update("update company_fa set active='N' where id=%s", fa["id"])
    conn.close()

if __name__ == "__main__":
    main()
