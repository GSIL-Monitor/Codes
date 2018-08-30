# -*- coding: utf-8 -*-
# 删除无金额和投资人的记录
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

# logger
loghelper.init_logger("export_audit", stream=True)
logger = loghelper.get_logger("export_audit")

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

companyStatusMap = {
    2010: '正常',
    2015: '融资中',
    2020: '已关闭',
    2025: '停止更新',
    0: '正常',
}


def getinfo(companyId, corporateId):
    info = ""
    verfyinfo = ""
    conn = db.connect_torndb()
    cor = conn.query("select * from corporate where (active is null or active='Y')"
                     " and verify is null and id=%s", corporateId)
    if len(cor) > 0: verfyinfo += "corporate "
    comp = conn.query("select * from company where (active is null or active='Y')"
                      " and verify is null and id=%s", companyId)
    if len(comp) > 0: verfyinfo += "基本信息 "
    fundings = conn.query("select * from funding f left join corporate c on f.corporateId=c.id "
                          "where f.corporateId=%s and (c.active is null or c.active='Y')  and "
                          "(f.active is null or f.active='Y') and f.verify is null", corporateId)
    if len(fundings) > 0: verfyinfo += "融资 "
    artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y') "
                           "and verify is null", companyId)
    if len(artifacts) > 0: verfyinfo += "产品 "
    members = conn.query("select cmr.* from company_member_rel  cmr left join member m on cmr.memberId=m.id "
                         "where cmr.companyId=%s and m.verify is null and "
                         "(cmr.type = 0 or cmr.type = 5010 or cmr.type = 5020) and "
                         "(cmr.active is null or cmr.active='Y')", companyId)
    if len(members) > 0: verfyinfo += "团队 "
    comaliases = conn.query("select * from company_alias where companyId=%s and (active is null or active='Y')"
                            " and verify is null and type=12020", companyId)
    if len(comaliases) > 0: verfyinfo += "产品线短名 "
    corpaliaes = conn.query("select * from corporate_alias where (active is null or active='Y') "
                            "and verify is null  and corporateId=%s", corporateId)
    if len(corpaliaes) > 0: verfyinfo += "corporate公司名 "
    comrecs = conn.query("select * from company_recruitment_rel where companyId=%s and "
                         "(active is null or active='Y') and verify is null", companyId)
    if len(comrecs) > 0:  verfyinfo += "招聘 "

    conn.close()
    if len(verfyinfo) > 0:
        info = verfyinfo + "未verify"
    else:
        info = " "
    logger.info("company: %s->%s", companyId, info)
    return info


