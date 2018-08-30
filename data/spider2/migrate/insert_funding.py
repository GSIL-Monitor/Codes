# -*- coding: utf-8 -*-
import os, sys, datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db

def getFundingRound(roundStr):
    fundingRound = None
    if roundStr.startswith("种子"):
        fundingRound = 1010
    elif roundStr.startswith("天使"):
        fundingRound = 1011
    elif roundStr.startswith("Pre-A"):
        fundingRound = 1020
    elif roundStr.startswith("A+"):
        fundingRound = 1031
    elif roundStr.startswith("A"):
        fundingRound = 1030
    elif roundStr.startswith("Pre-B"):
        fundingRound = 1039
    elif roundStr.startswith("B+"):
        fundingRound = 1041
    elif roundStr.startswith("B"):
        fundingRound = 1040
    elif roundStr.startswith("C+"):
        fundingRound = 1051
    elif roundStr.startswith("C"):
        fundingRound = 1050
    elif roundStr.startswith("D"):
        fundingRound = 1060
    elif roundStr.startswith("E"):
        fundingRound = 1070
    elif roundStr.startswith("F"):
        fundingRound = 1100
    elif roundStr.startswith("新三板"):
        fundingRound = 1105
    elif roundStr.startswith("IPO") or roundStr.startswith("已上市"):
        fundingRound = 1110
    elif roundStr.startswith("已被收购") or roundStr.startswith("并购"):
        fundingRound = 1120
    elif roundStr.startswith("战略投资"):
        fundingRound = 1130
    if fundingRound is None:
        print "%s not recognized" % roundStr
    return fundingRound


def get_currency(str):
    if str.startswith("人民币"):
        return 3020
    if str.lower().startswith("rmb"):
        return 3020
    if str.startswith("美元"):
        return 3010
    if str.lower().startswith("usd"):
        return 3010
    print "%s not recognized" % str
    return None


def get_company(code):
    conn = db.connect_torndb()
    company = conn.get("select * from company where code=%s", code)
    conn.close()
    if company:
        return company["id"]
    else:
        print "%s not found!" % code
    return None

def get_investor(name):
    investor_id = None
    conn = db.connect_torndb()
    investor = conn.get("select * from investor where name=%s", name)
    if investor is None:
        print "%s not found!" % name
        investors = conn.query("select * from investor where name like %s", "%" + name + "%")
        i = 1
        for investor in investors:
            print "%s: %s" % (i, investor["name"])
            i += 1
    else:
        investor_id = investor["id"]
    conn.close()

    return investor_id

def insert_funding(code, date_str, round_str, investment, precise, currency_str, investor_names):
    company_id = get_company(code)
    if company_id is None:
        return
    round = getFundingRound(round_str)
    if round is None:
        return
    currency = get_currency(currency_str)
    if currency is None:
        return
    investorIds = []
    for name in investor_names:
        if name == '未知':
            continue
        investor_id = get_investor(name)
        if investor_id is None:
            return
        investorIds.append(investor_id)

    try:
        fundingDate = datetime.datetime.strptime(date_str,'%Y/%m/%d')
    except:
        print "%s not recognized. Format:2016/01/02" % date_str
        return

    conn = db.connect_torndb()
    funding = conn.get("select * from funding where (active is null or active='Y') and "
                       "companyId=%s and round=%s",
                       company_id, round)
    if funding:
        # update
        funding_id = funding["id"]
        conn.update("update funding set investment=%s,currency=%s,precise=%s,fundingDate=%s "
                    "where id=%s",
                    investment, currency, precise, fundingDate, funding_id)
        conn.execute("delete from funding_investor_rel where fundingId=%s", funding_id)
    else:
        # new
        funding_id = conn.insert("insert funding(companyId,investment, round, currency, precise, fundingDate,"
                                 "fundingType,active,createTime) values(%s,%s,%s,%s,%s,%s,8030,'Y',now())",
                                 company_id, investment, round, currency,precise,fundingDate)
    for investor_id in investorIds:
        conn.insert("insert funding_investor_rel(fundingId,investorId,"
                    "active,createtime) values(%s,%s,'Y',now())",
                    funding_id, investor_id)

    funding = conn.get("select * from funding where companyId=%s order by round desc, fundingDate desc limit 1",
                           company_id)
    if funding is not None:
        conn.update("update company set round=%s, roundDesc=%s where id=%s",
                    funding["round"],funding["roundDesc"],company_id)

    conn.close()
    print "Ok."

def usage():
    print "python insert_funding.py code datestr roundstr investment precise currency investor1,investor2"

if __name__ == "__main__":
    if len(sys.argv) != 8:
        usage()
        exit()
    ts = sys.argv
    investor_names = ts[7].split(",")
    insert_funding(ts[1],ts[2],ts[3],ts[4],ts[5],ts[6], investor_names)