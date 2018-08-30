# -*- coding: utf-8 -*-
import os, sys
import datetime
import gridfs
import xlrd
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config, util, db, download, contenttype

#logger
loghelper.init_logger("audi_import", stream=True)
logger = loghelper.get_logger("audi_import")

mongo = db.connect_mongo()
collection = mongo.demoday.contest_company
imgfs = gridfs.GridFS(mongo.gridfs)

download_crawler = download.DownloadCrawler(use_proxy=False)

def get_topic_id(topic):
    if topic == "人工智能的应用":
        return 13
    if topic == "数字化":
        return 11
    if topic == "车·生活":
        return 12
    return None

def get_date(str):
    d = datetime.datetime.strptime(str.strip(),'%Y/%m/%d %p %H:%M:%S')
    if str.find("PM") > 0:
        d += datetime.timedelta(hours=12)
    return d


def find_company(name):
    try:
        conn =db.connect_torndb()
        c = conn.get("select c.* from company_alias a join company c on a.companyId=c.id "
                    "where a.type=12010 and (a.active is null or a.active='Y') and (c.active is null or c.active='Y') "
                    "and a.name=%s limit 1",
                     name.strip())
        conn.close()
        if c:
            return c["id"]
    except:
        pass

    return None


def process(table):
    sort = 0
    conn =db.connect_torndb()
    item = conn.get("select max(sort) as sort from contest_company where contestId=%s", 10)
    if item:
        sort = item["sort"]
        if sort is None:
            sort = 0
    conn.close()

    nrows = table.nrows
    for i in range(3, nrows):
        row = table.row_values(i)
        sourceId = str(int(row[1]))
        logger.info("sourceId: %s", sourceId)
        conn =db.connect_torndb()
        item = conn.get("select * from contest_company where contestId=%s and sourceId=%s", 10, sourceId)
        conn.close

        if item:
            bp_url = row[14]
            conn =db.connect_torndb()
            conn.update("update contest_company_file set link=%s where contestCompanyId=%s", bp_url, item["id"])
            conn.close()
            continue

        createTime = xlrd.xldate.xldate_as_datetime(row[2],0)
        logger.info(createTime)

        topic = row[10]
        logger.info("topic: %s", topic)
        topic_id = get_topic_id(topic)
        if topic_id is None:
            continue

        name = row[12]
        logger.info("name: %s", name)

        brief = row[13]
        logger.info("brief: %s", brief)

        bp_url = row[14]
        logger.info("bp url: %s", bp_url)

        bp_filename = bp_url.split("/")[-1]
        logger.info("bp filename: %s", bp_filename)

        desc = row[16]
        logger.info("desc: %s", desc)

        username=row[17]
        logger.info("username: %s", username)

        company = row[18]
        logger.info("company: %s", company)

        company_id = find_company(company)

        phone = row[19]
        try:
            phone = str(int(phone))
        except:
            pass
        logger.info("phone: %s", phone)

        other_phone = row[20]
        try:
            other_phone = str(int(other_phone))
        except:
            pass
        logger.info("other phone: %s", other_phone)

        email = row[21]
        logger.info("email: %s", email)

        wechat = row[22]
        logger.info("wechat: %s", wechat)

        image_value = download_crawler.get(bp_url)
        if image_value is not None:
            content_type = contenttype.get_content_type(bp_filename)
            bp_id = imgfs.put(image_value, content_type=content_type, filename='%s' % bp_filename)
            logger.info("bp_id: %s", bp_id)
        sort += 1

        conn =db.connect_torndb()
        contest_company_id = conn.insert("insert contest_company(contestId,topicId,name,createTime,sourceId,sort,extra,companyId)"
                    "values(%s,%s,%s,%s,%s,%s,%s,%s)",
                    10,topic_id,name,createTime,sourceId,sort, None, company_id)
        conn.insert("insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)"
                    "values(11,%s,56000,now(),1)", contest_company_id)
        conn.insert("insert contest_company_file(contestCompanyId,name,link,file,createTime) values(%s,%s,%s,%s,%s)",
                    contest_company_id, bp_filename, bp_url, bp_id, createTime)
        conn.close

        data = {
            "contestId": 10,
            "contestCompanyId": contest_company_id,
            "extra": [
                {"name":"项目概念／愿景",
                 "value":brief,
                 "type":"text"
                },
                {"name":"项目介绍",
                 "value":desc,
                 "type":"text"
                },
                {"name":"姓名",
                 "value":username,
                 "type":"text"
                },
                {"name":"公司名",
                 "value":company,
                 "type":"text"
                },
                {"name":"联系电话",
                 "value":phone,
                 "type":"text"
                },
                {"name":"其他联系电话",
                 "value":other_phone,
                 "type":"text"
                },
                {"name":"电子邮箱地址",
                 "value":email,
                 "type":"text"
                },
                {"name":"微信号",
                 "value":wechat,
                 "type":"text"
                },
            ]
        }
        collection.insert(data)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        exit()
    filename = sys.argv[1]
    data = xlrd.open_workbook(filename)
    process(data.sheets()[0])