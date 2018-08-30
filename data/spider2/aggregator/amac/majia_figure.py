# -*- coding: utf-8 -*-
import os, sys, re, json, time
import datetime
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import amac_util
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util, url_helper,email_helper,name_helper
import db

import find_investor_alias

#logger
loghelper.init_logger("majia", stream=True)
logger = loghelper.get_logger("majia")


DATE = None

def get_links(cids):
    links = []
    conn = db.connect_torndb()
    for cid in cids:
        # companies = conn.query("select * from company where corporateId=%s and (active is null or active='Y')", cid)
        # for c in companies:
            link = 'http://pro.xiniudata.com/validator/#/audit/investor/%s' % cid
            links.append(link)
    conn.close()
    return ";".join(links)


def dup_alias():
    tline = ""
    n = 0
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0
    conn = db.connect_torndb()
    cnames = conn.query("select name,count(*) as cnt from investor_alias where (active is null or active !='N') "
                        "and name is not null and name!='' and type=12010 group by name having cnt>1")
    logger.info(len(cnames))
    for cname in cnames:
        investor_ids = []
        investor_ids_un = []
        investor_aids_ver = []
        investor_as = conn.query(
            "select * from investor_alias where name=%s and (active is null or active !='N') and type=12010",
            cname["name"])
        for ia in investor_as:
            investor = conn.get("select * from investor where (active is null or active !='N') and id=%s", ia["investorId"])
            if investor is not None:
                investor_ids.append(investor["id"])
                if investor["id"] not in investor_ids_un:
                    investor_ids_un.append(investor["id"])
                if ia["verify"] == "Y":
                    investor_aids_ver.append(ia["id"])

        if len(investor_ids) > 1:
            n += 1
            logger.info("dup:%s -> %s", cname["name"], investor_ids)
            aa = "否"; ab = "否"; ac = "否"
            # line = "%s+++%s+++%s\n" % (cname["name"], ";".join([str(id) for id in investor_ids]),get_links(investor_ids))
            # tline += line
            if len(investor_ids_un) == 1:
                logger.info("dup:%s -> %s -- %s", cname["name"], investor_ids, "for same investor")
                aa = "是"
                ssinv = conn.get("select * from investor_alias where investorId=%s and name=%s and (active is null or active !='N') limit 1", investor_ids_un[0], cname["name"])
                logger.info("here we want to save: %s", ssinv["id"])
                conn.update(
                    "update investor_alias set active='N', modifyUser=-571 where id!=%s and type=12010 and name=%s",
                    ssinv["id"], cname["name"])
                # exit()
                n1 += 1
            if len(investor_aids_ver) == 1:
                logger.info("dup:%s -> %s -- %s %s", cname["name"], investor_ids, "for one verify", investor_aids_ver[0])
                ab = "是"
                conn.update("update investor_alias set active='N', modifyUser=-571 where id!=%s and type=12010 and name=%s", investor_aids_ver[0],cname["name"])
                # exit()
                n2 += 1
            if len(investor_aids_ver) == 0:
                logger.info("dup:%s -> %s -- %s", cname["name"], investor_ids, "for None verify")
                ac = "是"
                sid = investor_ids[0]
                f = 0
                for iid in investor_ids:
                    iinv = conn.get("select * from investor where (active is null or active !='N') and id=%s",
                                    iid)
                    if iinv["fundingCntFrom2017"] > f:
                        f = iinv["fundingCntFrom2017"]
                        sid = iid
                logger.info("here we want to save: %s", sid)
                conn.update(
                    "update investor_alias set active='N', modifyUser=-571 where investorId!=%s and type=12010 and name=%s",
                    sid, cname["name"])
                # exit()


                n3 += 1
            line = "%s+++%s+++%s+++%s+++%s+++%s\n" % (cname["name"], ";".join([str(id) for id in investor_ids]),
                                                      get_links(investor_ids), aa, ab, ac)
            tline += line

    logger.info("%s - %s - %s - %s - %s", n, n1, n2, n3, n4)
    fp2 = open("me.txt", "w")
    fp2.write(tline)
    content = '''<div>Dears,    <br /><br />

            附件是目前系统中存在重复的公司，请在后台搜索
            </div>
            '''
    fp2.close()
    path = os.path.join(sys.path[0], "me.txt")
    logger.info(path)
    email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "bamy@xiniudata.com",
                                ';'.join([i + '@xiniudata.com' for i in ["bamy"]]),
                                "重复机构检索--人工审查", content, path)
    fp2.close()
    conn.close()

