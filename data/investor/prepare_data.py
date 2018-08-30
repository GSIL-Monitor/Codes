# -*- coding: utf-8 -*-
import os, sys
import json
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("prepare_data", stream=True)
logger = loghelper.get_logger("prepare_data")


text = """
启明创投	108
IDG资本	109
高榕资本	110
贝塔斯曼亚洲投资基金	111
阿米巴资本	112
红杉	114
蓝驰创投	115
纪源资本	118
清科创投	119
真格基金	122
经纬中国	125
险峰长青	126
软银	131
北极光	132
五岳天下创投	133
金沙江创投	134
苏河汇	136
Star VC	139
光速安振中国创业投资基金	141
凯鹏华盈	142
Ventech China	145
青松基金	148
戈壁	149
红点投资	151
君联资本	154
九合创投	165
钟鼎创投	166
基石资本	167
顺为资本	170
鼎晖创投	171
盛大资本	172
中路资本	174
荷多投资PreAngel	175
Accel	178
CyberAgent Ventures（CA创投）	180
达泰资本	182
DCM资本	189
明势资本	196
高通	197
海纳亚洲	199
策源创投	201
创新工场	202
英诺天使基金	209
华映资本	210
今日资本	211
原子创投	213
湖畔山南	216
信天创投	223
英特尔投资	224
洪泰基金	225
德迅投资	231
联创永宣	234
线性资本	235
赛富投资基金	236
隆领投资	246
天使湾创投	247
同创伟业	251
新进创投	252
力合清源创投	253
昆仲资本	256
紫辉创投	257
光信资本	263
赛伯乐	265
深创投	267
丰厚资本	268
联想之星	278
华创资本	280
毅达资本	282
创智空间	289
安芙兰资本	293
启迪创投	295
启赋资本	300
东方富海	302
盈动投资	310
达晨创投	314
易一天使投资	328
元禾控股	348
浙商创投	358
创新谷投资	359
集富亚洲	363
云天使基金	366
500 Startups	372
心元资本	379
德同资本	387
峰瑞资本	391
银杏谷资本	418
德沃基金	445
源码资本	479
朗玛峰创投	482
蓝湖资本	486
云启资本	493
兰馨亚洲	496
陶石资本	533
天奇阿米巴	614
青云创投	671
谷歌投资	728
零一创投	768
红岭创投	1040
中国风投	2022
晨兴资本	2037
清流资本	2050
德丰杰	2057
东方汇富	2154
梅花天使创投	2164
青山资本	2265
国金纵横投资	2330
创业接力基金	2669
星河互联	2709
硅谷银行	3613
东方赛富	6316
谷歌风投	8079
火山石资本	8315
"""

def main():
    lines = text.splitlines()
    mongo = db.connect_mongo()
    for line in lines:
        logger.info(line)
        ts = line.split()
        if len(ts) != 2:
            continue
        name = ts[0]
        id = ts[1]
        item = mongo.investor.checklist.find_one({"investorId": id})
        if item is None:
            mongo.investor.checklist.insert({"investorName": name, "investorId": id})
    mongo.close()

def add_famours():
    mongo = db.connect_mongo()
    conn = db.connect_torndb()
    inames = conn.query("select ia.id,ia.name from investor ia join famous_investor fi on "
                        "ia.id = fi.investorId")
    num = 0
    for iname in inames:
        # logger.info("%s, %s",iname["id"], iname["name"])
        item = mongo.investor.checklist.find_one({"investorId": {'$in':[int(iname["id"]),str(iname["id"])]}})
        if item is None:
            logger.info("not founded")
            # num += 1
            # logger.info("%s, %s", iname["id"], iname["name"])
        else:
            if item.has_key("kr36InvestorId") is False:
                logger.info("%s, %s", iname["id"], iname["name"])
                logger.info("Missing 36kr")
                num+=1
            else:
                pass
                # logger.info("Having 36Kr: %s", item["kr36InvestorId"])
    logger.info(num)
    mongo.close()
    conn.close()


