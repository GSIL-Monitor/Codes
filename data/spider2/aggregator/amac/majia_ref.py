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


def update():
    # tline = ""
    n = 0
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0
    conn = db.connect_torndb()
    fp = open("majia_ref.txt")
    lines = fp.readlines()
    for line in lines:
        n += 1
        names = [name for name in line.strip().split("+++")]
        if len(names) != 5:
            # logger.info(line)
            continue
        id = names[0]
        name = names[1]
        ver = names[2]
        act = names[3]
        modiu = names[4]
        if act == "None": act = None
        if modiu == "None": modiu = None

        inv = conn.get("select * from investor_alias where id=%s and name=%s", id, name)
        if inv is None:
            n1 += 1
            logger.info("%s|%s", id,name)
            continue
        # logger.info(modiu)
        if inv["modifyUser"] is None or modiu is None or int(inv["modifyUser"]) != int(modiu):
            if inv["active"] != act:
                n2 += 1
                # logger.info("here2 : %s|%s", id,name)
                # conn.update("update investor_alias set active=%s, modifyUser=%s where id=%s", act, modiu, id)
            else:
                n3 += 1
                # logger.info("here3 : %s|%s", id, name)
                # conn.update("update investor_alias set modifyUser=%s where id=%s", modiu, id)
        else:
            # logger.info("%s|%s", id, name)
            n4 += 1

    logger.info("%s - %s - %s - %s - %s", n, n1, n2, n3, n4)
    # fp2 = open("me.txt", "w")
    # fp2.write(tline)
    # content = '''<div>Dears,    <br /><br />
    #
    #         附件是目前系统中存在重复的公司，请在后台搜索
    #         </div>
    #         '''
    # fp2.close()
    # path = os.path.join(sys.path[0], "me.txt")
    # logger.info(path)
    # email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "bamy@xiniudata.com",
    #                             ';'.join([i + '@xiniudata.com' for i in ["bamy"]]),
    #                             "重复机构检索--人工审查", content, path)
    # fp2.close()
    conn.close()

def export_data():
    tline = ""
    n = 0
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0
    conn = db.connect_torndb()
    investors = conn.query("select * from investor_alias")
    for i in investors:
        line = "%s+++%s+++%s+++%s+++%s\n" % (i["id"],i["name"],i["verify"],i["active"],i["modifyUser"])
        n += 1
        tline += line
    logger.info("%s - %s - %s - %s - %s", n, n1, n2, n3, n4)

    fp2 = open("me.txt", "w")
    fp2.write(tline)
    content = '''<div>Dears,    <br /><br />

                附件是目前系统中存在重复的公司，请在后台搜索
                </div>
                '''
    fp2.close()
    # path = os.path.join(sys.path[0], "me.txt")
    # logger.info(path)
    # email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "bamy@xiniudata.com",
    #                             ';'.join([i + '@xiniudata.com' for i in ["bamy"]]),
    #                             "重复机构检索--人工审查1", content, path)
    # fp2.close()
    conn.close()





if __name__ == "__main__":
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        # dup_alias()
        # kuohao_alias()
        # export_data()
        update()
        logger.info('end')



        time.sleep(60*60)
