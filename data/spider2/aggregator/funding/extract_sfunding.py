# -*- coding: utf-8 -*-

import os, sys,datetime,json
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper,util
import db
import name_helper

#logger
loghelper.init_logger("extract_funding", stream=True)
logger = loghelper.get_logger("extract_funding")

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



def extract_sf(date):
    rd = []
    conn = db.connect_torndb()
    # sourceCompanyIds = []
    # rd["IT桔子"] = []
    # rd["36氪"] = []
    source_fundings = conn.query("select * from source_funding where "
                              "fundingDate>=%s and fundingDate<%s", date, date+datetime.timedelta(days=1))
    for source_funding in source_fundings:
        # if source_funding["sourceCompanyId"] not in sourceCompanyIds:
        #     sourceCompanyIds.append(source_funding["sourceCompanyId"])

    # for sourceCompanyId in sourceCompanyIds:
        rds = {}
        sourceCompanyId = source_funding["sourceCompanyId"]
        source_company = conn.get("select * from source_company where id=%s and (active is null or active='Y')",
                                  sourceCompanyId)
        if source_company is None: continue
        if source_company["source"] not in [13022, 13030]: continue


        investors = [ii["name"] for ii in conn.query("select i.name from source_funding_investor_rel fir join "
                                                     "source_investor i "
                                                     "on fir.sourceInvestorId=i.id where fir.sourceFundingId=%s", source_funding["id"])]
        amount = get_amount(source_funding["investment"], source_funding["precise"])
        fi = {
            "date": str(source_funding["fundingDate"].date()) if source_funding["fundingDate"] is not None else "",
            "round": rmap[int(source_funding["round"])] if (source_funding["round"] is not None and
                                                     rmap.has_key(int(source_funding["round"]))) else "",
            "amount": amount,
            "currency": currentmap[int(source_funding["currency"])] if (source_funding["currency"] is not None and
                                                                 currentmap.has_key(int(source_funding["currency"]))) else "",
            "investor": ",".join(investors)

        }
        rds.update(fi)
        if source_company["companyId"] is None:
            rds["name"] = source_company["name"]
            rds["code"] = "None"

        else:
            company = conn.get("select * from company where id=%s",source_company["companyId"])
            rds["name"] = company["name"]
            rds["code"] = company["code"]
        if source_company["source"] == 13022:
            # rd["36氪"].append(rds)
            rds["source"] = "36氪"
        else:
            # rd["IT桔子"].append(rds)
            rds["source"] = "IT桔子"
        rd.append(rds)


    conn.close()
    return rd


if __name__ == '__main__':
    logger.info("Begin...")
    t1 = datetime.datetime.strptime("2017-10-11", "%Y-%m-%d").date()
    result = extract_sf(t1)
    logger.info("%s", len(result))
    logger.info(json.dumps({"a":result}, ensure_ascii=False, cls=util.CJsonEncoder))
    logger.info("End.")