# -*- coding: utf-8 -*-
import os, sys
import pandas as pd

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("export_tag", stream=True)
logger = loghelper.get_logger("export_tag")

conn = db.connect_torndb()
mongo = db.connect_mongo()

# 以太
company_ids = [
    7751,
    35614,
    204899,
    311791,
    198648,
    176980,
    83256,
    19668,
    117838,
    11664,
    22543,
    34096,
    19976,
    177088,
    35923,
    103823,
    244314,
    253455,
    197747,
    114992,
    330467,
    1161,
    1083,
    234077,
    255003,
    254983,
    329244,
    211088,
    20549,
    171588
]

# 旅游
# company_ids = [
#     22810, # 脆饼Tripinsiders
#     285722, #  明珠国际
#     7939, #  趣自游
#     23214, #  如影旅行网
#     102711, #  下一站
#     45521, #  收客易
#     17324, #  经过旅行
#     65142, #  爱聚吧
#     4717, #  八爪鱼在线旅游
#     115501, #  玩马旅行
#     197282, #  千宿
#     136953, #  玩赚世界
#     182914, #  Journi
#     288, #  小猪短租
#     303970, #  免签精选游
#     4418, #  iGola骑鹅旅行
#     190330, #  自游圈
#     12680, #  一家民宿
#     25506, #  内蒙古旅游目的地服务平台
#     19546, #  UU客
#     205190, #  尝途旅行
#     152808, #  银河漫游指南
#     253498, #  穷游网
#     36271, #  诗莉莉
#     205564, #  TATAMi
#     254542, #  稀客地图
#     1997, #  要出发旅行网
#     96508, #  欢逃游旅行网
#     19261, #  信息驿站
#     311566, #  乐派网
# ]

# 以太100个项目
company_fullnames = [
    '蓝白科技股份有限公司',
    '杭州博拉网络科技有限公司',
    '北京绘本原创教育科技有限公司',
    '上海聚虹光电科技有限公司  ',
    '深圳市百锦丰餐饮管理有限公司',
    '慷探网络科技（上海）有限公司',
    '北京东华宏泰科技股份有限公司',
    '雾联智能技术（上海）有限公司',
    '魔方天空科技（北京）有限公司',
    '上海炘璞电子科技有限公司',
    '深圳市康比特信息技术有限公司',
    '北京优朋普乐科技有限公司',
    341018, #'上海易跋信息科技有限公司',
    '云南真美度假酒店管理有限公司',
    '魔方天空科技（北京）有限公司',
    '厦门变格新材料科技有限公司',
    '广州云实信息科技有限公司',
    '北京丽家丽婴婴童用品有限公司',
    '深圳市奇诺动力科技有限公司',
    '珊口（上海）智能科技有限公司',
    '北京踏浪者科技有限公司',
    '上海傲天活力信息科技有限公司',
    '臻云智能（北京）投资管理有限公司',
    '宁波启点教育科技有限公司',
    '迈骆（上海）医疗供应链管理有限公司',
    '上海数据交易中心有限公司',
    '北京悦活餐饮管理有限责任公司',
    '深圳北斗应用技术研究院有限公司',
    '广州科天视畅信息科技有限公司',
    '云南新康医疗管理集团有限公司',
    '美国皇家加勒比国际游轮公司',
    '康膝生物医疗（深圳）有限公司',
    '上海天奕无线信息科技有限公司',
    '广州景联信息科技有限公司',
    '上海瓶钵信息科技有限公司',
    '北京智普信科技股份有限公司',
    '上海云砺信息科技有限公司',
    '北京蓦然认知科技有限公司',
    '北京康夫子科技有限公司',
    '北京火币天下网络技术有限公司',
    '北京好扑信息科技有限公司',
    '深圳市星炫科技有限公司',
    '深圳奥比中光科技有限公司',
    '北京伟景智能科技有限公司',
    '北京工商未知信息技术有限公司',
    '北京小马智行科技有限公司',
    '北京智齿博创科技有限公司',
    '北京尚世骁众科技有限公司',
    '北京星尘纪元智能科技有限公司',
    '深圳视见医疗科技有限公司',
    '北京深醒科技有限公司',
    '上海千颂网络科技有限公司',
    '北京凯声文化传媒有限责任公司',
    '北京桔子树音乐艺术培训有限公司',
    '上海佰集信息科技有限公司 ',
    '上海积梦智能科技有限公司',
    '承承网络科技（上海）有限公司',
    '触景无限科技（北京）有限公司',
    '深圳市编玩边学教育科技有限公司',
    '辰星（天津）自动化设备有限公司',
    '北京陌上花科技有限公司',
    '上海肇观电子科技有限公司',
    '苏州绿的谐波传动科技有限公司',
    '深圳市很有蜂格网络科技有限公司',
    '北京羽医甘蓝信息技术有限公司',
    '智擎信息技术（北京）有限公司',
    '上海云拿智能科技有限公司',
    '北京饮冰科技有限公司',
    '广州市人心网络科技有限公司',
    '北京中经智元科技发展有限公司',
    '上海证大喜马拉雅网络科技有限公司',
    '杭州桃树科技有限公司',
    '南京创普客商业管理有限公司',
    '北京魔力耳朵科技有限公司',
    '合肥码隆信息科技有限公司',
    '北京灵智优诺科技有限公司',
    '北京享阅教育科技有限公司',
    '上海分布信息科技有限公司',
    '北京迈瑞科教育科技有限公司',
    '杭州灵伴科技有限公司',
    '北京柏惠维康科技有限公司',
    '深圳佑驾创新科技有限公司',
    '知我探索教育科技（北京）有限公司',
    '中科视拓（北京）科技有限公司',
    '中科聚信信息技术（北京）有限公司',
    '西安翼展电子科技有限公司 ',
    '深圳市一面网络技术有限公司',
    '逻辑起点科技（北京）有限公司',
    '深圳星行科技有限公司',
    '杭州小码教育科技有限公司',
    '上海犀语科技有限公司',
    '上海图漾信息科技有限公司',
    '深图（厦门）科技有限公司',
    '北京深睿博联科技有限责任公司',
    '青岛福源祥经贸有限公司',
    '浙江安吉斯凯集成房屋科技有限公司',
    '北京无忧陪护信息技术有限公司',
    '广州房友圈网络科技有限公司',
    '杭州美窝科技有限公司',
]


