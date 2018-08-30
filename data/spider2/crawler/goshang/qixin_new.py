# -*- coding: utf-8 -*-
import sys, os, time, datetime

import requests
import json


reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db,util,url_helper,download, desc_helper
import name_helper

#logger
loghelper.init_logger("qixinbao_crawler", stream=True)
logger = loghelper.get_logger("qixinbao_crawler")

# url = 'http://api-sandbox.intsig.net'
url = 'https://api.intsig.net'
SOURCE = 13093
TYPE = 36008

conn = db.connect_torndb()

tmap = {
    4010: "网站", 4020: "微信公众号", 4030: "微博", 4040: "iOS", 4050: "Android"
}
rmap = {
    1000: '未融资',
    1010: '天使轮',
    1011: '天使轮',
    1020: 'pre-A',
    1030: 'A',
    1031: 'A+',
    1039: 'Pre-B',
    1040: 'B',
    1041: 'B+',
    1050: 'C',
    1060: 'D',
    1070: 'E',
    1080: 'F',
    1090: '后期阶段',
    1100: 'pre-IPO',
    1105: '新三板',
    1106: '新三板定增',
    1110: 'IPO',
    1120: '被收购',
    1130: '战略投资',
    1140: '私有化',
    1150: '债权融资',
    1160: '股权转让',
}

currentmap = {
    3010: "美元",
    3020: "人民币",
    3030: "新加坡元",
    3040: "欧元",
    3050: "英镑",
    3060: "日元",
    3070: "港币",
    3080: "澳元",
}
def get_amount(amount,precise):

    def pp(value):
        if value is None:
            return ''
        if value >= 1 and value < 10:
            return '数'
        elif value >= 10 and value <100:
            return '数十'
        elif value >= 100 and value < 1000:
            return '数百'
        elif value >= 1000 and value < 10000:
            return '数千'
        else:
            return ''

    if amount is None:
        return "金额不详"
    elif amount == 0:
        return "金额不详"
    elif float(amount)/float(100000000) > 1:
        if precise is None or precise == 'Y':
            return str(float(amount)/float(100000000))+'亿'
        else:
            return pp(float(amount) / float(100000000)) + '亿'
    elif float(amount)/float(10000) > 1:
        if precise is None or precise == 'Y':
            return str(float(amount) / float(10000)) + '万'
        else:
            return pp(float(amount) / float(10000)) + '万'
    else:
        return "金额不详"


