# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("gongshang_aggregator", stream=True)
logger = loghelper.get_logger("gongshang_aggregator")


if __name__ == '__main__':
    limit = 1000

    conn = db.connect_torndb()
    while True:
        ss = conn.query("select * from source_gongshang_base where gongshangBaseId is null order by id limit %s", limit)
        if len(ss) == 0:
            break

        for s in ss:
            logger.info("%s" % (s["name"]))

            b = conn.get("select * from gongshang_base where name=%s limit 1", s["name"])
            if b is not None:
                conn.update("update source_gongshang_base set gongshangBaseId=%s where id=%s", b["id"], s["id"])
                continue

            alias = conn.get("select * from company_alias where name=%s limit 1", s["name"])
            if alias is None:
                alias = conn.get("select * from company_alias where name=%s limit 1", s["name"].replace(u"（", "(").replace(u"）", ")"))

            if alias is None:
                logger.info("%s Not Found!!!" % s["name"])
                continue

            sql = "insert gongshang_base( \
                    companyAliasId, \
                    name,regCapital,industry,regInstitute,establishTime,base, \
                    regNumber,regStatus,fromTime,toTime,businessScope,regLocation, \
                    companyOrgType, legalPersonId, legalPersonName, \
                    createTime,active \
                    ) values( \
                    %s, \
                    %s, %s, %s, %s, %s, %s, \
                    %s, %s, %s, %s, %s, %s, \
                    %s, %s, %s, \
                    now(),'Y' \
                    )"

            gongshangBaseId = conn.insert(sql,
                            alias["id"],
                            s["name"], s.get("regCapital"),s.get("industry"),s.get("regInstitute"),s.get("establishTime"),s.get("base"),
                            s.get("regNumber"),s.get("regStatus"),s.get("fromTime"),s.get("toTime"),s.get("businessScope"),s.get("regLocation"),
                            s.get("companyOrgType"), s.get("legalPersonId"), s.get("legalPersonName")
                            )

            conn.update("update source_gongshang_base set gongshangBaseId=%s where id=%s", gongshangBaseId, s["id"])

            company_id = alias["companyId"]
            company1 = conn.get("select * from company where id=%s", company_id)
            if company1["establishDate"] is None:
                gongshang = conn.get("select g.* from gongshang_base g join company_alias a on g.companyAliasId=a.id \
                                     join company c on a.companyId=c.id where c.id=%s order by g.establishTime limit 1", company_id)
                if gongshang is not None:
                    conn.update("update company set establishDate=%s where id=%s", gongshang["establishTime"], company_id)

        if len(ss) < limit:
            break

        conn.close()