def main():
    for company_id in company_ids:
        company = conn.get("select * from company where id=%s", company_id)

        # old tags
        tags = list(conn.query("select t.name from company_tag_rel_bak  r join tag t on r.tagId=t.id where "
                               "(r.active is null or r.active='Y') and "
                               "(t.active is null or t.active='Y') and "
                               "r.companyId=%s "
                               "order by r.confidence desc",
                               company_id))
        old_tag_names = []
        for tag in tags:
            old_tag_names.append(tag["name"])

        # key tags
        key_tag = mongo.keywords.majorchain.find_one({"company": company_id})
        if key_tag is None:
            key_tag_names = []
        else:
            key_tag_names = key_tag.get("major")
            if key_tag_names is None:
                key_tag_names = []

        # new level tags
        tags = list(conn.query("select t.name from company_tag_rel r join tag t on r.tagId=t.id where "
                          "(r.active is null or r.active='Y') and "
                          "(t.active is null or t.active='Y') and "
                          "t.sectorType in (1, 2, 3) and "
                          "r.companyId=%s "
                          "order by r.confidence desc",
                          company_id))
        tag_names = []
        for tag in tags:
            if tag["name"] not in key_tag_names:
                tag_names.append(tag["name"])

        # new other tags
        tags = list(conn.query("select t.name from company_tag_rel r join tag t on r.tagId=t.id where "
                               "(r.active is null or r.active='Y') and "
                               "(t.active is null or t.active='Y') and "
                               "t.sectorType is null and "
                               "t.type != 11054 and t.type < 11100 and "
                               "r.companyId=%s "
                               "order by r.confidence desc",
                               company_id))
        other_tag_names = []
        for tag in tags:
            other_tag_names.append(tag["name"])

        # logger.info("%s|%s|%s|%s|%s|%s|%s|%s",
        #             company_id, company["code"],
        #             company["name"], company["brief"],
        #             company["description"].replace("\n","").replace("\r", ""),
        #             ", ".join(old_tag_names), ", ".join(tag_names), ", ".join(other_tag_names))
        logger.info("%s|%s|%s|%s|%s|%s",
                    company["name"], company["brief"],
                    company["description"].replace("\n", "").replace("\r", ""),
                    ", ".join(key_tag_names),
                    ", ".join(tag_names),
                    ", ".join(other_tag_names)
                    )