def add_new(investorId, kr36Id, itjuzisid="None"):
    mongo = db.connect_mongo()
    conn = db.connect_torndb()
    item = mongo.investor.checklist.find_one({"investorId": str(investorId)})
    investor = conn.get("select * from investor where id=%s", investorId)
    kr36s = conn.get("select * from source_investor where source=13022 and sourceId=%s",kr36Id)
    kr36sid = "None"
    if kr36s is None:
        logger.info("not found kr: %s", kr36Id)
        kr36sid = 'None'
        # exit()
    else:
        kr36sid = kr36s["id"]
    if item is None:
        mongo.investor.checklist.insert({"investorName": investor["name"], "investorId": str(investorId)})
    mongo.investor.checklist.update_one({"investorId": str(investorId)},
                                        {"$set": {"kr36InvestorId" : str(kr36Id),
                                                  "itjuziSourceInvestorId" : str(itjuzisid),
                                                  "kr36SourceInvestorId": str(kr36sid),
                                                  "kr36Processed": None,
                                                  "crossChecked": None
                                                  }})
    mongo.close()
    conn.close()


if __name__ == "__main__":
    # main()
    # add_famours()
    # mongo = db.connect_mongo()
    # conn = db.connect_torndb()
    # collection = mongo.investor.checklist
    # clists = list(
    #     collection.find({"crossChecked": True},
    #                     limit=1000))
    # for clist in clists:
    #     if clist.has_key("investorId") is True:
    #         fi = conn.get("select * from famous_investor where investorId=%s",int(clist["investorId"]))
    #         if fi is None:
    #             sql = "insert famous_investor (investorId,createUser,createTime,modifyTime) \
    #                            values(%s,-2,now(),now())"
    #             logger.info("add %s, %s", clist["investorName"], clist["investorId"])
    #             job_id = conn.insert(sql, int(clist["investorId"]))
    # conn.close()
    # mongo.close()
    if len(sys.argv) > 1:
        (a,b,c) = (sys.argv[1],sys.argv[2],sys.argv[3])
        logger.info(sys.argv[0])
        add_new(a,b,c)
    else:
        string = u'''name	id	36kr ID 	itjuzi
哔哩哔哩	3103	11261	None
安持资本	3302	1077	8172
中国人寿	3503	42444	8144
彬复资本	8104	2125	13646
树兰医疗	9312	19577	None
凯辉基金	12279	354	558
曜为资本	13786	46668	None
微软创投	14826	222	None
宣亚国际	15135	None	None
光远资本	15226	1477	None
深圳前海联合创业投资有限公司	15579	18184	None
澜亭投资	10091	15819	None
天风天睿	10147	1112	393
鼎兴量子	10159	1128	13432
一村资本	10217	10217	16345
泽贤投资	10254	39135	None
复之硕资本	10401	2758	None
奥博资本	1179	26078	1191
正和岛	10616	598	720
凯信资本	10786	608	None
拾玉资本	11628	42036	None
源星资本	12152	3254	None
华山资本	12346	153	681
治平资本	12454	2834	7178
联想控股	12535	6304	552
索道资本	12697	2152	None
天马股份	12753	31687	None
知初资本	13137	1029	1814
百福控股	13326	46983	None
时尚资本	13542	47166	None
辰韬资本	13643	3265	None
钧源资本	13832	35037	None
天使百人会基金	14178	None	None
正勤资本	14672	10986	None
百世物流	14687	7823	None
鑫澄投资	14871	28103	None
汇信资本	14905	17566	None
谷银基金	14919	13798	None
斗鱼	14921	None	None
越秀金控	6135	1106	None
力宝集团	14951	7635	13692
文创基金	14955	None	None
浙江吉利控股集团	14964	None	None'''
        for i in string.split('\n')[1:]:
            s = i.split('\t')
            logger.info('runing %s|%s|%s', s[1], s[2], s[3])
            add_new(s[1], s[2], s[3])

