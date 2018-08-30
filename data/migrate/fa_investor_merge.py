# -*- coding: utf-8 -*-
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("fa_investor_merge", stream=True)
logger = loghelper.get_logger("fa_investor_merge")

conn = db.connect_torndb()

FA = [
    (1, 1331), # 以太
    (2, 15757), # 华兴Alpha (new)
    (3, 2789),  # 小饭桌
    (4, 2508), # 36Kr
    (5, 3667), # 方创
    (6, 15759), # IPRdaily (new)
    (7, 15760), # 铅笔道 (new)
    (8, 3308), # 易凯资本
    (9, 1237), # 光源资本
    (10,15761), # 本初资本 (new, 无信息)
    (11,15762), # 势能资本 (new)
    (12,15763), # 清科资本 (new)
    (13,15764), # 华兴逐鹿 (new)
    (14,312), # 华兴资本
    (15,15765), # 浩悦资本 (new)
    (16,14917), # 凡卓资本
    (17,484), # 天使汇
    (18,15766), # 安可资本 (new)
    (19,15767), # Clipperton (new)
    (20,194), # 汉能资本
    (21,15768), # 毅仁资本 (new, 无信息)
    (22,15769), # 氧气资本 (new)
    (23,10782), # 泰合资本
    (24,15770), # 升维资本 (new)
    (25,15771), # 强云资本 (new)
    (26,3994), # 穆棉资本
    (27,1331), # 以太资本
    (28,3676), # 青桐资本
    (29,1331), #  致远资本
    (30,15781), # 独角兽资本 (new, 无信息)
    (31,15780), # 猎云资本
    (32,2806), # 星汉资本
    (33,15782), # 清科项目工场
    (34,15778), # BFC Group
    (35,15773), # 优氪资本 (new)
    (36,194), # 汉能投资
    (37,3667), # 方创资本
    (38,10524), # 中同资本
    (39,8436), # 华峰资本
    (40,15779), # 海通国际
    (41,15774), # 论道资本 (new)
    (42,15775), # 懒熊体育
    (43,3668), # 云岫资本
    (44,15776), # 美驰集团
    (45,15777), # FuTechVC
]


def get_investor_id(fa_id):
    for fa in FA:
        _fa_id, investor_id = fa
        if _fa_id == fa_id:
            return investor_id
    return None


def main():
    # # fa->investor
    # for fa in FA:
    #     fa_id, investor_id = fa
    #     conn.update("update investor set fa='Y' where id=%s", investor_id)

    # funding.faId -> funding_fa_rel
    items = conn.query("select * from funding where faId is not null and (active is null or active='Y')")
    for item in items:
        fa_id = item["faId"]
        funding_id = item["id"]
        rel = conn.get("select * from funding_fa_rel where active='Y' and fundingId=%s and faId=%s",
                       funding_id, fa_id)
        if rel is None:
            try:
                conn.insert('insert funding_fa_rel(fundingId,faId,createTime,modifyTime) values(%s,%s,now(),now())',
                            funding_id, fa_id)
            except:
                pass

    # # company_fa.faId -> company_fa.faInvestorId
    # items = conn.query("select * from company_fa where faId is not null")
    # for item in items:
    #     fa_id = item["faId"]
    #     investor_id = get_investor_id(fa_id)
    #     if investor_id is None:
    #         logger.info("company_fa, faId: %s, Not Found!", fa_id)
    #         exit()
    #     conn.update("update company_fa set faInvestorId=%s where id=%s",
    #                 investor_id, item["id"])
    #
    # # fa_advisor.faId -> fa_advisor.faInvestorId
    # items = conn.query("select * from fa_advisor where faId is not null")
    # for item in items:
    #     fa_id = item["faId"]
    #     investor_id = get_investor_id(fa_id)
    #     if investor_id is None:
    #         logger.info("fa_advisor, faId: %s, Not Found!", fa_id)
    #         exit()
    #     conn.update("update fa_advisor set faInvestorId=%s where id=%s",
    #                 investor_id, item["id"])


if __name__ == '__main__':
    main()