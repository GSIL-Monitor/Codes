# -*- coding: utf-8 -*-
import os, sys, re, json, time
import datetime
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import amac_util
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config, util, url_helper
import db


#logger
loghelper.init_logger("amac_findy", stream=True)
logger = loghelper.get_logger("amac_findy")

# investor_alias amacType amacId
# investor_alias_candidate amacType amacId

#
# 拉萨合业投资管理有限公司
# 北京聚信远业投资咨询有限公司
# 北京云瀚锦科技中心（有限合伙）
# 天津红杉资本投资管理中心
# 北京红杉嘉禾资产管理中心（有限合伙）
# 北京红杉盛远管理咨询有限公司
# 红杉资本投资管理（天津）有限公司
# 北京锋业股权投资中心（有限合伙）
# 上海桓远投资管理有限公司
# 北京创想天地投资管理有限公司
# 宁波梅山保税港区真致成远股权投资中心（有限合伙）
# 北京真格天投股权投资中心
# 杭州经天纬地投资合伙企业（有限合伙）
# 新疆高达经纬股权投资合伙企业（有限合伙）
# 上海登布苏投资中心（有限合伙）
# 上海经帛投资管理合伙企业（有限合伙）
# 北京创客绿洲投资管理有限公司
# 杭州德翼投资管理有限公司
# 杭州德赢创业投资合伙企业（有限合伙）
# 上海德粤群益投资中心（有限合伙）
# 德同轨道交通投资有限公司
# 广州德同凯得创业投资有限合伙企业
# 成都德同银科创业投资合伙企业
# 成都锦程同德股权投资基金合伙企业
# 上海微兴投资中心（有限合伙）
# 广州德同凯德创业投资有限合伙企业（有限合伙）
# 上海黄杉投资合伙企业（有限合伙）
# 晨兴资本三期香港有限公司
# 西藏鹰合信投资合伙企业（有限合伙）
# 西藏尚思投资合伙企业（有限合伙）
# 上海晨山投资管理有限公司
# 上海晨畔创业投资中心（有限合伙）
# 深圳市君盛金石投资企业
# 深圳君盛鼎石创业投资企业（有限合伙）
# 深圳市君盛金石投资企业（有限合伙）
#

names = [
    '拉萨合业投资管理有限公司',
    '北京聚信远业投资咨询有限公司',
    '北京云瀚锦科技中心（有限合伙）',
    '天津红杉资本投资管理中心',
    '北京红杉嘉禾资产管理中心（有限合伙）',
    '北京红杉盛远管理咨询有限公司',
    '红杉资本投资管理（天津）有限公司',
    '北京锋业股权投资中心（有限合伙）',
    '上海桓远投资管理有限公司',
    '北京创想天地投资管理有限公司',
    '宁波梅山保税港区真致成远股权投资中心（有限合伙）',
    '北京真格天投股权投资中心',
    '杭州经天纬地投资合伙企业（有限合伙）',
    '新疆高达经纬股权投资合伙企业（有限合伙）',
    '上海登布苏投资中心（有限合伙）',
    '上海经帛投资管理合伙企业（有限合伙）',
    '北京创客绿洲投资管理有限公司',
    '杭州德翼投资管理有限公司',
    '杭州德赢创业投资合伙企业（有限合伙）',
    '上海德粤群益投资中心（有限合伙）',
    '德同轨道交通投资有限公司',
    '广州德同凯得创业投资有限合伙企业',
    '成都德同银科创业投资合伙企业',
    '成都锦程同德股权投资基金合伙企业',
    '上海微兴投资中心（有限合伙）',
    '广州德同凯德创业投资有限合伙企业（有限合伙）',
    '上海黄杉投资合伙企业（有限合伙）',
    '晨兴资本三期香港有限公司',
    '西藏鹰合信投资合伙企业（有限合伙）',
    '西藏尚思投资合伙企业（有限合伙）',
    '上海晨山投资管理有限公司',
    '上海晨畔创业投资中心（有限合伙）',
    '深圳市君盛金石投资企业',
    '深圳君盛鼎石创业投资企业（有限合伙）',
    '深圳市君盛金石投资企业（有限合伙）',
]
if __name__ == "__main__":
    num=0
    for name in names:
        if amac_util.find_amac_fund(name) is not None or \
           amac_util.find_amac_manager(name) is not None:
            logger.info("eeeeeee: %s", name)
        else:
            num+=1
    logger.info(num)
    # conn = db.connect_torndb()
    # investors = conn.query("select * from famous_investor where active is null or active='Y'")
    # for investor in investors:
    #     amac_util.find_investor_alias_by_fund(investor["investorId"])
    #     amac_util.find_investor_alias_by_manager(investor["investorId"])
    #
    #     amac_util.find_investor_alias(investor["investorId"])
    # amac_util.find_investor_alias_by_fund(114)
