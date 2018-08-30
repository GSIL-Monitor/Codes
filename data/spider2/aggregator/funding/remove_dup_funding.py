# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("remove_empty_funding", stream=True)
logger = loghelper.get_logger("remove_empty_funding")


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cids = conn.query("select companyId,count(*) from funding where (active is null or active='Y') and "
                    "(round=1105) group by companyId having count(*)>1")
    num = 0
    tot = len(cids)
    deleteids = []
    for cid in cids:
        company = conn.get("select * from company where (active is null or active!='N') and id=%s", cid["companyId"])
        if company is None:
            continue
        fundings = conn.query("select * from funding where companyId=%s and (round=1105) and "
                              "(active is null or active='Y') order by id", cid["companyId"])
        # fdates = []
        # remainfd = None
        # remainfi = "ww"
        remainId = fundings[0]["id"]
        fd = []
        for funding in fundings:
            if funding["id"]!= remainId:
                deleteids.append(funding["id"])
                fd.append(funding["id"])
            # fdates.append(str(funding["fundingDate"]))
            # if remainfd == "ww":
            #     remainfd = funding["fundingDate"]
            #     remainfi = funding["investment"]
            #     continue
            #
            # if remainfd is not None and funding["fundingDate"] is not None:
            #     if remainfi == funding["investment"] or remainfi is None or funding["investment"] is None:
            #         if (remainfd-funding["fundingDate"]).days > -20 and (remainfd-funding["fundingDate"]).days< 20:
            #             num += 1
            #             deleteids.append(funding["id"])
            #             logger.info("%s, %s, %s, %s, %s, %s, %s", company["code"],company["id"], remainfd, funding["fundingDate"],
            #                         remainfd-funding["fundingDate"], remainfi, funding["investment"])
            # elif remainfd is None:
            #     if remainfi == funding["investment"] or remainfi is None:
            #         num += 1
            #         deleteids.append(funding["id"])
            #         logger.info("******%s, %s, %s, %s, %s, %s, %s", company["code"], company["id"], remainfd,funding["fundingDate"],
            #                     0, remainfi, funding["investment"])
            #     remainfd = funding["fundingDate"]
            #     remainfi = funding["investment"]
        logger.info("Company %s,%s has dup funding %s, %s", company["code"],company["id"], remainId, fd)

    logger.info("%s/%s", num,tot)
    logger.info(len(deleteids))
    logger.info(deleteids)

    for id in deleteids:
        conn.update("update funding set active='N' where id=%s", id)

    conn.close()