def find_company(full_name):
    corporate = conn.get("select * from corporate where fullname=%s and (active is null or active='Y') limit 1",
                         full_name)
    if corporate is None:
        corporate = conn.get("select c.* from corporate c join corporate_alias a on c.id=a.corporateId "
                                   "where a.name=%s and "
                                   "(c.active is null or c.active='Y') and "
                                   "(a.active is null or a.active='Y') "
                                   "limit 1",
                         full_name)
    if corporate is None:
        return None

    company = conn.get("select * from company where corporateId=%s and (active is null or active='Y') "
                       "order by id desc limit 1",
                       corporate["id"])
    return company


def main2():

    data = {
        "id": [],
        "name":[],
        "fullName":[],
        "brief":[],
        "desc":[],
        "key123":[],
        "level123":[],
        "others": [],
    }

    for full_name in company_fullnames:
        if type(full_name) == int:
            company = conn.get("select * from company where id=%s", full_name)
            corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
            full_name = corporate["fullName"]
        else:
            full_name = full_name.strip().replace("(",u"（").replace(")",u"）")
            company = find_company(full_name)
        if company is None:
            data["id"].append("")
            data["name"].append("")
            data["fullName"].append(full_name)
            data["brief"].append("")
            data["desc"].append("")
            data["key123"].append("")
            data["level123"].append("")
            data["others"].append("")
            continue

        # key tags
        key_tag = mongo.keywords.majorchain.find_one({"company": company["id"]})
        if key_tag is None:
            key_tag_names = []
        else:
            key_tag_names = key_tag.get("major")
            if key_tag_names is None:
                key_tag_names = []

        # new level tags
        tags = list(conn.query("select t.name from company_tag_rel r join tag t on r.tagId=t.id where "
                               "(r.active is null or r.active='Y') and "
                               "(t.active is null or t.active='Y') and "
                               "t.sectorType in (1, 2, 3) and "
                               "r.companyId=%s "
                               "order by r.confidence desc",
                               company["id"]))
        tag_names = []
        for tag in tags:
            if tag["name"] not in key_tag_names:
                tag_names.append(tag["name"])

        # new other tags
        tags = list(conn.query("select t.name from company_tag_rel r join tag t on r.tagId=t.id where "
                               "(r.active is null or r.active='Y') and "
                               "(t.active is null or t.active='Y') and "
                               "t.sectorType is null and "
                               "t.type != 11054 and t.type < 11100 and "
                               "r.companyId=%s "
                               "order by r.confidence desc",
                               company["id"]))
        other_tag_names = []
        for tag in tags:
            other_tag_names.append(tag["name"])

        if company["description"] is None:
            company["description"] = ""

        logger.info("%s|%s|%s|%s|%s|%s",
                    company["name"], full_name, company["brief"],
                    company["description"].replace("\n", "").replace("\r", ""),
                    ", ".join(tag_names), ", ".join(other_tag_names))
        data["id"].append(company["id"])
        data["name"].append(company["name"])
        data["fullName"].append(full_name)
        data["brief"].append(company["brief"])
        data["desc"].append(company["description"])
        data["key123"].append(", ".join(key_tag_names))
        data["level123"].append(", ".join(tag_names))
        data["others"].append(", ".join(other_tag_names))

    df = pd.DataFrame(data)
    df.to_excel('logs/tag_export.xlsx', index=False,
                columns=['id','name','fullName','brief','desc','key123','level123','others'],
                header=['id', u'项目名',u'公司名',u'一句话简介',u'简介',u'烯牛最匹配123级标签',u'烯牛其它123级标签',u'烯牛其它标签'])


if __name__ == '__main__':
    main2()