# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
from mako.template import Template
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config, db
import email_helper

#logger
loghelper.init_logger("user_industry_subscription", stream=True)
logger = loghelper.get_logger("user_industry_subscription")

conn = None
mongo = None

start = None
end = None

industries_data = {}

def process_user(user_id):
    user_industries_data = []
    message_count = 0
    user = conn.get("select * from user where id=%s", user_id)
    if user is None:
        return
    if user["active"] == 'D':
        return
    if user["email"] is None or user["email"].strip() == "":
        return
    if user["emailVerify"] != 'Y' and user["emailVerify"] != 'O':
        return
    logger.info("userId: %s, name: %s, phone: %s, email: %s", user["id"], user["username"], user["phone"], user["email"])

    ss = conn.query("select * from user_industry_subscription "
                    "where (active is null or active='Y') and "
                    "userId=%s "
                    "order by id desc",
                    user_id)
    for s in ss:
        industry_id = s["industryId"]
        industry = conn.get("select * from industry where id=%s", industry_id)
        if industry["active"] == 'N':
            continue
        data = industries_data[industry_id]
        message_count += data["message_count"]
        user_industries_data.append(data)
    # logger.info("message count: %s", message_count)
    # logger.info("data: %s", user_industries_data)

    str_start = start.strftime("%m月%d日%H:%M")
    str_end = end.strftime("%m月%d日%H:%M")
    data = {
        "start": str_start,
        "end": str_end,
        "user": user,
        "message_count": message_count,
        "user_industries_data": user_industries_data
    }
    t = Template(filename='template/user_industry_track.html', input_encoding='utf-8', output_encoding='utf-8',
                 encoding_errors='replace')
    content = t.render(data=data)
    logger.info(content.decode('UTF-8'))

    title = "行业追踪日报（%s ~ %s）" % (str_start, str_end)
    email_helper.send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", user["email"], title, content)


def process_users(test):
    logger.info("process_all start...")
    users = conn.query("select distinct userId as userId from user_industry_subscription "
                       "where (active is null or active='Y') "
                       "order by userId")
    for u in users:
        if test is True:
            if u["userId"] != 221:
                continue
        process_user(u["userId"])
    logger.info("process_all end...")


def process_industries():
    global industries_data
    industries = conn.query("select * from industry where (active is null or active!='N')")
    #industries = conn.query("select * from industry where id in (1,7)") # Test
    for industry in industries:
        industry_id = industry["id"]
        new_coming_companies = get_new_coming_companies(industry_id)
        companies_with_mesasge, message_count = get_companies_with_message(industry_id)
        industries_data[industry_id] = {
            "id": industry_id,
            "name": industry["name"],
            "code": industry["code"],
            "new_coming_companies": new_coming_companies,
            "companies_with_mesasge": companies_with_mesasge,
            "message_count": message_count
        }
    # logger.info(industries_data)


def get_new_coming_companies(industry_id):
    companies = []
    rels = conn.query("select * from industry_company where "
                     "(active is null or active='Y') and "
                     "industryId=%s and "
                     "publishTime>=%s and publishTime<%s",
                     industry_id, start, end)
    for rel in rels:
        company_id = rel["companyId"]
        company = conn.get("select * from company where id=%s", company_id)
        if company is None:
            continue
        if company["active"] is not None and company["active"] != 'Y':
            continue
        companies.append({
            "id": company["id"],
            "code": company["code"],
            "name": company["name"]
        })
    return companies


def get_companies_with_message(industry_id):
    companies = []
    message_count = 0
    rels = conn.query("select * from industry_company where "
                      "(active is null or active='Y') and "
                      "industryId=%s",
                      industry_id)
    for rel in rels:
        company_id = rel["companyId"]
        company = conn.get("select * from company where id=%s", company_id)
        if company is None:
            continue
        if company["active"] is not None and company["active"] != 'Y':
            continue
        messages = conn.query("select id,message,relateType,relateId,publishTime from company_message where "
                              "active='Y' and "
                              "companyId=%s and "
                              "publishTime>=%s and publishTime<%s "
                              "order by relateType desc, publishTime desc",
                              company_id, start, end
                              )
        if len(messages) == 0:
            continue
        message_count += len(messages)
        companies.append({
            "id": company_id,
            "code": company["code"],
            "name": company["name"],
            "messages": messages
        })

    return companies, message_count


def init():
    global start
    global end
    today = datetime.datetime.now()
    end = datetime.datetime(today.year, today.month, today.day, 19, 0, 0)
    start = end - datetime.timedelta(days=1)


def main(test=True):
    global conn
    global mongo
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()

    init()
    process_industries()
    process_users(test)

    mongo.close()
    conn.close()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main(test=False)
    else:
        if sys.argv[1] == "test":
            main(test=True)