def kuohao_alias():
    tline = ""
    conn = db.connect_torndb()
    n = 0; n1 = 0; n2 = 0; n3 =0; n4 = 0
    # cnames = conn.query("select * from investor_alias where (active is null or active !='N') and name like %s", '%(%')
    cnames = conn.query("select name,count(*) as cnt from investor_alias where (active is null or active !='N') "
                        "and (name like %s or name like %s) group by name", '%(%', '%)%')

    for cname in cnames:
        wname = cname["name"]
        investors = conn.query("select * from investor_alias where (active is null or active !='N') and name=%s", wname)
        for inv in investors:
            if inv["type"] != 12010: continue
            wid = inv["investorId"]
            investor = conn.get("select * from investor where (active is null or active !='N') and id=%s", wid)
            if investor is None: continue
            n1 += 1
            # logger.info("*****************name:%s",inv["name"])
            mnames =  [wname.replace("(", "（").replace(")", "）").strip()]
            # csameiid = ""
            investor_ids = []
            for mname in mnames:
                # i0 = conn.get("select * from investor_alias where name=%s and (active is null or active !='N') and "
                #               "investorId=%s limit 1", mname, wid)
                i0 = None
                if i0 is None:
                    i1s = conn.query("select * from investor_alias where name=%s and (active is null or active !='N')", mname)
                    for i1 in i1s:
                        iv1 = conn.get("select * from investor where (active is null or active !='N') and id=%s", i1["investorId"])
                        if iv1 is not None and iv1["id"] not in investor_ids:
                            investor_ids.append(iv1["id"])
                else:
                    if wid not in investor_ids:
                        investor_ids.append(wid)

            if len(investor_ids) > 0:
                if wid in investor_ids and len(investor_ids) == 1:
                    csameiid = "同一机构"
                    n2 += 1
                    conn.update("update investor_alias set active='N',modifyUser=-561 where id=%s",inv["id"])
                else:
                    csameiid = "多个机构"
                    n3 += 1
                    line = "%s+++%s+++%s\n" % (
                    cname["name"], ";".join([str(id) for id in [str(wid)] + investor_ids]), get_links([str(wid)] + investor_ids))
                    tline += line
                logger.info("%s - %s - %s - %s", wname, str(wid), ";".join([str(id) for id in investor_ids]), csameiid )
                n += 1
            else:
                (chinese, cccompany) = name_helper.name_check(mnames[0])
                if chinese is True:
                    n4 += 1
                    logger.info("update!!!!!")
                    conn.update("update investor_alias set name=%s,modifyUser=-561 where id=%s", mnames[0],inv["id"])
    logger.info("%s - %s - %s - %s - %s", n, n1, n2, n3, n4)

    fp2 = open("me.txt", "w")
    fp2.write(tline)
    content = '''<div>Dears,    <br /><br />

                附件是目前系统中存在重复的公司，请在后台搜索
                </div>
                '''
    fp2.close()
    path = os.path.join(sys.path[0], "me.txt")
    logger.info(path)
    email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "bamy@xiniudata.com",
                                ';'.join([i + '@xiniudata.com' for i in ["bamy"]]),
                                "重复机构检索--人工审查", content, path)
    fp2.close()
    conn.close()





if __name__ == "__main__":
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        dup_alias()
        # kuohao_alias()
        logger.info('end')



        time.sleep(60*60)
