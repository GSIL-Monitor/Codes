# -*- coding: utf-8 -*-
import os, sys
import datetime
import xlwt

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config, util, db


#logger
loghelper.init_logger("export_big_deal", stream=True)
logger = loghelper.get_logger("export_big_deal")

def getCurrencyName(currency):
    if currency == 3010:
        return u"USD"
    if currency == 3020:
        return u"RMB"
    if currency == 3030:
        return u"SGD"
    return ""

def getRoundName(round):
    if round==1010:
        return u"种子轮"
    if round==1011:
        return u"天使轮"
    if round==1020:
        return u"Pre-A"
    if round==1030:
        return u"A"
    if round==1031:
        return u"A+"
    if round==1039:
        return u"Pre-B"
    if round==1040:
        return u"B"
    if round==1041:
        return u"B+"
    if round==1050:
        return u"C"
    if round==1060:
        return u"D"
    if round==1070:
        return u"E"
    if round==1080:
        return u"F"
    if round==1090:
        return u"Late Stage"
    if round==1100:
        return u"Pre-IPO"
    if round==1105:
        return u"新三板"
    if round==1110:
        return u"IPO"
    if round==1120:
        return u"Acquired"
    if round==1130:
        return u"战略投资"
    return u""

if __name__ == "__main__":
    style_date = xlwt.easyxf(num_format_str='yyyy/MM/dd hh:mm:ss')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Deals')

    line = 0
    col = 0
    num = 0

    ws.write(line,col,""); col+=1
    ws.write(line,col,u"项目名称"); col+=1
    ws.write(line,col,u"url"); col+=1
    ws.write(line,col,u"融资日期"); col+=1
    ws.write(line,col,u"轮次"); col+=1
    ws.write(line,col,u"币种"); col+=1
    ws.write(line,col,u"金额"); col+=1
    ws.write(line,col,u"投资方"); col+=1


    conn =db.connect_torndb()
    cids = conn.query("select distinct companyId from funding "
                      "where fundingDate>='2011/1/1' and "
                      "((currency=3010 and investment>=50000000) or (currency=3020 and investment>=300000000))")
    for cid in cids:
        line += 1; num += 1; col=0

        company = conn.get("select * from company where id=%s", cid["companyId"])
        if company["active"] == 'N':
            continue
        logger.info(company["name"])
        ws.write(line,col,num); col+=1
        ws.write(line,col,company["name"]); col+=1
        ws.write(line,col,"http://www.xiniudata.com/#/company/%s/overview" % company["code"]); col+=1

        fundings = conn.query("select * from funding where (active is null or active='Y') "
                              "and companyId=%s order by fundingDate desc", cid["companyId"])
        for funding in fundings:
            ws.write(line,col,funding["fundingDate"], style_date); col+=1
            ws.write(line,col, getRoundName(funding["round"])); col+=1
            ws.write(line,col, getCurrencyName(funding["currency"])); col+=1
            ws.write(line,col, funding["investment"]); col+=1
            investors = []
            investor_rels = conn.query("select * from funding_investor_rel where fundingId=%s", funding["id"])
            for rel in investor_rels:
                investor = conn.get("select * from investor where id=%s", rel["investorId"])
                investors.append(investor["name"])
            ws.write(line,col, ",".join(investors)); col+=1

            col = 3; line += 1
    conn.close()

    wb.save("logs/big_deals.xls")