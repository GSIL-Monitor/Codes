# -*- coding: utf-8 -*-
import os, sys
import time
from datetime import datetime
from datetime import timedelta
from mako.template import Template

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, email_helper

#logger
loghelper.init_logger("check_company_status", stream=True)
logger = loghelper.get_logger("check_company_status")

emails = [
        "wuwenxian@xiniudata.com",
        "arthur@xiniudata.com",
        "zhangli@xiniudata.com",
    ]

def process():
    items = []
    conn = db.connect_torndb()
    cs = conn.query("select id, corporateId, code, name, createTime, modifyTime from company "
                    "where companyStatus=2015 and (active='Y' or active is null)")
    for c in cs:
        fa = conn.get("select * from company_fa f join dictionary d on f.source=d.value "
                     "where d.subTypeValue=1301 and (active is null or active='Y') and "
                     "companyId=%s order by publishDate desc limit 1", c["id"])
        if fa is not None:
            continue

        funding = conn.get("select * from funding where (active is null or active='Y') and "
                           "corporateId=%s order by fundingDate desc limit 1", c["corporateId"])
        if funding is None:
            continue

        status_time = c["modifyTime"]
        if status_time is None:
            status_time = c["createTime"]
        if status_time is None:
            continue

        if status_time > funding["fundingDate"] + timedelta(days=7):
            continue

        # logger.info("companyId: %s, code: %s, name: %s, may finish raising money", c["id"], c["code"], c["name"])
        items.append((c["id"], c["code"], c["name"]))
    conn.close()

    # send email
    t = Template(filename='template/check_company_status.html', input_encoding='utf-8',
                 output_encoding='utf-8', encoding_errors='replace')
    content = t.render(data={"items":items})
    # logger.info(content)
    d = datetime.now()
    for email in emails:
        email_helper.send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", email,
                  "疑似融资结束的公司清单-%s/%s/%s" % (d.year, d.month, d.day), content)



if __name__ == "__main__":
    logger.info("Start...")
    process()
    logger.info("End.")