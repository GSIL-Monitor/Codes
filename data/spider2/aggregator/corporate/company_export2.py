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
import db,util


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


ivids = [108,114,122,125,149,387,493,2037,3348,4546]
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


    fp = open("company.txt", "w")

    conn = db.connect_torndb()

    companyIds =[]
    for ivid in ivids:
        investor = conn.get("select * from investor where id=%s",ivid)
        funding_investor_rels = conn.query(
            "select distinct fundingId from funding_investor_rel where investorId=%s and (active is null or active='Y')",
            ivid)
        # companyIds = []
        for fir in funding_investor_rels:
            # funding = conn.get("select * from funding where id=%s and (active is null or active='Y')"
            #                    " and fundingDate >='2017-01-01'", fir["fundingId"])
            funding = conn.get("select * from funding where id=%s and (active is null or active='Y')"
                               , fir["fundingId"])
            # if fir["fundingId"] != 109428: continue
            # funding = conn.get("select * from funding where id=%s and (active is null or active='Y')", fir["fundingId"])
            if funding is not None and funding["corporateId"] is not None:
                # logger.info(funding)
                cs = conn.query("select id from company where corporateId=%s and (active is null or active='Y')",
                                funding["corporateId"])
                for c in cs:
                    # logger.info(c)
                    if c["id"] not in companyIds:
                        companyIds.append(c["id"])
        logger.info(companyIds)
        logger.info("found %s companies", len(companyIds))


    for companyId in companyIds:
        company = conn.get("select * from company where id=%s and (active is null or active='Y')", companyId)
        name = company["name"]
        fullNames = []
        corporate_aliases = conn.query("select * from corporate_alias where corporateId=%s and type=12010"
                                           " and (active is null or active='Y')", company["corporateId"])
        [fullNames.append(ca["name"]) for ca in corporate_aliases if ca["name"] is not None and
              ca["name"].strip() != "" and ca["name"] not in fullNames]

        fundings = conn.query("select * from funding where corporateId=%s and (active='Y' or active is null)",
                              company["corporateId"])
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
                "amount": amount,
                "currency": currentmap[int(funding["currency"])] if (funding["currency"] is not None and
                                                                     currentmap.has_key(int(funding["currency"]))) else "",
                "investors": ",".join(investors)

            }
            bfi.append(fi)

        item = {
                "name": name,
                "fullNames": fullNames,
                "finance_info": bfi,
        }
        line = json.dumps(item)
        logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(line)
        fp.write(line)
        fp.write("\n")
        num += 1

    conn.close()
    fp.close()
    logger.info("num: %s", num)
    logger.info("End.")