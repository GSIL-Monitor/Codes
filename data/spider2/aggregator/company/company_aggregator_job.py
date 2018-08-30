# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_db_util

#logger
loghelper.init_logger("company_aggregator_job", stream=True)
logger = loghelper.get_logger("company_aggregator_job")

def aggregate_job(company_id, source_company_id):
    conn = db.connect_torndb()
    jobs = conn.query('select * from source_job where sourceCompanyId = %s', source_company_id)
    for job in jobs:
        sql = 'select * from job where companyId=%s and position=%s and salary=%s and educationType=%s and workYearType=%s and locationId=%s and offline=%s limit 1'
        result = conn.get(sql, company_id, job['position'], job['salary'], job['educationType'], job['workYearType'], job['locationId'], 'N')
        if result is None:
            job_id = aggregator_db_util.insert_job(company_id, job)
        else:
            job_id = result['id']
            sql = 'update job set updateDate = %s, modifyTime=now() where id =%s'
            conn.update(sql, result['updateDate'], job_id)
    conn.close()



