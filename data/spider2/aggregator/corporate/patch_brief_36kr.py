# -*- coding: utf-8 -*-
import datetime
import os, sys
import time,json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import util
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper


#logger
loghelper.init_logger("patch_36kr", stream=True)
logger = loghelper.get_logger("patch_36kr")




if __name__ == '__main__':
    logger.info("Begin...")
    logger.info("funding 36kr repatch start ")
    conn = db.connect_torndb()
    (n1, n2, n3, n4, n5, n6, n7) = (0, 0, 0, 0, 0, 0, 0)
    # cs = conn.query("select * from company where (active is null or active='Y') and id=%s order by id", 248477)
    cs = conn.query("select * from company where (active is null or active='Y') and "
                    "((modifyTime is null and createTime<'2017-04-01') or modifyTime<'2017-01-01')")
    for cc in cs:
        n6 += 1
        sc = conn.get("select * from source_company "
                      "where (active is null or active='Y') and source=13022 and companyId=%s"
                      " and (brief is not null and brief !='') and (description is not null and description!='') "
                      "limit 1", cc["id"])

        if sc is not None:
            n5 += 1
            if cc["brief"] != sc["brief"] or cc["description"]!=sc["description"]:
                n4 += 1
                logger.info("company: %s|%s", cc["code"],cc["id"])
                logger.info("a: %s|%s",cc["brief"], cc["description"])
                logger.info("a: %s|%s", sc["brief"], sc["description"])
            # if cc["id"] not in [190372]:
            #     continue
                conn.update("update company set brief=%s,description=%s where id=%s",
                            sc["brief"], sc["description"],
                            cc["id"])
            # logger.info("done")
        # if len(sfs) > 0:
        #     n1 += 1
        #     if check_ok(cc) is True:
        #         n2 += 1
        #         logger.info("company %s|%s|%s could add funding from 36kr",cc["code"],cc["name"],cc["id"])
        #         n3 += len(sfs)
        #         flag = True
        #         for sf in sfs:
        #             logger.info(sf)
        #             flag = aggregate1(sf, cc["id"],cc["corporateId"])
        #             if flag is False:
        #                 break
        #         if flag is True:
        #             n5 += 1
        #             logger.info("New funding added for company : %s", cc["name"])
        #             set_processed(sfs)
        #         else:
        #             logger.info("Something wrong with aggregating funding for company : %s|%s", cc["code"], cc["id"])
        #             n4 += 1
        #             #set_processed(sfs)
        #             exit()
        #         pass

    logger.info("funding aggregator end.")
    logger.info("%s/%s/%s/%s/%s/%s", n1, n2, n3, n4, n5, n6)

    conn.close()
    logger.info("End.")