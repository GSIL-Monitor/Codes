# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("import_investor_tag", stream=True)
logger = loghelper.get_logger("import_investor_tag")

str_investors = """
170创业营
500 Startups
Accel Partners
Accenture
Access Venture Partners
Accion Frontier Inclusion Fund
Accion’s Frontier Investments Group
Ah! Ventures
Aleph Venture Capital
Amasia
AME Cloud Ventures
American Express
Amino Capital
Amplify.LA
Andreessen Horowitz
AngelList
Anthemis Group
Anthony Di Iorio
Arbor Ventures
ARTIS Ventures
Aspect Ventures
AXA Strategic Ventures
Badwater Capital
Balderton Capital
Barclays
Battery Ventures
Beenext
Benchmark Capital
Bitcoin Faith
BitFury Capital
Block VC
Blockchain Capital
Blockchain Ventures
Blockchange Ventures
BlueChilli
BlueYard Capital
Blume Ventures
Bnk to the Future
Boldstart
BOLDstart Ventures
Boost VC
Bpifrance
Breyer Capital
Bridgescale Partners
Bullpen Capital
Capital One
Capstone Partners
Carthona Capital
Cervin Ventures
Chain Capital
Citigroup
CME Ventures
Cogint, Inc.
Colbeck Capital Management
Collaborative Fund
Collinstar Capital
Comcast Ventures
Commerce Ventures
Correlation Ventures
Crosscut Ventures
Crosslink Capital
Data Collective
David Lee
DCG
DCM
DFJ德丰杰
DFUND基金
Digital Currency Group
Digital Garage
Draper Associates
Draper Esprit
Drummond Road Capital
DSC Investment
du
Earlybird Venture Capital
East Ventures
EMC媒体基金
FBTC
ff Venture Capital
Fifth Wall Ventures
First Round Capital
FirstMark Capital
Flare Capital Partners
Fortress Investment Group
Foundation Capital
Founders Fund
F-Prime Capital Partners
FundersClub
GaiaX Global Marketing Ventures
General Catalyst Partners
Global Brain Corporation
Goodwater Capital
Google
Google Ventures
Granite Ventures
Greycroft Partners
Greylock Partners
Haystack Partners
Hogege
Horizon Ventures
IBM
IBT资本
Iconiq Capital
Ideaspace Foundation
IDG资本
Index Ventures
Infinity Venture Partners
ING（荷兰国际集团）
Initialized Capital
Innovation Endeavors
Jefferson
JeHan Chu
JPMorgan摩根大通
JRR Capital
Jungle Ventures
Khosla Ventures
Kickstart Seed Fund
Kima Ventures
Lakestar
Lerer Hippeau Ventures
Liberty City Ventures
Lightspeed Venture Partners美国光速
Lux Capital
Martin Ventures
Mesh Ventures
MIH Holdings Limited
Mirae Asset Venture Investment
Money Partners Group
Mosaic Ventures
Mumbai Angels
Naspers
NEA恩颐投资
NEO Global Capital
Oak Investment Partners
OEX International
OMERS Ventures
Pantera Capital
Partech Ventures
Pelion Venture Partners
Playfair Capital
Plug & Play Ventures
PNC Financial Services Group
Point Nine Capital
PreAngel
QueensBridge Venture Partners
Radar Partners
Rakishev
Real Ventures
Rebright Partners
Recruit Strategic Partners
RGAx
Ribbit Capital
Right Side Capital Management
Rising Tide Fund
Robert Bosch Venture Capital GmbH
RRE Ventures
RTP Ventures
Sam Altman
Santander InnoVentures
SBI集团
SEB Venture Capital
Seed Capital
Seedcamp
Shell Technology Ventures
Siemens Venture Capital
Sierra Ventures
SIG海纳亚洲
Singulariteam
Skandinaviska Enskilda Banken
Social Starts
SOS Ventures
Sozo Ventures
Spark
Spark Capital
SparkLabs Global Ventures
Sparkland Capital
Spotify
Storm Ventures
Streamlined Ventures
String Ventures
Strong Ventures
SV Angel
Tangle Capital
Tappan Hill Ventures
Techstars Ventures (前Bullet Time Ventures)
TEEC Angel Fund
Tekton Ventures
Tenfore Holdings
Thrive capital
TNB CAPITAL
Tokyo Founders Fund
TriplePoint Capital
True Ventures
Tusk Ventures
Union Square Ventures
Upfront Ventures
Valor Equity Partners
Variv Capital
Venture Labo Investment
Venturra Capital
Verizon Ventures
Version One Ventures
Visa
VY Capital
Wamda Capital
Wavemaker Labs
Wavemaker Partners
Wicklow Capital
Wing Venture Partners
Winklevoss Capital
XAnge Private Equity
阿尔法公社
阿里巴巴
安赐资本
安芙兰创投
澳大利亚国民银行
澳银资本
百度
帮实资本
趵朴投资
比特大陆
蝙蝠资本
伯藜创投
博将资本
蔡文胜
策源创投
陈伟星
晨兴资本
筹帷资本
创大InnoHub
创世资本
创势资本
创新工场
创新谷Innovalley
创业工场
达晨创投
大河创投
戴姆勒公司
丹华资本
丹来资产
德鼎创新基金
德丰杰龙脉基金
点亮资本
鼎峰资本
多维资本
恩厚资本
泛城资产
泛娱链
方创资本
芳晟投资
分布式资本
峰瑞资本
复励投资
复星集团
复星锐正资本
复星同浩
傅盛
富士康
高达资本
高榕资本
高盛集团
高通风险投资
高原资本
高樟资本
戈壁创投
公信宝基金
古莲资本
光大控股
光速中国
光照资本
广和投资
广州外服
硅谷银行
国灏创投
海通开元
和盟创投
恒生电子
弘桥资本
红点中国
红杉中国
洪泰基金
胡皓
花旗风投
花旗集团
华创资本
汇丰银行HSBC
汇通富达
汇银集团
火币网
伙伴创投
机遇空间
基石资本
极豆资本
极客帮创投
纪源资本GGV
节点资本
界石投资
金艮资本
金科君创
金桥创投
金色财经
金沙江创投
锦江国际
经纬中国
景林投资
九鼎数字资产
九鼎投资
九合创投
玖富
巨人网络
凯辉基金
凯辉私募股权投资基金
凯鹏华盈
快的打车
昆仲资本
蓝驰创投
老鹰基金
乐搏资本
了得资本
李火星
李笑来比特基金
连接资本
联发科MTK
联合创投
联想创投集团
联想之星
量子策略基金
量子链
量子资本
猎鹰创投
临潮资产
刘俊
龙庆投资
隆领投资
蛮子基金
曼图资本Mandra Capital
梅花天使创投
美国中经合集团
明势资本
墨柏资本
宁夏瑞宁前锋
盘古创富
普华资本
七海资本
奇虎360
启迪新创投
启赋资本
起源资本
千方基金
千合资本
前海汇潮
前海梧桐并购基金
钱世投资
青山资本
清华企业家协会天使基金
清华同方
区块宝
曲速创投
人人网
日本乐天Rakuten
容铭资本
三菱东京日联银行
三星
厦门巴根创投
山行资本
深创投
沈波
盛大资本
时戳资本
首都金融服务商会
水滴资本
松禾创新
韬蕴资本
陶石资本
腾讯产业共赢基金
天奇创投
天使百人会基金
天使湾
田范江
同道大叔
头狼金服
投资网
暾澜投资
万向分布资本
万向集团
万向区块链
王伟林
王啸
网易资本
旺家投资
微软
唯嘉资本
唯猎资本
维港投资
维京资本
无引力ICO基金
先知资本
险峰长青
现在支付
香港尚亚交易所
橡树投资集团
心元资本
信天创投
信雅达
信中利资本
星辰资本
星合资本
星链资本
星耀资本
邢帅网络学院
许飞
薛蛮子
亚东投资
亚杰商会天使基金
羊羊得亿投资
宜信
亦庄互联基金
易一天使
英诺天使基金
英特尔投资
硬币资本
用友幸福投资
优领资本
元生资本
源政投资
粤科资本
云锋基金
云脑基金
泽清资本
长江国弘投资
长远控股
招商局资本
招银国际
浙大网新
浙江君宝通信科技有限公司
浙江清华长三角研究院
浙江中南建设控股公司
真格基金
执一资本
中国风投
中国华立集团
中金甲子
中骏基金
中科乐创
中科招商
中新力合
逐鹿资本
追梦者基金
追远创投
紫辉创投
纵横天下投资
FBG
凯辉基金
邢帅教育
金桥资本
"""

conn = db.connect_torndb()

BLOCKCHAIN_TAGID = 175747

def main():
    investor_names = str_investors.split("\n")
    for name in investor_names:
        name = name.strip()
        if name == "":
            continue
        # logger.info(name)
        investors = conn.query("select * from investor where (active is null or active='Y') and name=%s", name)
        if len(investors) != 1:
            logger.info("%s, cnt: %s", name, len(investors))
            continue
        investor = investors[0]
        investor_id = investor["id"]
        rel = conn.get("select * from investor_tag_rel where (active is null or active='Y') and investorId=%s and tagId=%s",
                       investor_id, BLOCKCHAIN_TAGID)
        if rel is None:
            conn.insert("insert investor_tag_rel(investorId, tagId, verify, active, createTime,modifyTime) "
                        "values(%s,%s,'Y','Y',now(),now())",
                        investor_id, BLOCKCHAIN_TAGID)


if __name__ == '__main__':
    main()