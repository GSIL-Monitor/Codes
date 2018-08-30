# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("migrate_companyfa_tag", stream=True)
logger = loghelper.get_logger("migrate_companyfa_tag")

'''
insert tag(id,name,type,createTime,modifyTime) values(591703,'微软加速器', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591704,'氪空间', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591705,'奥迪创新实验室', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591706,'戈壁创投VCDay', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591707,'天使湾', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591708,'清科', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591709,'投中', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591710,'小饭桌', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591711,'i黑马', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591712,'微链', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591713,'创业邦', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591714,'TechCrunch', 11054, now(),now());
'''

rules1 = {
    #"13300": 591703,     #微软加速器
    #"13001": 591704,     #氪空间
    #"13500": 591705,     #奥迪创新实验室
    #"13501": 591706,     #戈壁创投VC Day
    #"13502": 591707,     #天使湾
    #"13503": 591708,     #清科
    #"13504": 591709,     #投中
    #"13505": 591710,     #小饭桌
    #"13506": 591711,     #i黑马
    #"13802": 591712,     #微链
    #"13806": 591713,     #创业邦
    #"13815": 591714      #TechCrunch

}

'''
insert tag(id,name,type,createTime,modifyTime) values(591715,'微软加速器第八期', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591716,'微软加速器第九期', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591717,'微软加速器北京第十期', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591718,'微软加速器上海第一期', 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591730,'氪空间第七期', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591731,'氪空间第八期', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591732,'氪空间第九期', 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591733,'奥迪创新实验室2016', 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591734,'天使湾2016秋季观潮会路演', 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591735,'清科2016中国最具投资价值企业新芽榜50强', 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591736,'清科2016中国最具投资价值企业50强', 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591754,"投中2016年中国最具潜力成长企业TOP50", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591738,"投中2016年中国最具成长价值企业TOP50", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591739,"投中2016年度中国互联网产业最佳互联网/移动互联网领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591740,"投中2016年度中国互联网产业最佳大数据/企业服务领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591741,"投中2016年度中国互联网产业最佳退出案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591742,"投中2016年度中国医疗及健康服务产业最佳生物医药领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591743,"投中2016年度中国医疗及健康服务产业最佳医疗器械领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591744,"投中2016年度中国医疗及健康服务产业最佳医疗服务领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591745,"投中2016年度中国医疗及健康服务产业最佳退出案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591746,"投中2016年度中国消费及升级服务产业最佳品牌消费领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591747,"投中2016年度中国消费及升级服务产业最佳消费升级领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591748,"投中2016年度中国消费及升级服务产业最佳退出案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591749,"投中2016年度中国文化及娱乐传媒产业最佳内容领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591750,"投中2016年度中国文化及娱乐传媒产业最佳传播领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591751,"投中2016年度中国文化及娱乐传媒产业最佳体育领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591752,"投中2016年度中国先进制造与高科技产业最佳先进制造领域投资案例TOP10", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591753,"投中2016年度中国先进制造与高科技产业最佳人工智能领域投资案例TOP10", 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591755,"小饭桌2016年度新锐创业公司TOP30", 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591756,"i黑马2016年中国最具潜力创业公司-新锐组", 11054, now(),now());
insert tag(id,name,type,createTime,modifyTime) values(591757,"i黑马2016年中国最具潜力创业公司-成长组", 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591758,"微链2017消费升级研究报告暨新品牌100榜单", 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591759,"创业邦2017中国人工智能创新公司50强榜单", 11054, now(),now());

insert tag(id,name,type,createTime,modifyTime) values(591760,"TechCrunch2016创业大赛", 11054, now(),now());
'''
rules2 = {
    u"13300-第八期": 591715,
    u"13300-第九期": 591716,
    u"13300-北京第十期": 591717,
    u"13300-上海第一期": 591718,

    u"13301-第七期": 591730,
    u"13301-第八期": 591731,
    u"13301-第九期": 591732,

    u"13500-奥迪创新实验室2016": 591733,

    u"13501-VC Day": 591706,

    u"13502-2016秋季观潮会路演": 591734,

    u"13503-2016中国最具投资价值企业新芽榜50强": 591735,
    u"13503-2016中国最具投资价值企业50强": 591736,

    u"13504-投中2016年中国最具潜力成长企业TOP50": 591754,
    u"13504-投中2016年中国最具成长价值企业TOP50": 591738,
    u"13504-2016年度中国互联网产业最佳互联网/移动互联网领域投资案例TOP10": 591739,
    u"13504-2016年度中国互联网产业最佳大数据/企业服务领域投资案例TOP10": 591740,
    u"13504-2016年度中国互联网产业最佳退出案例TOP10": 591741,
    u"13504-2016年度中国医疗及健康服务产业最佳生物医药领域投资案例TOP10": 591742,
    u"13504-2016年度中国医疗及健康服务产业最佳医疗器械领域投资案例TOP10": 591743,
    u"13504-2016年度中国医疗及健康服务产业最佳医疗服务领域投资案例TOP10": 591744,
    u"13504-2016年度中国医疗及健康服务产业最佳退出案例TOP10": 591745,
    u"13504-2016年度中国消费及升级服务产业最佳品牌消费领域投资案例TOP10": 591746,
    u"13504-2016年度中国消费及升级服务产业最佳消费升级领域投资案例TOP10": 591747,
    u"13504-2016年度中国消费及升级服务产业最佳退出案例TOP10": 591748,
    u"13504-2016年度中国文化及娱乐传媒产业最佳内容领域投资案例TOP10": 591749,
    u"13504-2016年度中国文化及娱乐传媒产业最佳传播领域投资案例TOP10": 591750,
    u"13504-2016年度中国文化及娱乐传媒产业最佳体育领域投资案例TOP10": 591751,
    u"13504-2016年度中国先进制造与高科技产业最佳先进制造领域投资案例TOP10": 591752,
    u"13504-2016年度中国先进制造与高科技产业最佳人工智能领域投资案例TOP10": 591753,

    u"13505-2016年度新锐创业公司TOP30": 591755,

    u"13506-中国最具潜力创业公司-新锐组": 591756,
    u"13506-中国最具潜力创业公司-成长组": 591757,

    u"13802-2017消费升级研究报告暨新品牌100榜单": 591758,

    u"13806-2017中国人工智能创新公司50强榜单": 591759,

    u"13815-2016创业大赛": 591760
}


