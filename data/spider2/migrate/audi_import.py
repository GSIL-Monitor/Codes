# -*- coding: utf-8 -*-
import os, sys
import xlrd
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config, util, db

#logger
loghelper.init_logger("audi_import", stream=True)
logger = loghelper.get_logger("audi_import")

mongo = db.connect_mongo()
collection = mongo.demoday.contest_company

def process(topic, table):
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
        sourceId = row[1]
        conn =db.connect_torndb()
        item = conn.get("select * from contest_company where contestId=%s and sourceId=%s", 10, sourceId)
        conn.close

        if item:
            continue

        name = row[3]
        logger.info(name)

        proposal_status = row[4]
        proposal_highlight_en = row[6]
        proposal_highlight_cn = row[7]
        participant = row[8]
        gender = row[9]
        city = row[10]
        try:
            contact = str(int(row[11]))
        except:
            contact = row[11]

        sort += 1

        extra = {
            "data": [
                {"name":"Proposal status",
                 "value":proposal_status,
                 "type":"text"
                },
                {"name":"Proposal highlight (en)",
                 "value":proposal_highlight_en,
                 "type":"text"
                },
                {"name":"Proposal highlight (cn)",
                 "value":proposal_highlight_cn,
                 "type":"text"
                },
                {"name":"Participant",
                 "value":participant,
                 "type":"text"
                },
                {"name":"Gender",
                 "value":gender,
                 "type":"text"
                },
                {"name":"City",
                 "value":city,
                 "type":"text"
                },
                {"name":"Contact",
                 "value":contact,
                 "type":"text"
                },
            ]
        }

        extra_str = json.dumps(extra).replace("\\","\\\\").replace('\\\u','\u')
        print extra_str

        conn =db.connect_torndb()
        contest_company_id = conn.insert("insert contest_company(contestId,topicId,name,createTime,createUser,sourceId,sort,extra)"
                    "values(%s,%s,%s,now(),1,%s,%s,%s)",
                    10,topic,name,sourceId,sort,extra_str)
        conn.insert("insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)"
                    "values(11,%s,56000,now(),1)", contest_company_id)
        conn.close



        data = {
            "contestId": 10,
            "contestCompanyId": contest_company_id,
            "extra": [
                {"name":"Proposal status",
                 "value":proposal_status,
                 "type":"text"
                },
                {"name":"Proposal highlight (en)",
                 "value":proposal_highlight_en,
                 "type":"text"
                },
                {"name":"Proposal highlight (cn)",
                 "value":proposal_highlight_cn,
                 "type":"text"
                },
                {"name":"Participant",
                 "value":participant,
                 "type":"text"
                },
                {"name":"Gender",
                 "value":gender,
                 "type":"text"
                },
                {"name":"City",
                 "value":city,
                 "type":"text"
                },
                {"name":"Contact",
                 "value":contact,
                 "type":"text"
                },
            ]
        }
        collection.insert(data)

if __name__ == "__main__":
    #data = xlrd.open_workbook('audi_sample.xls')
    #process(11,data.sheets()[1])
    #process(12,data.sheets()[2])
    #process(13,data.sheets()[3])
    pass