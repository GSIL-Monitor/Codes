# -*- coding: utf-8 -*-
import os, sys
import datetime
import traceback
from mako.template import Template
import pymongo

import track_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, email_helper, funding_helper

#logger
loghelper.init_logger("track_email", stream=True)
logger = loghelper.get_logger("track_email")


def process():
    conn = db.connect_torndb()
    orgs = conn.query("select o.* from organization o "
                      "join org_menu_rel r on o.id=r.orgId "
                      "where "
                      "o.serviceStatus='Y' and (o.active is null or o.active='Y') and "
                      "r.active='Y' and r.orgMenuId=8")
    conn.close()

    for org in orgs:
        # if org["id"] not in [51, 7, 343, 14459]:     # Test
        # if org["id"] not in [14459]:  # Test
        #     continue
        conn = db.connect_torndb()
        users = conn.query("select u.* from user u "
                           "join user_organization_rel r on u.id=r.userId "
                           "where "
                           "r.active='Y' and "
                           "(u.active=null or u.active not in ('D','B')) and "
                           "u.emailVerify='Y' and "
                           "u.email is not null and u.email !='' and "
                           "r.organizationId=%s",
                           org["id"])
        conn.close()
        for user in users:
            # 12286, 14703 刘林
            # 14787 杜强测试
            # if user["id"] not in [221, 14787]:     # Test
            #     continue
            email = user["email"]
            if "@" not in email:
                continue
            try:
                process_one(org, user)
            except Exception, e:
                logger.exception(e)
                traceback.print_exc()


def process_one(org, user):
    today = datetime.datetime.now()
    yesterday = today + datetime.timedelta(days=-1)
    start_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 19, 0, 0)
    # start_time = datetime.datetime(2018, 7, 1, 19, 0, 0)
    end_time = datetime.datetime(today.year, today.month, today.day, 19, 0, 0)

    logger.info("org: %s, user: %s, start time: %s, end time: %s", org["name"], user["username"], start_time, end_time)
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    groups = []

    company_message_cnt = 0
    investor_message_cnt = 0

    personal_company_group = conn.get(" select * from track_group where "
                                      " active='Y' and userId=%s and type=82001 and sendEmail='Y'"
                                      " order by id desc limit 1",
                                      user["id"])
    if personal_company_group is not None:
        groups.append(personal_company_group)

    personal_investor_group = conn.get(" select * from track_group where"
                                       " active='Y' and userId=%s and type=82002 and sendEmail='Y'"
                                       " order by id desc limit 1",
                                      user["id"])
    if personal_investor_group is not None:
        groups.append(personal_investor_group)


    org_groups = None
    if org["serviceType"] == 80003:
        org_groups = conn.query(" select g.* from track_group g "
                            " join track_group_user_rel r on g.id=r.trackGroupId "
                            " where "
                            " g.active='Y' and "
                            " r.active='Y' and "
                            " g.userId is null and "
                            " g.sendEmail='Y' and "
                            " r.userId=%s and g.organizationId=%s "
                            " order by g.type, g.id desc",
                            user["id"], org["id"])
        groups.extend(org_groups)

    if len(groups) == 0:
        # 全部分组设定为不发邮件
        mongo.close()
        conn.close()
        return

    company_cnt = 0
    investor_cnt = 0

    for g in groups:
        result = conn.get(" select count(*) cnt from track_group_item_rel where "
                          " active='Y' and trackGroupId=%s", g["id"])
        if g["type"] == 82001:
            company_cnt += result["cnt"]
        elif g["type"] == 82002:
            investor_cnt += result["cnt"]

        logger.info("company cnt: %s, investor cnt: %s", company_cnt, investor_cnt)

        messages = list(mongo.message.user_message2.find({
            "userId": user["id"],
            "trackGroupId": g["id"],
            "publishTime": {
                "$gte": track_util.from_utc8_to_utc0(start_time),
                "$lt": track_util.from_utc8_to_utc0(end_time)
            }
        }).sort("publishTime", pymongo.DESCENDING))

        for m in messages:
            if m["type"] == 5010:
                company_message_cnt += 1
                m["company"] = get_company(conn, m)
            elif m["type"] == 5030:
                investor_message_cnt += 1
                m["investor"] = get_investor(conn, m)
            dimension_name = get_dimension_name(conn, m)
            m["dimension_name"] = dimension_name
            content = get_content(conn, mongo, m)
            m["content"] = content

        g["messages"] = messages

    mongo.close()
    conn.close()

    data = {
        "org": org,
        "user": user,
        "personal_company_group": personal_company_group,
        "personal_investor_group": personal_investor_group,
        "org_groups": org_groups,
        "startTime": start_time.strftime("%m月%d日%H:%M"),
        "endTime": end_time.strftime("%m月%d日%H:%M"),
        "company_message_cnt": company_message_cnt,
        "investor_message_cnt": investor_message_cnt,
    }

    # logger.info(data)

    filename = "track.html"
    t = Template(filename='template/%s' % filename, input_encoding='utf-8', output_encoding='utf-8',
                 encoding_errors='replace')

    if company_cnt > 0:
        data["type"] = 82001
        content = t.render(data=data)
        # logger.info(content.decode('UTF-8'))
        title = "公司追踪日报（%s ~ %s）" % (data["startTime"], data["endTime"])
        email_helper.send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", user["email"], title, content)

    if investor_cnt > 0:
        data["type"] = 82002
        content = t.render(data=data)
        # logger.info(content.decode('UTF-8'))
        title = "投资机构追踪日报（%s ~ %s）" % (data["startTime"], data["endTime"])
        email_helper.send_mail("烯牛数据", "烯牛数据", "noreply@xiniudata.com", user["email"], title, content)




