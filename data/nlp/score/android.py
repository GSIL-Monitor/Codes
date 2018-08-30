# -*- encoding=utf-8 -*-
__author__ = "kailu"

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon


def recent_android_increase_rapidly_all():
    db = dbcon.connect_torndb()

    query_string = ("create temporary table if not exists temp1 "
                    "(select artifactid, growth from source_summary_android "
                    "where modifytime > date_add(now(), interval -7 day) "
                    "and download > 1000 and growth > 10);")
    db.execute(query_string)
    query_string = ("select * from( "
                    "select c.id cid, a.id aid "
                    "from company c, artifact a, temp1 t1 "
                    "where c.id = a.companyid "
                    "and (c.active is null or c.active = 'Y') "
                    "and (a.active is null or a.active = 'Y') "
                    "and a.id = t1.artifactid "
                    "order by t1.growth desc)t "
                    "group by cid;")
    query_result = db.query(query_string)
    return [(int(row.cid), int(row.aid), 10.0001) for row in query_result]

    db.close()


if __name__ == '__main__':
    pass
