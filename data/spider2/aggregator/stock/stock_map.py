# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
import stock_aggregate
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
#logger
loghelper.init_logger("stock_map", stream=True)
logger = loghelper.get_logger("stock_map")

def find_company_by_name(full_name, short_name):
    companyIds = []
    full_name = name_helper.company_name_normalize(full_name)
    conn = db.connect_torndb()
    companies = conn.query("select * from company where fullName=%s and (active is null or active !='N') order by id desc", full_name)
    companyIds.extend([company["id"] for company in companies if company["id"] not in companyIds])
    # logger.info("a: %s",companyIds)
    companies2 = conn.query( "select * from company where (name=%s or name=%s) and (active is null or active !='N') order by id desc", full_name, short_name)
    companyIds.extend([company["id"] for company in companies2 if company["id"] not in companyIds])
    # logger.info("b: %s", companyIds)
    company_alias = conn.query("select distinct a.companyId from company_alias a join company c on c.id=a.companyId where (c.active is null or c.active !='N') \
                               and (a.active is null or a.active !='N') and (a.name=%s or a.name=%s) order by c.id desc", full_name, short_name)
    companyIds.extend([company["companyId"] for company in company_alias if company["companyId"] not in companyIds])
    # logger.info("c: %s", companyIds)
    return companyIds


def check_funding(stock, stock_sname, cids):
    mcids = []
    conn = db.connect_torndb()
    for cid in cids:
        neeqf = conn.get("select * from funding where companyId=%s and (active is null or active='Y') and round=1105 limit 1",cid)
        if neeqf is None:
            # logger.info("stock: %s|%s, company:%s missing funding", stock, stock_sname, cid)
            mcids.append(int(cid))
    conn.close()
    return mcids

def ipo():
    conn = db.connect_torndb()
    ipos = conn.query("select * from funding where (active is null or active='Y') and round=1110 order by id")
    ids = [int(ipo["companyId"]) for ipo in ipos]
    conn.close()
    return ids

def insert(company_ids,stock_name, stock_code, listtime):
    ldate = datetime.datetime.strptime(listtime,"%Y%m%d")
    data = {
        "name": "新三板: " +stock_name,
        "processStatus": 0,
        "items": [{
            "sort": 1,
            "brief": "http://www.neeq.com.cn/nq/detailcompany.html?companyCode=%s&typeId=1&typename=G" % stock_code,
            "round": "新三板"
        },{
                "sort": 1.01,
                "brief": "挂牌时间: %s" % ldate,
                "round": "新三板"
            }
        ],
        "company": company_ids,
        "news_date": datetime.datetime.now() - datetime.timedelta(hours=8),
        "news_id": [],
        "createTime": datetime.datetime.now() - datetime.timedelta(hours=8)
    }

    # print data
    mongo = db.connect_mongo()
    mongo.raw.funding.insert(data)
    mongo.close()

if __name__ == '__main__':
    logger.info("Begin...")
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    stocks = list(collection.find({"source":13400,"key_int":832871}))
    # webs = list(collection_website.find({"$or": [{"websiteCheckTime": None}, {"websiteCheckTime": {"$lt": daysago}}]}, limit=10))
    mongo.close()
    ipocids = ipo()
    num =0; num1= 0; total = 0; mnum0 = 0; mnum1 = 0
    for stock in stocks:
        total += 1
        if stock["content"].has_key("baseinfo") is False: continue
        name = stock["content"]["baseinfo"]["name"]
        shortname = stock["content"]["baseinfo"]["shortname"]
        # ids = find_company_by_name(name,shortname)
        phone = stock["content"]["baseinfo"]["phone"]
        if phone is not None and phone.find("-") !=-1 and len(phone.split("-")[0]):
            locationIds = stock_aggregate.get_locations(str(phone.split("-")[0]))
            ids = stock_aggregate.find_companies(name, shortname, locationIds)
        else:
            logger.info("aaaaaaaaaaaaaaaa : %s/%s", name, phone)
            ids = find_company_by_name(name, shortname)
        if len(ids)> 0:
            num1 += 1
            for id in ids:
                if id in ipocids:
                    logger.info("stock: %s|%s, mapping companys: %s wrong funding", name,shortname,id)
                    # insert([id],name+"|"+shortname,stock["content"]["baseinfo"]["code"],stock["content"]["baseinfo"]["listingDate"])
                    # exit()
                    num += 1
            mcids = check_funding(name,shortname,ids)
            if len(mcids) == 0: pass
            else:
                if len(ids) == 1: mnum0 += 1
                else:
                    logger.info("stock: %s|%s, mapping multi companys: %s with missing funding", name, shortname, ids)
                    # insert(ids, name + "|" + shortname, stock["content"]["baseinfo"]["code"],stock["content"]["baseinfo"]["listingDate"])
                    mnum1 += 1
                    # if mnum1 >= 50:
                    #     exit()

    logger.info("num: %s/%s/%s/%s/%s", num,mnum0, mnum1 ,num1, total)
    logger.info("End.")