def add_tag(conn, company_id, tag_id):
    logger.info("companyId: %s, tagId: %s", company_id, tag_id)
    if company_id is None or tag_id is None:
        return
    rel = conn.get("select * from company_tag_rel where companyId=%s and tagId=%s limit 1",
                   company_id, tag_id)
    if rel is None:
        conn.insert("insert company_tag_rel(companyId,tagId,createTime,modifyTime,verify,confidence) values(%s,%s,now(),now(),'Y', 1.0)",
                    company_id, tag_id)
    else:
        if rel["active"] == 'N':
            conn.update("update company_tag_rel set active='Y',verify='Y',modifyTime=now(),confidence=1.0 where id=%s", rel["id"])


def process():
    conn = db.connect_torndb()
    items = conn.query("select * from company_fa where (active is null or active='Y') order by id")
    for item in items:
        company_id = item["companyId"]
        if company_id is None:
            continue
        source = item["source"]
        eventName = item["eventName"]
        if source is None:
            continue

        logger.info("id: %s, source: %s, eventName: %s, companyId: %s", item["id"], source, eventName, company_id)
        # tag_id1 = rules1.get(str(source))
        # if tag_id1 is not None:
        #     add_tag(conn, company_id, tag_id1)
        #     if eventName is not None and eventName != "":
        #         tag_id2 = rules2.get(str(source) + "-" + eventName)
        #         if tag_id2 is not None:
        #             add_tag(conn, company_id, tag_id2)
        #     conn.update("update company_fa set active='N',modifyUser=1078 where id=%s", item["id"])
        if eventName is not None and eventName != "":
            tag_id2 = rules2.get(str(source) + "-" + eventName)
            if tag_id2 is not None:
                add_tag(conn, company_id, tag_id2)
                # exit(0)
            conn.update("update company_fa set active='N',modifyUser=1078 where id=%s", item["id"])
    conn.close()


def tag2topic():
    conn = db.connect_torndb()
    for key, tag_id in rules2.items():
        t = key.split("-", 1)
        source = int(t[0])
        event_name = t[1]

        tag = conn.get("select * from tag where id=%s", tag_id)
        logger.info(tag["name"])

        # topic
        topic = conn.get("select * from topic where name=%s", tag["name"])
        if topic is None:
            topic_id = conn.insert("insert topic(name,shortName,active,autoPublish,recommend,hot,"
                                   "sectorRelevant,general,onlyForInvestor,type,autoExpand,"
                                   "createTime,modifyTime) values("
                                   "%s, %s, 'P','N','N','N',"
                                   "'N','N','N',902,'N',"
                                   "now(),now())", tag["name"], tag["name"])
        else:
            topic_id = topic["id"]
        logger.info("topicId: %s", topic_id)

        # topic_tag_rel
        rel = conn.get("select * from topic_tag_rel where topicId=%s and tagId=%s", topic_id, tag_id)
        if rel is None:
            conn.insert("insert topic_tag_rel(topicId,tagId,createTime,modifyTime,verify,active) "
                        "values(%s, %s, now(),now(),'Y','Y')",
                        topic_id, tag_id)

        # topic_tab
        tab = conn.get("select * from topic_tab where topicId=%s and type=1200", topic_id)
        if tab is None:
            topicTabId = conn.insert("insert topic_tab(topicId,name,type,subType,createTime,modifyTime,sort) "
                                     "values(%s,%s,1200,1200,now(),now(),1)",
                                     topic_id, u"相关公司")
        else:
            topicTabId = tab["id"]

        # topic_company
        cs = conn.query("select companyId from company_tag_rel where tagId=%s and (active is null or active='Y')",
                        tag_id)
        for c in cs:
            company_id = c["companyId"]
            logger.info("companyId: %s", company_id)
            tc = conn.get("select * from topic_company where topicId=%s and companyId=%s limit 1",
                          topic_id, company_id)
            if tc is None:
                f = conn.get("select * from company_fa where companyId=%s and source=%s and eventName=%s "
                             "order by id desc limit 1",
                             company_id, source, event_name)
                publishTime = f["publishDate"]
                topicCompanyId = conn.insert("insert topic_company(topicId,companyId,publishTime,createTime,modifyTime,"
                                             "active,pushStatus,tabStatus,sectorStatus) "
                                             "values(%s,%s,%s,now(),now(),'Y',1,1,1)",
                                             topic_id, company_id, publishTime)
            else:
                topicCompanyId = tc["id"]

            # topic_tab_company_rel
            rel = conn.get("select * from topic_tab_company_rel where topicCompanyId=%s and topicTabId=%s",
                           topicCompanyId, topicTabId)
            if rel is None:
                conn.insert("insert topic_tab_company_rel(topicTabId,topicCompanyId,createTime,modifyTime) "
                            "values(%s,%s,now(),now())",
                            topicTabId, topicCompanyId)

            # topic_company_sector_rel
            patch_sector_by_company_sector(topicCompanyId, company_id, conn)
        # exit(0)
    conn.close()


