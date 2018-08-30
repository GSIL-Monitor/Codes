# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

# logger
loghelper.init_logger("xtecher_company_repair", stream=True)
logger = loghelper.get_logger("xtecher_company_repair")


def run():
    conn = db.connect_torndb()
    sql = '''select name,fullname,sourceid,id  from source_company where source=13821
    '''
    results = conn.query(sql)  # TODO
    conn.close()

    for c in results:
        if c['fullname'] is not None and not name_helper.name_check(c['fullname'])[1] == True:
            logger.info('%s not company', c['fullname'])

            conn = db.connect_torndb()
            conn.update('''UPDATE source_company SET fullName=null where id = %s''', c['id'])
            conn.update(
                'UPDATE source_company_name SET type=12020 where sourcecompanyid = %s and type=12010 and name=%s',
                c['id'],c['fullname'])

            conn.close()


if __name__ == "__main__":
    run()
