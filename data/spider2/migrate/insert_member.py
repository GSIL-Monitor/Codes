# -*- coding: utf-8 -*-
import os, sys, datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db


def get_company(code):
    conn = db.connect_torndb()
    company = conn.get("select * from company where code=%s", code)
    conn.close()
    if company:
        return company["id"]
    else:
        print "%s not found!" % code
    return None

def get_type(position):
    if position.find("创始")>=0:
        return 5010
    if position.lower().find("ceo")>=0:
        return 5020
    if position.lower().find("coo")>=0:
        return 5020
    if position.lower().find("cto")>=0:
        return 5020
    if position.lower().find("cfo")>=0:
        return 5020

    return 5030

def insert_member(code, name, position, work):
    company_id = get_company(code)
    if company_id is None:
        return

    conn = db.connect_torndb()
    member_id = None
    rels = conn.query("select * from company_member_rel where companyId=%s and "
                      "(active is null or active='Y')", company_id)
    for rel in rels:
        member = conn.get("select * from member where id=%s", rel["memberId"])
        if name == member["name"]:
            member_id = member["id"]
            break

    if member_id:
        # update
        conn.update("update member set work=%s "
                    "where id=%s",
                    work, member_id)
    else:
        # new
        member_id = conn.insert("insert member(name,work,active,createTime) values(%s,%s,'Y',now())",
                    name, work)
        conn.insert("insert company_member_rel(companyId,memberId,position,type,active,createTime) "
                    "values(%s,%s,%s,%s,'Y',now())",
                    company_id, member_id,position, get_type(position))
    conn.close()
    print "Ok."

def usage():
    print "python insert_member.py code name position desc"


if __name__ == "__main__":
    if len(sys.argv) != 5:
        usage()
        exit()
    ts = sys.argv
    insert_member(ts[1],ts[2],ts[3],ts[4])