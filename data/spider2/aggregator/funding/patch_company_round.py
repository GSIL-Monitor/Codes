# -*- coding: utf-8 -*-
#重新聚合融资信息
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("patch_company_round", stream=True)
logger = loghelper.get_logger("patch_company_round")


def process(corporate_id):
    logger.info("corporate id: %s", corporate_id)
    conn = db.connect_torndb()
    funding = conn.get("select * from funding where corporateId=%s and (active is null or active !='N') order by fundingDate desc limit 1",
                       corporate_id)
    if funding is not None:
        # corporate = conn.get("select * from corporate where id=%s", corporate_id)
        # if corporate is not None:
            conn.update("update corporate set round=%s, roundDesc=%s where id=%s",
                        funding["round"],funding["roundDesc"],corporate_id)
    else:
        pass
    conn.close()

def process2(corporate_id):
    global n
    global n1
    global n2
    # logger.info("corporate id: %s", corporate_id)
    conn = db.connect_torndb()
    funding = conn.get("select * from funding where corporateId=%s and (active is null or active !='N') "
                       "and round in (1105,1110) limit 1",
                       corporate_id)
    if funding is not None:
        # corporate = conn.get("select * from corporate where id=%s", corporate_id)
        # if corporate is not None:
            company = conn.get("select * from company where corporateId=%s and (active is null or active !='N') "
                               "limit 1", corporate_id)
            if company is not None:
                locationId= company["locationId"]
                if locationId is not None:
                    if locationId >0 and locationId<371:
                        istatus = 72030
                        ilocationId = 340
                        n1 += 1
                        conn.update("update corporate set ipoStatus=%s, ipoLocation=%s where id=%s", istatus,
                                    ilocationId, corporate_id)
                    elif locationId >=371:
                        istatus = 72030
                        ilocationId = 421
                        n2 += 1
                        conn.update("update corporate set ipoStatus=%s, ipoLocation=%s where id=%s", istatus,
                                    ilocationId, corporate_id)
                    else:
                        n += 1
                        logger.info("wrong corporate:%s|%s|%s",corporate_id, company["name"], company["code"])
                else:
                    n += 1
                    logger.info("wrong corporate:%s|%s|%s", corporate_id, company["name"], company["code"])

    else:
        pass
    conn.close()

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    # cs = conn.query("select id from corporate where (active is null or active !='N') and ipoStatus is null order by id")
    #cs = conn.query("select id from company where code='ejiajie'")
    cs = conn.query("select distinct corporateId from funding where (active is null or active !='N') "
                    "and round in (1105,1110)")
    conn.close()
    n = 0
    n1 = 0
    n2 = 0

    for c in cs:
        # company_id= c["id"]
        corporate = conn.get("select * from corporate where id=%s and (active is null or active !='N') "
                             "and ipoStatus is null", c["corporateId"])
        if corporate is None: continue

        corporate_id =  c["corporateId"]
        process2(corporate_id)

    logger.info("End.%s/%s/%s",n1,n2,n)