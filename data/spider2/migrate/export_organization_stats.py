# -*- coding: utf-8 -*-
import os, sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper
import db
import xlwt

#logger
loghelper.init_logger("export_organization_stats", stream=True)
logger = loghelper.get_logger("export_organization_stats")


def t_org_title(t):
    titles = [
        u'机构ID',
        u'机构名称',
        u'机构状态',
        u'机构创建时间',
        u'开始试用时间',
        u'试用结束时间',
        u'总人数',
        u'登陆过人数',
        u'使用过机构版人数',
        u'总人数',
        u'登陆过人数',
    ]

    for index, title in enumerate(titles):
        t.write(0,index,title)


def t_user_title(t):
    titles = [
        u'机构ID',
        u'机构名',
        u'用户名',
        u'机构版',
        u'认证',
        u'身份',
        u'职位',
        u'角色',
        u'账号状态',
        u'注册时间',
        u'最新登陆时间',
        u'开始试用机构版时间',
        u'试用结束时间',
        u'邮箱',
        u'邮箱验证',
        u'手机',
        u'手机验证',
    ]

    for index, title in enumerate(titles):
        t.write(0,index,title)


def run():
    f = xlwt.Workbook()
    t_org = f.add_sheet("org")
    t_org_title(t_org)
    t_user = f.add_sheet("user")
    t_user_title(t_user)

    conn = db.connect_torndb()
    orgs = conn.query("select * from organization where type=17020 "
                      "order by trial, serviceEndDate desc, id")
    line_org = 1
    line_user = 1
    for org in orgs:
        if org["trial"] is None:
            status = u"正式机构版"
        else:
            if org["serviceEndDate"] is None:
                continue

            if org["serviceEndDate"] < datetime.datetime.now():
                status = u"试用已结束"
            else:
                status = u"正在试用中"

        first_trial_user = conn.get("select u.*,t.createTime as startTrialTime from user_start_trial t join user u "
                                    "on t.userId=u.id "
                                    "where t.orgId=%s "
                                    "order by createTime desc limit 1",
                                    org["id"])

        logger.info("%s, %s, %s, %s, %s",
                    org["id"], org["name"], status, org["createTime"],
                    org["serviceEndDate"])
        if first_trial_user:
            logger.info("first trial user: %s, %s", first_trial_user["username"], first_trial_user["startTrialTime"])

        #已关联机构
        result = conn.get("select count(*) cnt from user_organization_rel where organizationId=%s", org["id"])
        verified_cnt = result["cnt"]
        result = conn.get("select count(*) cnt from user_organization_rel r join user u on r.userId=u.id "
                          "where organizationId=%s and lastLoginTime is not null", org["id"])
        verified_login_cnt = result["cnt"]
        result = conn.get("select count(*) cnt from user_organization_rel r join user u on r.userId=u.id "
                          "where organizationId=%s and lastLoginTime is not null and r.trial='Y'", org["id"])
        verified_trial_cnt = result["cnt"]
        logger.info("%s, %s, %s", verified_cnt, verified_login_cnt, verified_trial_cnt)

        #未关联机构
        org_name = org["name"]
        email_domain = ""
        if org["emailDomain"] is not None and org["emailDomain"] != "":
            email_domain = " or u.email like '%%@" + org["emailDomain"] + "'"
        sql = "select count(*) cnt from user u \
                        left join (select o.*,r.userId userId from user_organization_rel r join organization o on r.organizationId=o.id and o.type=17020) o1 \
                        on u.id=o1.userId \
                        left join (select o.*,r.userId from user_organization_rel r join organization o on r.organizationId=o.id and o.type=17010) o2 \
                        on u.id=o2.userId \
                    where o1.id is null and o2.id is not null and \
                          (o2.name='" + org_name + "'" + email_domain + ")"
        # logger.info(sql)
        result = conn.get(sql)
        unverified_cnt = result["cnt"]

        sql = "select count(*) cnt from user u \
                        left join (select o.*,r.userId userId from user_organization_rel r join organization o on r.organizationId=o.id and o.type=17020) o1 \
                        on u.id=o1.userId \
                        left join (select o.*,r.userId from user_organization_rel r join organization o on r.organizationId=o.id and o.type=17010) o2 \
                        on u.id=o2.userId \
                    where o1.id is null and o2.id is not null and \
                                  (o2.name='" + org_name + "'" + email_domain + ") \
                                   and u.lastLoginTime is not null"
        # logger.info(sql)
        result = conn.get(sql)
        unverified_login_cnt = result["cnt"]

        logger.info("%s, %s", unverified_cnt, unverified_login_cnt)

        logger.info("")

        col = 0
        t_org.write(line_org, col, org["id"]); col += 1
        t_org.write(line_org, col, org["name"]); col += 1
        t_org.write(line_org, col, status); col += 1
        t_org.write(line_org, col, org["createTime"].strftime('%Y.%m.%d')); col += 1
        if first_trial_user:
            t_org.write(line_org, col, first_trial_user["startTrialTime"].strftime('%Y.%m.%d'))
        col += 1
        if org["serviceEndDate"]:
            t_org.write(line_org, col, org["serviceEndDate"].strftime('%Y.%m.%d'))
        col += 1
        t_org.write(line_org, col, verified_cnt); col += 1
        t_org.write(line_org, col, verified_login_cnt); col += 1
        t_org.write(line_org, col, verified_trial_cnt); col += 1
        t_org.write(line_org, col, unverified_cnt); col += 1
        t_org.write(line_org, col, unverified_login_cnt); col += 1

        line_org += 1


        #用户
        # 已关联机构
        items = conn.query("select * from user_organization_rel where organizationId=%s", org["id"])
        for item in items:
            user = conn.get("select * from user where id=%s", item["userId"])
            col = 0
            t_user.write(line_user, col, org["id"])
            col += 1
            t_user.write(line_user, col, org["name"])
            col += 1
            t_user.write(line_user, col, user["username"])
            col += 1
            if org["trial"] is None:
                status = u"正式机构版"
            else:
                if item["trial"] == 'Y':
                    status = u"已试用"
                else:
                    status = u"未试用"
            t_user.write(line_user, col, status)
            col += 1
            t_user.write(line_user, col, user["verifiedInvestor"])
            col += 1
            t_user.write(line_user, col, get_user_type(user["userIdentify"]))
            col += 1
            t_user.write(line_user, col, user["position"])
            col += 1
            t_user.write(line_user, col, get_user_roles(user["id"]))
            col += 1
            t_user.write(line_user, col, user["active"])
            col += 1
            t_user.write(line_user, col, user["createTime"].strftime('%Y.%m.%d'))
            col += 1
            if user["lastLoginTime"]:
                t_user.write(line_user, col, user["lastLoginTime"].strftime('%Y.%m.%d'))
            col += 1

            mongo = db.connect_mongo()
            log = mongo.log.api_log.find_one({"requestURL": '/api/user/upgrade/upgrade', "userId":user["id"]})
            mongo.close()
            if log:
                t_user.write(line_user, col, log["time"].strftime('%Y.%m.%d'))
            col += 1

            if org["serviceEndDate"] and item["trial"] == "Y":
                t_user.write(line_user, col, org["serviceEndDate"].strftime('%Y.%m.%d'))
            col += 1

            t_user.write(line_user, col, user["email"])
            col += 1
            t_user.write(line_user, col, user["emailVerify"])
            col += 1
            t_user.write(line_user, col, user["phone"])
            col += 1
            t_user.write(line_user, col, user["phoneVerify"])
            col += 1

            line_user += 1


        # 未关联机构
        sql = "select u.* from user u \
                                left join (select o.*,r.userId userId from user_organization_rel r join organization o on r.organizationId=o.id and o.type=17020) o1 \
                                on u.id=o1.userId \
                                left join (select o.*,r.userId from user_organization_rel r join organization o on r.organizationId=o.id and o.type=17010) o2 \
                                on u.id=o2.userId \
                            where o1.id is null and o2.id is not null and \
                                  (o2.name='" + org_name + "'" + email_domain + ")"
        items = conn.query(sql)
        for item in items:
            user = item
            col = 0
            t_user.write(line_user, col, org["id"])
            col += 1
            t_user.write(line_user, col, org["name"])
            col += 1
            t_user.write(line_user, col, user["username"])
            col += 1
            t_user.write(line_user, col, u"疑似同机构")
            col += 1
            t_user.write(line_user, col, user["verifiedInvestor"])
            col += 1
            t_user.write(line_user, col, get_user_type(user["userIdentify"]))
            col += 1
            t_user.write(line_user, col, user["position"])
            col += 1
            t_user.write(line_user, col, get_user_roles(user["id"]))
            col += 1
            t_user.write(line_user, col, user["active"])
            col += 1
            t_user.write(line_user, col, user["createTime"].strftime('%Y.%m.%d'))
            col += 1
            if user["lastLoginTime"]:
                t_user.write(line_user, col, user["lastLoginTime"].strftime('%Y.%m.%d'))
            col += 1

            col += 1
            col += 1

            t_user.write(line_user, col, user["email"])
            col += 1
            t_user.write(line_user, col, user["emailVerify"])
            col += 1
            t_user.write(line_user, col, user["phone"])
            col += 1
            t_user.write(line_user, col, user["phoneVerify"])
            col += 1

            line_user += 1

    conn.close()

    f.save('logs/org.xls')


def get_user_type(type):
    user_types = {
        61010:u"投资人",
        61020:u"FA",
        61030:u"创业者",
        61040:u"其他"
    }
    return user_types[type]

def get_user_roles(user_id):
    roles = {
        25010:u"机构内部管理员",
        25020:u"创业者",
        25030:u"合伙人",
        25031:u"董事总经理",
        25032:u"副总裁",
        25033:u"投资总监",
        25040:u"投资经理",
        25041:u"分析师",
        25042:u"投后",
        25050:u"其他",
        25060:u"后台管理员",
        25070:u"数据维护",
        25080:u"其他"
    }
    conn = db.connect_torndb()
    rs = conn.query("select * from user_role where userId=%s order by role", user_id)
    conn.close()
    temps = []
    for r in rs:
        temps.append(roles[r["role"]])
    return ", ".join(temps)


if __name__ == '__main__':
    run()