def qixinCrawler(name,type, corporateIds=[],test=False):

    if type == 1:
        if len(corporateIds) == 0: return None,None
        (chinese, cccompany) = name_helper.name_check(name)
        if chinese is True:
            pass
        else:
            return None,None

        for corporateId in corporateIds:
            corporate_alias = conn.get("select * from corporate_alias where (active is null or active='Y') and "
                                       "corporateId=%s and name=%s limit 1", corporateId, name)
            # logger.info(corporateId)
            if corporate_alias is None:
                continue
            # logger.info(corporateId)
            corporate = conn.get("select * from corporate where id=%s and "
                                 "(active ='Y' or active ='A' or active is null)", corporateId)
            # logger.info(corporateId)
            if corporate is None:
                continue
            company = conn.get("select * from company where corporateId=%s and "
                               "(active ='Y' or active ='A' or active is null) limit 1",
                               corporateId)
            # logger.info(corporateId)
            if company is None:
                continue
            if company["name"] is None or company["name"].strip() == "" or \
                    len(desc_helper.count_other2(company["name"])) == len(company["name"]):
                logger.info("wwwwwwrong here")
                continue
            param = {}
            tags = [tt["name"] for tt in conn.query(" select t.name from company_tag_rel ctr join tag t "
                                                    "on ctr.tagId=t.id where ctr.companyId=%s and t.type=11012 and "
                                                    "(ctr.active='Y' or ctr.active is null)", company["id"])]
            baseinfo = {
                "company_name": name.strip(),
                "project_logo_url": "http://www.xiniudata.com/file/%s" % company["logo"] if company["logo"] is not None
                                                                                            else "",
                "project_name": company["name"].strip(),
                "finance_rounds": rmap[int(corporate["round"])] if (corporate["round"] is not None and
                                                                    rmap.has_key(int(corporate["round"]))) else "未融资",
                "website_url": company["website"] if company["website"] is not None and company["website"].strip() != ""
                                                    else "",
                "key_words": ",".join(tags) if len(tags) >0 else "",
                "introduction": company["description"],
            }
            # logger.info(baseinfo)
            fundings = conn.query("select * from funding where corporateId=%s and (active='Y' or active is null)",
                                  corporateId)
            bfi = []

            for funding in fundings:
                investors = [ii["name"] for ii in conn.query("select i.name from funding_investor_rel fir join "
                                                             "investor i "
                                                             "on fir.investorId=i.id where fir.fundingId=%s and "
                                                             "(fir.active is null or fir.active='Y') and "
                                                             "(i.active is null or i.active='Y')", funding["id"])]
                amount = get_amount(funding["investment"], funding["precise"])

                # logger.info("**************%s, %s -> %s", funding["investment"], funding["precise"], amount)
                fi = {
                    "date": str(funding["fundingDate"].date()) if funding["fundingDate"] is not None else "",
                    "round": rmap[int(funding["round"])] if (funding["round"] is not None and
                                                                    rmap.has_key(int(funding["round"]))) else "",
                    "amount":  amount,
                    "currency": currentmap[int(funding["currency"])] if (funding["currency"] is not None and
                                                                         currentmap.has_key(int(funding["currency"]))) else "",
                    "investor": ",".join(investors)

                }
                bfi.append(fi)
            baseinfo["finance_info"] = bfi

            param["base"] = baseinfo

            #members
            members = conn.query("select cmr.type,cmr.position,m.* from member m join company_member_rel cmr on "
                                 "m.id=cmr.memberId where cmr.companyId=%s and (cmr.active is null or cmr.active='Y')"
                                 " and (m.active='Y' or m.active is null)", company["id"])
            tcm = []
            for m in members:
                if int(m["type"]) not in [5010, 5020]: continue
                cm = {
                    "avatar_url": "http://www.xiniudata.com/file/%s" % m["photo"] if m["photo"] is not None else "",
                    "name": m["name"], "position": m["position"],
                    "education": m["education"], "introduction": m["description"], "work": m["work"]
                }
                tcm.append(cm)
            param["team"]= {"core_members":tcm}
            #comps
            coms = conn.query("select c.name from companies_rel cr join company c on cr.company2Id=c.id "
                              "where cr.companyId=%s and (c.active is null or c.active='Y') "
                              "order by cr.distance desc limit 10", company["id"])
            param["competitors"] = [{"project_name":c["name"]} for c in coms]
            #artifact
            products = []
            for tt in [4010,4020,4030,4040,4050]:
                if tt == 4010:
                    artifacts = conn.query("select name, description, type from artifact where companyId=%s and "
                                           "(active is null or active='Y') and type=%s "
                                           "order by rank limit 5", company["id"], tt)
                else:
                    artifacts = conn.query("select name, description, type from artifact where companyId=%s and "
                                           "(active is null or active='Y') and type=%s "
                                           "order by rank desc limit 5", company["id"], tt)

                for a in artifacts:
                    if a["name"] is None: a["name"] = ""
                    if a["description"] is None: a["description"] = ""
                    if a["name"].find("av") >= 0 or a["name"].find("AV") >= 0 or \
                            a["name"].find("性爱") >= 0 or a["name"].find("做爱") >= 0 or \
                            a["name"].find("澳门") >= 0 or a["name"].find("威尼斯") >= 0 or \
                            a["name"].find("男人")>=0 or a["name"].find("成人")>=0:
                        continue
                    if a["description"].find("av") >= 0 or a["description"].find("AV") >= 0 or \
                            a["description"].find("性爱") >= 0 or a["description"].find("做爱") >= 0 or \
                            a["description"].find("澳门") >= 0 or a["description"].find("威尼斯") >= 0 or \
                            a["description"].find("男人")>=0 or a["description"].find("成人")>=0:
                        continue
                    if tmap.has_key(a["type"]):
                        if a["type"] == 4010:
                            cchinese = desc_helper.count_other(a["name"]) + desc_helper.count_other(a["description"])
                            if len(cchinese) > 0:
                                logger.info("wrong luanma!!!!!: %s", a["name"])
                                continue

                        products.append({"name":a["name"], "description":a["description"], "kind": tmap[a["type"]]})
            param["products"] = products

            logger.info("products upload for %s|%s, %s", corporateId, len(products), len(str(products)))
            logger.info("tags: %s", param["base"]["key_words"])
            url_company = url+'/open/xiniu/venture/capital'
            try:
                if test is True:
                    for p in param:
                        logger.info(p)
                        if p == "products":
                            for pp in param[p]:
                                # logger.info(pp)
                                logger.info(json.dumps(pp, ensure_ascii=False, cls=util.CJsonEncoder))
                        else:
                            # logger.info(p)
                            logger.info(json.dumps(param[p], ensure_ascii=False, cls=util.CJsonEncoder))
                    return  None, None
                else:
                    # logger.info(json.dumps(param, ensure_ascii=False, cls=util.CJsonEncoder))
                    # exit()
                    # http://httpbin.org/posthttp://www.xiniudata.com/5977875df8716656636efb78/stat/gettest
                    # res = requests.post('http://httpbin.org/post', json=param)
                    res = requests.post(url_company, json=param)
                    # logger.info("\n\n\n\n")
                    # logger.info("result:")
                    # logger.info(json.dumps(param, ensure_ascii=False, cls=util.CJsonEncoder))
                    logger.info(res.text)
                    # logger.info("\n\n\n\n")
                    # conn.close()
                    return json.loads(res.text), json.dumps(param, ensure_ascii=False, cls=util.CJsonEncoder)
            except:
                pass

        # conn.close()
        return None,None

    elif type == 2:
        # conn = db.connect_torndb()
        url_investor = url+'/open/xiniu/venture/institution'
        investoras = conn.query("select * from investor_alias where verify='Y' and "
                                "(active is null or active!='N') and name=%s", name)
        if len(investoras) == 0:
            investoras = conn.query("select * from investor_alias where "
                                    "(active is null or active!='N') and name=%s", name)
        if len(investoras) > 0:
            for investora in investoras:
                investor = conn.get("select * from investor where (active is null or active!='N') and id=%s",
                                    investora["investorId"])

                if investor is not None:
                    try:
                        logger.info(investor)
                        param = {
                            "full_name": name,
                            "short_name": investor["name"] if investor["name"] is not None and investor["name"]!="" else name
                        }
                        res = requests.post(url_investor, json=param)
                        # conn.close()
                        return json.loads(res.text), json.dumps(param, ensure_ascii=False, cls=util.CJsonEncoder)
                    except:
                        return None, None
                        # conn.close()

        return None, None

    elif type == 3:
        try:
            # conn = db.connect_torndb()
            url_investor = url+'/open/xiniu/venture/institution'

            param = {
                "full_name": name,
                "short_name": name
            }
            res = requests.post(url_investor, json=param)
            # conn.close()
            return json.loads(res.text), json.dumps(param, ensure_ascii=False, cls=util.CJsonEncoder)
        except:
            return None, None


    else:
        return None, None