def get_company(conn, m):
    company_id = m["companyId"]
    company = conn.get("select * from company where id=%s", company_id)
    return company


def get_investor(conn, m):
    investor_id = m["investorId"]
    investor = conn.get("select * from investor where id=%s", investor_id)
    return investor


def get_dimension_name(conn, m):
    if m["type"] == 5010:
        _type = 82001
    elif m["type"] == 5030:
        _type = 82002
    else:
        return ""

    track_dimension = m["trackDimension"]
    r = conn.get("select s.* from track_sub_type s join track_type t on s.trackTypeId=t.id "
                 "where "
                 "t.type=%s and "
                 "trackDimension=%s",
                 _type, track_dimension)
    if r is not None:
        return r["name"]
    return ""


def get_content(conn, mongo, m):
    # TODO
    if m["type"] == 5010:
        return get_company_message_content(conn, mongo, m)
    elif m["type"] == 5030:
        return get_investor_message_content(conn, mongo, m)

APP_TYPE = {
    4010:'网站',
    4020:'微信',
    4030:'微博',
    4040:'iOS',
    4050:'安卓',
    4060:'小程序',
    4070:'PC',
    4080:'MAC',
    4099:''
}

DIMENSION = {
    1001: "媒体报道",

    2001: "发现新应用",
    2002: "重大版本更新",
    2003: "发布新版本",
    2004: "产品下架",
    2005: "90天未更新",
    3107: "入榜",
    3108: "出榜",
    3201: "下载量激增",

    4002: "长期无新职位发布",
    4004: "正在招聘核心职位",

    5001: "股东变更",
    5002: "注册资本变更",


    6001: "发现新的竞争对手",

    7002: "获得新融资",
}

GENRE = {
    "None": "总",
    "6000": "商务",
    "6022": "商品指南",
    "6017": "教育",
    "6016": "娱乐",
    "6015": "财务",
    "6023": "美食佳饮",
    "6013": "健康健美",
    "6012": "生活",
    "6020": "医疗",
    "6011": "音乐",
    "6010": "导航",
    "6009": "新闻",
    "6008": "摄影与录像",
    "6007": "效率",
    "6006": "参考",
    "6024": "购物",
    "6005": "社交",
    "6004": "体育",
    "6003": "旅游",
    "6002": "工具",
    "6001": "天气",
    "6014": "游戏",
    "6021": "报刊杂志",
    "6025": "贴纸",
    "7001": "动作游戏",
    "7002": "冒险游戏",
    "7003": "街机游戏",
    "7004": "桌面游戏",
    "7005": "卡牌游戏",
    "7006": "娱乐场游戏",
    "7007": "骰子游戏",
    "7008": "教育类游戏",
    "7009": "聚会游戏",
    "7011": "音乐游戏",
    "7012": "益智解谜",
    "7013": "赛车游戏解谜",
    "7014": "角色扮演游戏",
    "7015": "模拟游戏",
    "7016": "体育游戏",
    "7017": "策略游戏",
    "7018": "问答游戏",
    "7019": "文字游戏",
}

RANK_TYPE = {
    "free": "免费榜",
    "charge": "付费榜",
    "grossing": "畅销榜"
}


