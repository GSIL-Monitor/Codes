# -*- coding: utf-8 -*-
import os, sys
import datetime
import time
from mako.template import Template

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, email_helper, funding_helper

#logger
loghelper.init_logger("openapi_funding_check", stream=True)
logger = loghelper.get_logger("openapi_funding_check")

emails = [
        "wuwenxian@xiniudata.com",
        "arthur@xiniudata.com",
        "zhangli@xiniudata.com"
    ]


def main():
    today = datetime.datetime.now()
    today = datetime.datetime(year=today.year, month=today.month, day=today.day) - datetime.timedelta(hours=8)
    yesterday = today - datetime.timedelta(days=1)
    logger.info("today: %s, yesterday: %s", today, yesterday)

    mongo = db.connect_mongo()
    items = list(mongo.company.funding.find(
        {
            "companyFullyVerify":"N",
            "fundingCreateTime": {"$gte": yesterday, "$lt": today}
        }
    ))

    all_items = list(mongo.company.funding.find(
        {
            "fundingCreateTime": {"$gte": yesterday, "$lt": today}
        }
    ))
    mongo.close()
    # logger.info(items)

    companies = []
    all_companies = []
    conn = db.connect_torndb()
    for item in items:
        company = get_detail(conn, item)
        companies.append(company)
    for item in all_items:
        company = get_detail(conn, item)
        all_companies.append(company)
    conn.close()

    companies.sort(key=lambda k:(k.get('fundingCreator', '')))
    all_companies.sort(key=lambda k: (k.get('fundingCreator', '')))

    # send email
    t = Template(filename='template/not_fully_verified_company.html', input_encoding='utf-8',
                 output_encoding='utf-8', encoding_errors='replace')
    content = t.render(data={"items": companies, "allItems": all_companies})
    logger.info(content)
    d = datetime.datetime.now()
    for email in emails:
        email_helper.send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", email,
                               "有融资但内容未完全确认的公司清单-%s/%s/%s" % (d.year, d.month, d.day), content)


def get_detail(conn, item):
    funding_id = item["fundingId"]
    funding = conn.get("select * from funding where id=%s", funding_id)
    company = conn.get("select * from company where id=%s", item["companyId"])
    company["round"] = funding_helper.get_round_desc(funding["round"])
    company["fundingCreator"] = ""
    if funding["createUser"] is not None:
        user = conn.get("select * from user where id=%s", funding["createUser"])
        if user is not None:
            company["fundingCreator"] = user["username"]
    elif funding["modifyUser"] is not None:
        user = conn.get("select * from user where id=%s", funding["modifyUser"])
        if user is not None:
            company["fundingCreator"] = user["username"]
    return company


if __name__ == '__main__':
    main()