def save(company_name, content):
    if content is not None and content.has_key("errorCode") and content["errorCode"] == "" and \
       content.has_key("data") and isinstance(content["data"], dict):

        collection_content = {
            "date":datetime.datetime.now(),
            "source":SOURCE,
            "type":36008,
            "url":None,
            "content":content["data"],
            "key": company_name
        }

        mongo = db.connect_mongo()
        if mongo.raw.projectdata.find_one({"source":SOURCE, "type":TYPE, "key":company_name}) is not None:
            mongo.raw.projectdata.delete_one({"source":SOURCE, "type":TYPE, "key":company_name})
        mongo.raw.projectdata.insert_one(collection_content)
        mongo.close()

    elif content is not None and content.has_key("errorCode") and content["errorCode"] != "":
        mongo = db.connect_mongo()
        collection_name = mongo.info.gongshang_name
        collection_name.update_one({"name": company_name}, {'$set': {"errorCode": content["errorCode"]}})
        mongo.close()



def start_run():
    while True:
        logger.info("qixin crawler start...")


        mongo = db.connect_mongo()
        collection_name = mongo.info.gongshang_name
        cnames = list(collection_name.find({
            "type": 3,
            "$or": [
                {"lastCheckTime": None},
                {"lastCheckTime": {"$lt": datetime.datetime.now() - datetime.timedelta(days=4)}}
            ]
        }).limit(300))

        for cname in cnames:
            if cname["name"] is None or cname["name"].strip() == "":
                continue
            logger.info("crawler type 3: %s", cname["name"])
            if cname.has_key("corporateIds") and isinstance(cname["corporateIds"],list):
                r, u = qixinCrawler(cname["name"], 1, cname["corporateIds"])
                logger.info(r)
                save(cname["name"], r)
            collection_name.update_one({"_id": cname["_id"]},{'$set': {"lastCheckTime": datetime.datetime.now()}})

        cnames = list(collection_name.find({
            "type": 1,
            "$or": [
                {"lastCheckTime": None},
                {"lastCheckTime": {"$lt": datetime.datetime.now() - datetime.timedelta(days=2)}}
            ]
        }).limit(200))

        for cname in cnames:
            if cname["name"] is None or cname["name"].strip() == "":
                continue
            logger.info("crawler type 1: %s", cname["name"])
            r,u = qixinCrawler(cname["name"], 2)
            logger.info(r)
            save(cname["name"], r)
            collection_name.update_one({"_id": cname["_id"]},{'$set': {"lastCheckTime": datetime.datetime.now()}})

        cnames = list(collection_name.find({
            "type": 2,
            "$or": [
                {"lastCheckTime": None},
                {"lastCheckTime": {"$lt": datetime.datetime.now() - datetime.timedelta(days=4)}}
            ]
        }).limit(50))

        for cname in cnames:
            if cname["name"] is None or cname["name"].strip() == "":
                continue
            logger.info("crawler type 2: %s", cname["name"])
            r,u= qixinCrawler(cname["name"], 2)
            logger.info(r)
            save(cname["name"], r)
            collection_name.update_one({"_id": cname["_id"]}, {'$set': {"lastCheckTime": datetime.datetime.now()}})

        cnames = list(collection_name.find({
            "type": 5,
            "lastCheckTime": None
        }).limit(100))

        for cname in cnames:
            if cname["name"] is None or cname["name"].strip() == "":
                continue
            logger.info("crawler type 5: %s", cname["name"])
            r, u = qixinCrawler(cname["name"], 3)
            logger.info(r)
            save(cname["name"], r)
            collection_name.update_one({"_id": cname["_id"]}, {'$set': {"lastCheckTime": datetime.datetime.now()}})

        mongo.close()

        conn = db.connect_torndb()

        company_aliases = conn.query("select * from corporate_alias where gongshangCheckTime is null")

        for company in company_aliases:
            if company["name"] is None or company["name"].strip() == "":
                pass
            else:
                logger.info("crawler new company: %s", company["name"])
                r, u = qixinCrawler(company["name"], 3)
                logger.info(r)
                save(company["name"], r)
            sql = "update corporate_alias set gongshangCheckTime=now() where id=%s"
            conn.update(sql, company["id"])

        conn.close()

        logger.info("qixin crawler end...")

        time.sleep(1*10)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
        type = sys.argv[2]
        tt = sys.argv[3]
        if tt == 'a':
            test = True
        else:
            test = False
        infos = []
        mongo = db.connect_mongo()
        collection_name = mongo.info.gongshang_name
        cnames = list(collection_name.find({"name":name,"type":int(type)}))
        if int(type) in [1,2]:
            t = 2
            if len(cnames) == 0:
                logger.info("nnnn ooo name")
                cnames = [{"name":name}]
        elif int(type) in [5]:
            t = 3
        else:
            t = 1
        for ca in cnames:
            logger.info("%s,%s,%s",ca["name"], t, ca.get("corporateIds",[]))
            r, u = qixinCrawler(ca["name"], t, ca.get("corporateIds",[]), test)
            if r is not None and r.has_key("errorCode") and r["errorCode"] == "" and \
                r.has_key("data") and isinstance(r["data"], dict):
                logger.info(u)
                logger.info("\n\n\n")
                logger.info(r["data"])
                save(ca["name"],r)
                pass
            elif u is not None:
                logger.info("\n")
                logger.info("wrong: %s",r)
                # logger.info(u)
                logger.info(r["errorMsg"])
        mongo.close()
        # save(param, r)
    else:
        start_run()
        # conn = db.connect_torndb()
        #
        # company_aliases = [{"name":"河北聚精采电子商务股份有限公司","corporateIds" : [ 8293, 131631 ]}]
        # for ca in company_aliases:
        #     logger.info("caaaaa: %s", ca["name"])
        #     r,u = qixinCrawler(ca["name"], 1, ca["corporateIds"])
        #     if r is not None and r.has_key("errorCode") and r["errorCode"] == "" and \
        #         r.has_key("data") and isinstance(r["data"], dict):
        #         logger.info(u)
        #         logger.info("\n\n\n")
        #         logger.info(r["data"])
        #         pass
        #     elif u is not None:
        #         logger.info("\n")
        #         logger.info("wrong: %s",r)
        #         # logger.info(u)
        #         logger.info(r["errorMsg"])
        #
        # conn.close()
        # pass
