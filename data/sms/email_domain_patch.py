# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("email_domain_patch", stream=True)
logger = loghelper.get_logger("email_domain_patch")

if __name__ == "__main__":
    conn = db.connect_torndb()
    orgs = conn.query("select * from organization where type=17020 order by id")
    for org in orgs:
        #logger.info("org name: %s", org["name"])
        users = conn.query("select * from user u join user_organization_rel r on u.id=r.userId "
                           "where r.organizationId=%s and (u.active is null or u.active !='D')",
                           org["id"])
        emails = {}
        for user in users:
            email = user["email"]
            domain = email.split("@")[1].lower()
            if domain == "163.com" or \
                domain == "qq.com" or \
                domain == "139.com" or \
                domain == "126.com" or \
                domain == "gmail.com" or \
                domain == "hotmail.com" or \
                domain == "me.com":
                continue
            if emails.has_key(domain):
                emails[domain] += 1
            else:
                emails[domain] = 1
        for domain in emails.keys():
            #logger.info("%s : %s", domain, emails[domain])
            print "update organization set emailDomain='%s' where id=%s; #%s, %s" % (domain, org["id"], org["name"], emails[domain])

        print ""
    conn.close()