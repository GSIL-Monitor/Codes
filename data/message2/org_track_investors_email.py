# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import traceback
from mako.template import Template
from bson.objectid import ObjectId
import json

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, email_helper, funding_helper

#logger
loghelper.init_logger("org_track_investors_email", stream=True)
logger = loghelper.get_logger("org_track_investors_email")

def process(test=True):
    conn = db.connect_torndb()
    orgs = conn.query("select distinct organizationId from org_function_switch where "
                      "active='Y' and functionState='Y' and functionValue=68023")
    conn.close()
    for org in orgs:
        org_id = org["organizationId"]
        logger.info("orgId: %s", org_id)
        process_one(org_id, test=test)


def process_one(org_id, thedate=None, test=True):
    if thedate is None:
        today = datetime.datetime.now()
    else:
        today = thedate
    yesterday = today + datetime.timedelta(days=-1)
    start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 19, 0, 0)
    end_time = datetime.datetime(today.year, today.month, today.day, 19, 0, 0)

    conn = db.connect_torndb()
    org = conn.get("select * from organization where id=%s", org_id)
    investors = conn.query("select distinct i.id, i.name, i.online, i.code "
                          "from investor_message m join investor i on i.id=m.investorId "
                          "join org_track_investor oti on oti.investorId=i.id "
                          "where oti.orgId=%s and oti.active='Y' and "
                          "m.active='Y' and "
                           "m.relateType in (70) and "
                           "m.publishTime>=%s and m.publishTime<%s "
                           "order by i.id desc",
                            org_id, start_time, end_time
                          )
    cnt = 0
    for investor in investors:
        logger.info("%s", investor["name"])
        messages = conn.query("select m.investorId, i.name, m.message, m.relateType, m.relateId, m.trackDimension "
                          "from investor_message m join investor i on i.id=m.investorId "
                          "where i.id=%s and "
                          "m.active='Y' and "
                          "m.relateType in (70) and "
                          "m.publishTime>=%s and m.publishTime<%s "
                           "order by relateType desc, publishTime desc",
                            investor["id"], start_time, end_time
                          )
        patch_messages(messages)
        investor["messages"] = messages
        cnt += len(messages)

    data = {
        "org": org,
        "investors": investors,
        "startTime": start_time.strftime("%m月%d日%H:%M"),
        "endTime": end_time.strftime("%m月%d日%H:%M"),
        "cnt": cnt
    }
    # print(data)

    filename = "track_investor.html"
    t = Template(filename='template/%s' % filename, input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
    content = t.render(data=data)
    print(content.decode('UTF-8'))

    title = "投资机构追踪日报（%s ~ %s）" % (data["startTime"], data["endTime"])
    users = conn.query("select * from org_track_user "
                       "where active='Y' and orgId=%s",
                       org_id)
    for user in users:
        if user["email"] is None or user["email"].strip() == "":
            continue
        if test is True:
            if user["email"] not in ["arthur@xiniudata.com"]:
                continue
        logger.info("%s", user["email"])
        email_helper.send_mail("烯牛数据","烯牛数据", "noreply@xiniudata.com", user["email"], title, content)
        pass

    conn.close()


def patch_messages(messages):
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    for message in messages:
        if message["relateType"] == 70:
            # news
            message["newsId"] = None
            if message["relateId"] is not None and message["relateId"].strip() != "":
                try:
                    funding_id = int(message["relateId"].strip())
                    funding = conn.get("select * from funding where id=%s", funding_id)
                    if funding is not None and funding["newsId"] is not None and funding["newsId"].strip() != "":
                        news_id = funding["newsId"].strip()
                        news = mongo.article.news.find_one({"_id": ObjectId(news_id)})
                        if news is not None:
                            message["newsId"] = news_id
                            message["newsTitle"] = news["title"]
                except:
                    pass

            # company, investors, round, investment
            try:
                funding_id = int(message["relateId"].strip())
                funding = conn.get("select * from funding where id=%s", funding_id)
                if funding is not None:
                    company_id = funding["companyId"]
                    company = conn.get("select * from company where id=%s", company_id)
                    message["companyName"] = company["name"]
                    message["brief"] = company["brief"]
                    message["companyCode"] = company["code"]
                    message["round"] = funding_helper.get_round_desc(funding["round"])
                    message["investment"] = funding_helper.gen_investment_desc(funding["investment"], funding["precise"], funding["preciseDesc"], funding["currency"])
                    message["investors"] = funding_helper.gen_investors(funding["investorsRaw"], funding["investors"])
                    message["source"] = funding["source"]
            except:
                pass
    mongo.close()
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        process(test=False)
    else:
        if sys.argv[1] == "test":
            process(test=True)
        else:
            test = False
            org_id = int(sys.argv[1])
            str_thedate = sys.argv[2]
            _test = sys.argv[3]
            if _test == "test":
                test = True
            thedate = datetime.datetime.strptime(str_thedate, '%Y-%m-%d')
            process_one(org_id, thedate, test=test)