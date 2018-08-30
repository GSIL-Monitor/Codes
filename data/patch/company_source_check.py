# -*- coding: utf-8 -*-
import os, sys
import time
import xlwt

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("company_source_check", stream=True)
logger = loghelper.get_logger("company_source_check")

codes = [
'lingfenzhiyi',
'boshi360',
'heyiwangluo',
'herongwang',
'midunwangluo',
'miyoukeji',
'juyekeji',
'youliao',
'tianyu1206',
'tingyouAPP',
'suninglvxing87',
'hangzhoukaisandianshang40',
'naomiwang',
'yunzhikeji13',
'pqPetkitchzhsh',
'shixiongbangbangmang',
'qitianledikeji',
'guangzhoujixunke',
'fanshaowangluo',
'haxiuhuabao',
'turuixinx',
'hailidianshang',
'bjzhshflFlyfish',
'biliankeji',
'shizuokeji',
'dangmalawangluo',
'kuaizuwangluo',
'shishangmao',
'ipiaolmpl',
'shanghaitupaiwangluo',
'tuitu84',
'mkkjqmsh',
'DDhua',
'shanhaileyou80',
'jingshikeji',
'yunwakeji',
'jiankangbaobeiwang',
'yishengkang',
'jinwankansha46',
'daxiangce',
'shoudaoxinxikeji',
'boliboshi',
'gongshang',
'genshuiyou',
'kutingshuokejibeifen',
'youzhukeji',
'chishengkeji',
'bangfenxi',
'meijiale',
'moxun',
'chongqinghongnuokeji',
'xiaoku1229',
'weijiashipin',
'buyilehukeji',
'gaoshouzaixian',
'xiaolingmao',
'dilijiajubao',
'guangzhouyeyouxinxi',
'taoqipei5',
]


def process():
    wb = xlwt.Workbook()
    ws = wb.add_sheet('company')
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    line = 0
    for code in codes:
        col = 0
        company = conn.get("select * from company where code=%s", code)
        if company is None:
            continue
        logger.info("%s, %s, %s", company["name"], company["fullName"], company["website"])
        ws.write(line, col, company["name"])
        col += 1
        ws.write(line, col, company["fullName"])
        col += 1
        ws.write(line, col, company["website"])
        col += 1
        aliass = conn.query("select * from company_alias "
                            "where companyId=%s and type=12010 and (active is null or active='Y')",
                            company["id"])
        str = ""
        for alias in aliass:
            logger.info("%s", alias["name"])
            str += alias["name"] + "\n"
        ws.write(line, col, str)
        col += 1

        domains = conn.query("select distinct domain as domain from artifact where"
                             "(active is null or active='Y') and "
                             "type=4010 and companyId=%s",
                             company["id"])
        str = ""
        for domain in domains:
            beians = mongo.info.beian.find({"domain" : domain["domain"]})
            for beian in beians:
                logger.info("%s, %s, %s", beian["beianhao"],beian["domain"],beian["organizer"])
                str += beian["beianhao"] + ", " + beian["domain"] + ", " + beian["organizer"] + "\n"
        ws.write(line, col, str)
        col += 1
        source_companies = conn.query("select * from source_company where companyId=%s and (active is null or active='Y')",
                                      company["id"])
        str = ""
        for source_company in source_companies:
            logger.info("%s, %s, %s, %s", source_company["source"], source_company["sourceId"], source_company["name"], source_company["fullName"])
            str += "%s, %s, %s, %s\n" % (source_company["source"], source_company["sourceId"], source_company["name"], source_company["fullName"])
            source_artifacts = conn.query("select * from source_artifact where "
                                          "sourceCompanyId=%s and (active is null or active='Y') and type=4010",
                                          source_company["id"])
            for source_artifact in source_artifacts:
                logger.info("%s, %s, %s", source_artifact["extended"], source_artifact["link"], source_artifact["domain"])
                str += "*** %s, %s, %s\n" % (source_artifact["extended"], source_artifact["link"], source_artifact["domain"])
        ws.write(line, col, str)
        col += 1

        logger.info("")
        line += 1
    mongo.close()
    conn.close()
    wb.save("logs/company.xls")

if __name__ == "__main__":
    process()