if __name__ == '__main__':
    logger.info("Begin...")
    num = 0
    conn = db.connect_torndb()
    icompanies = conn.query("select * from audit_investor_company where investorId=125")
    count_name = {}
    count_gongshang = {}
    # fullnames = {}
    for icompany in icompanies:
        if icompany["companyId"] is None: continue
        company = conn.get("select * from company where (active is null or active='Y') and id=%s",
                           icompany["companyId"])
        if company is None: continue
        # num += 1

        # fullName parts
        fullNames = []
        if company["fullName"] is not None and company["fullName"] != "": fullNames.append(company["fullName"])
        if company["corporateId"] is not None:
            corporate_aliases = conn.query("select * from corporate_alias where corporateId=%s and type=12010"
                                           " and (active is null or active='Y')", company["corporateId"])
            [fullNames.append(ca["name"]) for ca in corporate_aliases if ca["name"] is not None and
             ca["name"].strip() != "" and ca["name"] not in fullNames]

        count_gongshang[icompany["companyId"]] = fullNames
        logger.info("id: %s -> %s", icompany["companyId"], ":".join(fullNames))
        # count name part
        for fullName in fullNames:
            if count_name.has_key(fullName) is False:
                count_name[fullName] = [company["name"]]
            else:
                if company["name"] not in count_name[fullName]:
                    count_name[fullName].append(company["name"])

    for name in count_name:
        if len(count_name[name]) > 1:
            logger.info("name:%s -> %s", name, ":".join(count_name[name]))

    # fp = open("audit.txt", "w")
    line = "name###code###id###round###brief###xiniuInvestor###itjuziInvestor###kr36Investor###gongshangInvestor###fullNames###RepeatWith###verify\n"
    # fp.write(line)
    results = []
    for icompany in icompanies:
        if icompany["companyId"] is None: continue
        company = conn.get("select * from company where (active is null or active='Y') and id=%s",
                           icompany["companyId"])
        if company["locationId"] is not None:
            lc = conn.get("select * from location where locationId=%s", company["locationId"])
            if lc is not None:
                location = lc["locationName"]
        else:
            location = None

        company_tags = conn.query('''
        select t.name from company_tag_rel r 
        join tag t on t.id=r.tagId
        where (r.active is null or r.active='Y') and r.companyId=%s
        and (t.active is null or t.active='Y')
        and t.type in (11100,11012)
        ''',
                                  company["id"])


        if company is None: continue
        if icompany["name"] is None or icompany["name"] == "": continue
        fn = count_gongshang[icompany["companyId"]]

        roundDesc = " "
        if company["corporateId"] is None: continue

        corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
        if corporate is None: continue

        rounda = corporate["round"]
        roundDesc = rmap[int(rounda)] if (rounda is not None and rmap.has_key(int(rounda))) else " "

        vinfo = getinfo(company["id"], company["corporateId"])

        repeats = []
        for f in fn:
            if len(count_name[f]) > 1:
                for rn in count_name[f]:
                    if rn != company["name"] and rn not in repeats: repeats.append(rn)
        line = "%s###%s###%s###%s###%s###%s###%s###%s###%s###%s###%s###%s\n" % (icompany["name"], company["code"],
                                                                                company["id"], roundDesc,
                                                                                company["brief"] if (
                                                                                    company["brief"] is not None and
                                                                                    company[
                                                                                        "brief"].strip() != "") else " ",
                                                                                icompany["xiniuInvestor"],
                                                                                icompany["itjuziInvestor"],
                                                                                icompany["kr36Investor"],
                                                                                icompany["gongshangInvestor"],
                                                                                "++".join(fn) if len(fn) > 0 else " ",
                                                                                "++".join(repeats) if len(
                                                                                    repeats) > 0 else " ",
                                                                                vinfo

                                                                                )
        print 'status:',company['companyStatus'],company["code"]
        lineList = [icompany["name"], company["code"],
                    company["id"], roundDesc,
                    company["brief"] if (company["brief"] is not None and company["brief"].strip() != "") else " ",
                    icompany["xiniuInvestor"],
                    icompany["itjuziInvestor"],
                    icompany["kr36Investor"], icompany["gongshangInvestor"],
                    "++".join(fn) if len(fn) > 0 else " ",
                    "++".join(repeats) if len(repeats) > 0 else " ",
                    vinfo, company['establishDate'],
                    'http://www.xiniudata.com/file/%s/product.png' % company['logo'],
                    company['website'],
                    company['description'],
                    company['fullName'],
                    location,
                    companyStatusMap.get(company['companyStatus']),
                    ','.join([i['name'] for i in company_tags])

                    ]

        num += 1
        results.append(lineList)
        # fp.write(line)

    import pandas as pd

    df = pd.DataFrame(results, columns=['name', 'companyCode', 'id', 'round', 'brief', 'xiniuInvestor', 'itjuziInvestor',
                                        'kr36Investor',
                                        'gongshangInvestor', 'fullNames', 'RepeatWith', 'verify', 'establishDate',
                                        'logo', 'website',
                                        'description', 'fullName', 'locationName', 'companyStatus','tagVOs'])

    for c in df.columns:
        def illegal(row):
            import re
            content = row[c]
            if content is not None:
                ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
                # print 'content:',c,content
                try:
                    content = ILLEGAL_CHARACTERS_RE.sub(r'', content)
                except:
                    pass
            return content

        # print 'c:',c
        df[c] = df.apply(illegal, axis=1)

    df.to_excel('export.xlsx', index=0,
                columns=["companyCode", "name", "establishDate", "logo", "website", "description", "fullName", "round",
                         " locationName", "companyStatus", "tagVOs", "xiniuInvestor", "itjuziInvestor", "kr36Investor",
                         "gongshangInvestor", "brief", "fullNames", "RepeatWith", "verify"])

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
    #     line = "%s###%s###%s###%s###%s###%s###%s\n" % (name, "++".join(fullNames) if len(fullNames)>0 else " ",
    #                                                    "++".join(websites) if len(websites)>0 else " ",
    #                                                    round if round is not None else " ",
    #                                                    edate if edate is not None else " ",
    #                                                    location if location is not None else " ",
    #                                                    "++".join(fields) if len(fields)>0 else " ")
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
    # fp.close()
    # mongo.close()
    conn.close()
    logger.info("num: %s", num)
    logger.info("End.")