def patch_sector_by_company_sector(topicCompanyId, companyId, conn):
    conn.execute("delete from topic_company_sector_rel where topicCompanyId=%s", topicCompanyId)
    sectors = get_company_sectors(companyId, conn)
    for sector in sectors:
        conn.insert("insert topic_company_sector_rel(topicCompanyId,sectorId) values(%s,%s)",
                    topicCompanyId, sector["id"])


def get_company_sectors(company_id, conn):
    sectors = conn.query("select s.* from company_tag_rel r join tag t on t.id=r.tagId "
                      "join sector s on s.tagId=t.Id "
                      "where (r.active is null or r.active='Y') and (t.active is null or t.active='Y') "
                      "and s.level=1 and s.active='Y' "
                      "and r.companyId=%s and t.type=11012", company_id)
    return sectors


def colletion2topic():
    conn = db.connect_torndb()
    collections = conn.query("select * from collection where type=39020 and (active is null or active='Y')")
    for collection in collections:
        # topic
        topic = conn.get("select * from topic where name=%s", collection["name"])
        if topic is None:
            topic_id = conn.insert("insert topic(name,shortName,active,autoPublish,recommend,hot,"
                                   "sectorRelevant,general,onlyForInvestor,type,autoExpand,"
                                   "createTime,modifyTime) values("
                                   "%s, %s, 'P','N','N','N',"
                                   "'N','N','N',902,'N',"
                                   "now(),now())", collection["name"], collection["name"])
        else:
            topic_id = topic["id"]
        logger.info("topicId: %s", topic_id)

        # topic_tab
        tab = conn.get("select * from topic_tab where topicId=%s and type=1200", topic_id)
        if tab is None:
            topicTabId = conn.insert("insert topic_tab(topicId,name,type,subType,createTime,modifyTime,sort) "
                                     "values(%s,%s,1200,1200,now(),now(),1)",
                                     topic_id, u"相关公司")
        else:
            topicTabId = tab["id"]

        # topic_company
        cs = conn.query("select c.id, r.createTime from collection_company_rel r join company c on c.id=r.companyId "
                        "where collectionId=%s and (r.active is null or r.active='Y') "
                        "and (c.active is null or c.active='Y')",
                        collection["id"])
        for c in cs:
            company_id = c["id"]
            logger.info("companyId: %s", company_id)
            tc = conn.get("select * from topic_company where topicId=%s and companyId=%s limit 1",
                          topic_id, company_id)
            if tc is None:
                topicCompanyId = conn.insert("insert topic_company(topicId,companyId,publishTime,createTime,modifyTime,"
                                             "active,pushStatus,tabStatus,sectorStatus) "
                                             "values(%s,%s,%s,now(),now(),'Y',1,1,1)",
                                             topic_id, company_id, c["createTime"])
            else:
                topicCompanyId = tc["id"]

            # topic_tab_company_rel
            rel = conn.get("select * from topic_tab_company_rel where topicCompanyId=%s and topicTabId=%s",
                           topicCompanyId, topicTabId)
            if rel is None:
                conn.insert("insert topic_tab_company_rel(topicTabId,topicCompanyId,createTime,modifyTime) "
                            "values(%s,%s,now(),now())",
                            topicTabId, topicCompanyId)

            # topic_company_sector_rel
            patch_sector_by_company_sector(topicCompanyId, company_id, conn)
        # exit(0)
    conn.close()


def tag_4_topic(topic_id):
    conn = db.connect_torndb()
    tags = conn.query("select * from topic_tag_rel where topicId=%s and (active is null or active='Y')", topic_id)
    companies = conn.query("select * from topic_company where topicId=%s and (active is null or active='Y')", topic_id)
    for tag in tags:
        for company in companies:
            logger.info("companyId: %s", company["companyId"])
            add_tag(conn, company["companyId"], tag["tagId"])
            # exit()
    conn.close()


if __name__ == '__main__':
    # process()  # tag
    # tag2topic()
    # colletion2topic()
    tag_4_topic(65)

