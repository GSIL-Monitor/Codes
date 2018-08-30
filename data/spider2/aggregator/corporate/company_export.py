# -*- coding: utf-8 -*-
#删除无金额和投资人的记录
import os, sys
import time
import json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("export_company", stream=True)
logger = loghelper.get_logger("export_company")

def get_code(id):
    conn = db.connect_torndb()
    c = conn.get("select * from company where id=%s", id)
    if c is None:
        exit()
    conn.close()
    return c

def get_links(cids):
    links = []
    for cid in cids:
        link = 'http://dev.xiniudata.com/#/company/%s/overview' % get_code(cid)["code"]
        links.append(link)
    return ";".join(links)


if __name__ == '__main__':
    logger.info("Begin...")
    num = 0
    conn = db.connect_torndb()
    tgs = conn.query("select * from tag where type=11012 and (active is null or active='Y')")
    tags = {}
    for tg in tgs:
        tags[tg["id"]] = tg["name"]

    fp = open("company.txt", "w")
    # companies = conn.query("select * from company where (active is null or active='Y')")
    # for company in companies:
    #     if company["corporateId"] is None or company["corporateId"] == "":
    #         continue
    #     name = company["name"]
    #     fullNames = []
    #     websites = []
    #     round = None
    #     fields = []
    #     location = None
    #     edate = None
    #     desc = None
    #     brief = None
    #
    #     corporate_aliases = conn.query("select * from corporate_alias where corporateId=%s and type=12010"
    #                                    " and (active is null or active='Y')", company["corporateId"])
    #     [fullNames.append(ca["name"]) for ca in corporate_aliases if ca["name"] is not None and
    #       ca["name"].strip() != "" and ca["name"] not in fullNames]
    #
    #     if company["website"] is not None and company["website"].strip() != "":
    #         websites.append(company["website"])
    #
    #     artifacts = conn.query("select * from artifact where companyId=%s and type=4010"
    #                            " and (active is null or active='Y')", company["id"])
    #     [websites.append(web["link"]) for web in artifacts if web["domain"] is not None and web["link"] not in websites]
    #
    #     round = company["round"]
    #     edate = company["establishDate"]
    #     desc = company["description"]
    #     brief = company["brief"]
    #     if company["locationId"] is not None:
    #         lc = conn.get("select * from location where locationId=%s", company["locationId"])
    #         if lc is not None:
    #             location = lc["locationName"]
    #
    #     company_tags = conn.query("select * from company_tag_rel where (active is null or active='Y') and companyId=%s",
    #                               company["id"])
    #     for ct in company_tags:
    #         if ct["tagId"] is not None and tags.has_key(ct["tagId"]) is True:
    #             if tags[ct["tagId"]] not in fields: fields.append(tags[ct["tagId"]])
    #
    #
    #     # line = "%s###%s###%s###%s###%s###%s###%s###%s###%s\n" % (name, "++".join(fullNames) if len(fullNames)>0 else " ",
    #     #                                                "++".join(websites) if len(websites)>0 else " ",
    #     #                                                round if round is not None else " ",
    #     #                                                edate if edate is not None else " ",
    #     #                                                location if location is not None else " ",
    #     #                                                "++".join(fields) if len(fields)>0 else " ",
    #     #                                                desc if desc is not None else " ",
    #     #                                                brief if brief is not None else " ",
    #     #                                                )
    #     item = {
    #         "name": name,
    #         "fullNames": fullNames,
    #         "website": websites,
    #         "round": round,
    #         "establishDate": str(edate) if edate is not None else None,
    #         "location": location,
    #         "fields": fields,
    #         "desc": desc,
    #         "brief": brief
    #     }
    #     line = json.dumps(item)
    #     logger.info(line)
    #     fp.write(line)
    #     num += 1

    # fp = open("investor.txt", "w")
    # for investor in investors:
    #     desc = None
    #     if conn.get("select * from funding_investor_rel where investorId=%s limit 1", investor["id"]) is not None:
    #
    #         if investor["description"] is not None:
    #             desc = investor["description"].replace("\n"," ").replace("\b", " ").replace("\r", " ").replace(" ","")
    #             # " ".join(investor["description"].split())
    #         num += 1
    #         line = "%s####%s####%s####%s\n" %(investor["id"],investor["name"],desc,investor["website"])
    #         fp.write(line)
    #
    # fp.close()
    # conn.close()

    # mongo = db.connect_mongo()
    # collection_org = mongo.fellowPlus.org
    # fp = open("investor_f.txt", "w")
    # orgs = list(collection_org.find({}))
    # for org in orgs:
    #     if org.has_key("org_name") is False or org["org_name"] is None or org["org_name"].strip() == "":continue
    #     num += 1
    #     line = "%s\n" %(org["org_name"])
    #     fp.write(line)


    mongo = db.connect_mongo()
    collection_org = mongo.aggreTest.agg

    orgs = list(collection_org.find({}))
    for org in orgs:
        company = get_code(org["companyId"])
        if org.has_key("method1") is True:
            link ='http://dev.xiniudata.com/#/company/%s/overview' % company["code"]
            links1 = get_links(org["method1"]["companyIds"])
            links2 = get_links(org["method2"]["companyIds"])
            links3 = get_links(org["method3"]["companyIds"])
            line = "%s+++%s+++%s+++%s+++%s+++%s+++%s+++%s+++%s\n" % (company["code"], company["name"], link,
                                                                     len(org["method1"]["companyIds"]), links1,
                                                                     len(org["method2"]["companyIds"]), links2,
                                                                     len(org["method3"]["companyIds"]), links3)
            fp.write(line)
            num+=1




    mongo.close()
    conn.close()
    fp.close()
    logger.info("num: %s", num)
    logger.info("End.")