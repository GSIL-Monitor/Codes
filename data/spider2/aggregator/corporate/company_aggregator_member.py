# -*- coding: utf-8 -*-
import os, sys, re, json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_db_util
import helper, util

#logger
loghelper.init_logger("company_aggregator_member", stream=True)
logger = loghelper.get_logger("company_aggregator_member")

def check_postion(position, crels):
    for crel in crels:
        if crel["position"] is not None and re.search(position, crel["position"], re.I):
            return True
    return False

def aggregate_member(company_id, source_company_id, test=False):
    logger.info("aggregate_member")
    conn = db.connect_torndb()
    rels = conn.query("select * from source_company_member_rel where sourceCompanyId=%s", source_company_id)
    crels = conn.query("select * from company_member_rel where companyId=%s and (active is null or active='Y')", company_id)
    logger.info(json.dumps(crels, ensure_ascii=False, cls=util.CJsonEncoder))
    conn = db.connect_torndb()
    for rel in rels:
        source_member_id = rel["sourceMemberId"]
        source_member = conn.get("select * from source_member where id=%s", source_member_id)
        if source_member is None:
            continue

        #Check position if it is existed
        exist = False
        if rel["position"] is not None:
            for position in ["ceo", "cto", "coo"]:
                if re.search(position, rel["position"], re.I) and check_postion(position, crels):
                    exist = True
                    break
        if exist:
            continue
        # member_id = source_member["memberId"]
        # if member_id is None:
        #     member_id = aggregate_one_member(company_id, source_member)
        member_id = aggregate_one_member(company_id, source_member, test)
        logger.info("aggregate_member. member_id=%s source, %s", member_id, source_member["name"])
        aggregator_db_util.insert_company_member_rel(company_id,member_id,rel, test)


def aggregate_one_member(company_id, source_member, test):
    table_names = helper.get_table_names(test)
    # member_id = source_member["memberId"]
    # if member_id is not None:
    #     return member_id

    member_id = None
    conn = db.connect_torndb()

    #同公司同名识别为同一个人
    members = conn.query("select m.* from "
        + table_names["member"] + " m join " + table_names["company_member_rel"] + " r on m.id=r.memberId " +
        "where r.companyId=%s and (r.active is null or r.active='Y' or (r.active='N' and r.modifyUser != 139))", company_id)
    m = None

    for m in members:
        logger.info(json.dumps(m, ensure_ascii=False, cls=util.CJsonEncoder))
        if m["name"] == source_member["name"]:
            member_id = m["id"]
            break

    if member_id is None and not test:
        member_id = source_member["memberId"]

    if member_id is not None:
        #merge
        if m is not None and m["verify"] != 'Y':
            if not test:
                flag = replace(m, source_member)
                if flag:
                    aggregator_db_util.update_member(m)
    else:
        member_id = aggregator_db_util.insert_member(source_member, test)

    if not test:
        conn.update("update source_member set memberId=%s where id=%s", member_id, source_member["id"])

    conn.close()
    return member_id


def replace(member, source_member):
    names = ["name",
             "description",
             "education",
             "work",
             "photo",]
    flag = False
    for name in names:
        if (member[name] is None or member[name].strip() == "") and (source_member[name] is not None and source_member[name].strip() != ""):
            member[name] = source_member[name]
            flag = True
    return flag

def merge_company_member(company_id, name):
    ms = conn.query("select m.* from company_member_rel r join member m on r.memberId=m.id where r.companyId=%s and m.name=%s order by id", company_id, name)
    target = None
    for m in ms:
        if m["active"] != 'N':
            target = m
            logger.info("merge to: %s ", target["id"])
            break
    if target is None:
        return
    for m in ms:
        if m["id"] != target["id"] and m["active"] != 'N':
            merge_member(target,m)

def merge_member(target, m):
    columns = ["education",
               "workEmphasis",
               "work",
               "description",
               "photo",
               "email",
               "phone"
               ]
    conn = db.connect_torndb()
    for col in columns:
        if target[col] is None or target[col].strip() == "":
            if m[col] is not None and m[col].strip() != "":
                conn.update("update member set " + col + "=%s where id=%s",m[col].strip(),target["id"])

    cmrs = conn.query("select * from company_member_rel where (active is null or active='Y') and memberId=%s", m["id"])
    for r in cmrs:
        company_id = r["companyId"]
        r_target = conn.get("select * from company_member_rel where (active is null or active='Y') and companyId=%s and memberId=%s",company_id,target["id"])
        if r_target:
            conn.update("update company_member_rel set active='N' where id=%s", r["id"])
        else:
            conn.update("update company_member_rel set memberId=%s where id=%s", target["id"], r["id"])

    conn.update("update source_member set memberId=%s where memberId=%s", target["id"], m["id"])
    conn.update("update member set active='N' where id=%s", m["id"])
    conn.close()

if __name__ == "__main__":
    logger.info("Start...")
    conn = db.connect_torndb()
    cs = conn.query("select id, name, code from company where (active is null or active='Y')")
    for c in cs:
        ms = {}
        cmrs = conn.query("select * from company_member_rel where (active is null or active='Y') and companyId=%s", c["id"])
        for r in cmrs:
            m = conn.get("select * from member where id=%s", r["memberId"])
            if ms.has_key(m["name"]):
                ms[m["name"]] += 1
            else:
                ms[m["name"]] = 1
        for name in ms:
            if ms[name] > 1:
                logger.info("company code: %s, member name: %s", c["code"], name)
                merge_company_member(c["id"], name)
                #exit()