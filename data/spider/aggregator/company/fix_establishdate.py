# -*- coding: utf-8 -*-
import os, sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("funding_remove_dup", stream=True)
logger = loghelper.get_logger("funding_remove_dup")

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cs = conn.query("select * from company where establishDate is null order by id")
    for c in cs:
        #logger.info(c)
        logger.info("%s-%s", c["id"], c["code"])
        company_id= c["id"]
        gongshang = conn.get("select g.* from gongshang_base g join company_alias a on g.companyAliasId=a.id \
                             join company c on a.companyId=c.id where c.id=%s order by g.establishTime limit 1", company_id)
        if gongshang is not None:
            conn.update("update company set establishDate=%s where id=%s", gongshang["establishTime"], company_id)
        else:
            fp = conn.get("select * from footprint where companyId=%s order by footDate limit 1", company_id)
            if fp is not None:
                conn.update("update company set establishDate=%s where id=%s", fp["footDate"],company_id)

    conn.close()
    logger.info("End.")





