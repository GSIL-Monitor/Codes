# -*- coding: utf-8 -*-
# 工商探测发现的funding的publishDate应该为空，除非之后有媒体报道，但现在后台处理不对
import os, sys
import datetime, time
from bson import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_funding_publishdate", stream=True)
logger = loghelper.get_logger("patch_funding_publishdate")

def main():
    conn = db.connect_torndb()
    items = conn.query("select id,companyId,publishDate,gsDetectdate "
                       "from funding where "
                       "gsDetectdate is not null and "
                       "publishDate is not null and "
                       "publishDate<=gsDetectdate and "
                       "source=69002")
    for item in items:
        logger.info("id: %s, companyId: %s, publishDate: %s, gsDetectdate: %s",
                    item["id"], item["companyId"], item["publishDate"], item["gsDetectdate"])
        conn.update("update funding set publishdate=null where id=%s", item["id"])
        # exit()
    conn.close()

if __name__ == "__main__":
    main()