def get_company_message_content(conn, mongo, m):
    _id = m["companyMessageId"]
    m_mysql = conn.get("select * from company_message where id=%s", _id)

    if m['relateType'] == 10:  # 新闻
        return '<a href="http://www.xiniudata.com/news/' + m['relateId'] + '">' + m_mysql['message'] + '</a>'

    if m['trackDimension'] in [2001, 2002, 2003, 2004, 2005, 3107, 3108, 3201]:
        artifact = conn.get("select * from artifact where id=%s", m["relateId"])
        app = artifact["name"]
        app_type = APP_TYPE.get(artifact["type"], "")

        if m['trackDimension'] in [2004, 2005, 3201, 2001]:  #
            msg = "%s应用【%s】%s" % (app_type, app, DIMENSION.get(m['trackDimension'], ""))
            return msg

        desc = ""
        if m['trackDimension'] in [ 2002, 2003 ]:   #
            if artifact["type"] == 4040:    # iOS
                itunes = mongo.market.itunes.find_one({"trackId": int(artifact["domain"])})
                if itunes is not None:
                    updates = itunes["releaseNotes"]
                    if updates is None or updates.strip() == "":
                        updates = "无"
                    desc = "更新内容：%s" % updates
            elif artifact["type"] == 4050:  # 安卓
                android = mongo.market.android.find_one({"apkname": artifact["domain"]})
                if android is not None:
                    updates = android["updates"]
                    if updates is None or updates.strip() == "":
                        updates = "无"
                    desc = "更新内容：%s" % updates

        if m['trackDimension'] in [3107, 3108]:
            detail_id = m["detailId"]
            if detail_id is not None:
                strs = detail_id.split(",")
                if len(strs) == 2:
                    genre = strs[0]
                    rank_type = strs[1]
                    if m['trackDimension'] == 3107:
                        desc = "入围%s-%s前100名" % (GENRE.get(genre, ""), RANK_TYPE.get(rank_type, ""))
                    if m['trackDimension'] == 3108:
                        desc = "跌出%s-%s前100名" % (GENRE.get(genre, ""), RANK_TYPE.get(rank_type, ""))

        msg = "%s应用【%s】%s" % (app_type, app, desc)
        return msg

    if m['trackDimension'] == 7002:  # 公司完成新一轮融资
        funding_id = m['relateId']
        funding = conn.get("select * from funding where id=%s", funding_id)
        str_money = funding_helper.gen_investment_desc(funding["investment"], funding["precise"], funding["preciseDesc"],
                                                  funding["currency"])
        if str_money == "金额未知":
            str_money = '未披露'
        str_investors = funding_helper.gen_investors(funding["investorsRaw"], funding["investors"])
        if str_investors != "未透露":
            str_investors = "为%s" % str_investors
        msg = "获得新一轮融资，轮次%s，金额%s，投资机构%s" % \
              (funding_helper.get_round_desc(funding["round"]),
               str_money,
               str_investors
               )
        return msg

    if m['trackDimension'] in [5001, 5002]:
        msg = m_mysql["message"]
        if msg is None or msg.strip() == "":
            msg = "变更信息未披露"
        return msg

    if m['trackDimension'] == 6001:
        relate_id = m["relateId"]
        cs = conn.query("select name from company where id in (" + relate_id + ")")
        msg = "发现了%s个潜在竞争对手：%s" % (len(cs), ", ".join([c["name"] for c in cs]))
        return msg

    if m['trackDimension'] == 4002:
        msg = "期无新职位发布"
        return msg

    if m['trackDimension'] == 4004:
        msg = "正在招核心岗位"
        return msg

    return m_mysql["message"]


def get_investor_message_content(conn, mongo, m):
    _id = m["investorMessageId"]
    m_mysql = conn.get("select * from investor_message where id=%s", _id)
    if m['relateType'] == 10:
        return '<a href="http://www.xiniudata.com/news/' + m['relateId'] + '">' + m_mysql['message'] + '</a>'

    if m['trackDimension'] == 7002:  # 完成新一轮融资
        funding_id = m['relateId']
        funding = conn.get("select * from funding where id=%s", funding_id)
        company = conn.get("select * from company where id=%s", funding["companyId"])
        str_money = funding_helper.gen_investment_desc(funding["investment"], funding["precise"],
                                                       funding["preciseDesc"],
                                                       funding["currency"])
        if str_money == "金额未知":
            str_money = '未披露'

        str_investors = funding_helper.gen_investors(funding["investorsRaw"], funding["investors"])
        if str_investors != "未透露":
            str_investors = "为%s" % str_investors

        msg = '投资了<a href="https://www.xiniudata.com/company/%s/overview">%s</a>，轮次%s，金额%s，投资机构%s' % \
              (company["code"], company["name"],
               funding_helper.get_round_desc(funding["round"]),
               str_money,
               str_investors)
        return msg

    if m['trackDimension'] == 7005:
        funding_id = m['relateId']
        funding = conn.get("select * from funding where id=%s", funding_id)
        company = conn.get("select * from company where id=%s", funding["companyId"])
        round = funding_helper.get_round_desc(funding["round"])
        if round == "轮次未知":
            round = "未披露"
        else:
            round = "为%s" % round
        msg = '退出了<a href="https://www.xiniudata.com/company/%s/overview">%s</a>，退出方式%s' % \
              (company["code"], company["name"], round)
        return msg

    if m['trackDimension'] == 7006:  # 已投项目发生投资事件
        funding_id = m['relateId']
        funding = conn.get("select * from funding where id=%s", funding_id)
        company = conn.get("select * from company where id=%s", funding["companyId"])
        str_money = funding_helper.gen_investment_desc(funding["investment"], funding["precise"],
                                                       funding["preciseDesc"],
                                                       funding["currency"])
        if str_money == "金额未知":
            str_money = '未披露'

        str_investors = funding_helper.gen_investors(funding["investorsRaw"], funding["investors"])
        if str_investors != "未透露":
            str_investors = "为%s" % str_investors

        msg = '投资过的<a href="https://www.xiniudata.com/company/%s/overview">%s</a>获得新一轮融资，轮次%s，金额%s，投资机构%s' % \
              (company["code"], company["name"],
               funding_helper.get_round_desc(funding["round"]),
               str_money,
               str_investors)
        return msg

    return m_mysql["message"]


if __name__ == "__main__":
    process()