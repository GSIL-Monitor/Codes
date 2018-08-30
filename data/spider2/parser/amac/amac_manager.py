# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import util, name_helper, url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util2'))
import parser_mongo_util

#logger
loghelper.init_logger("amac_manager_parser", stream=True)
logger = loghelper.get_logger("amac_manager_parser")

SOURCE = 13630  #amac manager
TYPE = 36001    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)


def process():
    logger.info("amac manager parser begin...")

    start = 0
    while True:
        items = parser_mongo_util.find_process_limit(SOURCE, TYPE, start, 1000)
        # items = [parser_mongo_util.find_process_one(SOURCE,TYPE,1705031504105341)]
        for item in items:
            # logger.info(item)
            r = parse_company(item)
            # for n in r:
            #     logger.info("%s   ->    %s", n, r[n])
            if r["status"] == "Fail":
                exit()
            else:
                parser_mongo_util.save_mongo_amac_manager(r["source"], r["sourceId"], r)
                parser_mongo_util.update_processed(item["_id"])
                logger.info("processed %s" ,item["url"])
                # else:
                #     logger.info("lack something:  %s", item["url"])

        #     break
        # break
        if len(items) == 0:
            break

    logger.info("amac manager parser end.")


def parse_company(item):
    logger.info("parse_company")
    company_key = item["key"]
    record = {}
    d = pq(html.fromstring(item["content"].decode("utf-8")))

    (managerName, managerEnglishName, organizationCode, regDate, establishDate, lastUdpateDate, managerType,
     website, domain, managerLegalPerson, executives, fundsBeforeReg, fundsAfterReg, managerLegalPerson_workingHistory,
     regCode, regAddress, officeAddress, regCapitalRMB, realCapitalRMB, companyType, capitalProportion,
     otherBusType, headCount, legalOpinionState, lawOrganization, lawyer, managerLegalPerson_qualification,
     managerLegalPerson_qualificationType) = \
        (None, None, None, None, None, None, None, None, None, None, [],[],[],[], None, None, None, None, None, None
         , None, None, None, None, None, None, None, None)

    for td in d('td.td-title'):
        tdpq = pq(td)
        # if tdpq.text() is not None and tdpq.text().strip() == "律师姓名:":
        #     td_next = tdpq.next('td.td-content')
        #     logger.info("%s", td_next.text())
        if tdpq.text() is not None and tdpq.text().strip() == "基金管理人全称(中文):":
            td_next = tdpq.next('td.td-content> div#complaint2')
            managerName = td_next.eq(0).text().replace("&nbsp", "").strip()
            logger.info("Manager Name %s", managerName)
        elif tdpq.text() is not None and tdpq.text().strip() == "基金管理人全称(英文):":
            td_next = tdpq.next('td.td-content')
            managerEnglishName = td_next.text().strip()
            logger.info("Manager English Name %s", managerEnglishName)
        elif tdpq.text() is not None and tdpq.text().strip() == "组织机构代码:":
            td_next = tdpq.next('td.td-content')
            organizationCode = td_next.text().strip()
            logger.info("organizationCode %s", organizationCode)
        elif tdpq.text() is not None and tdpq.text().strip() == "登记编号:":
            td_next = tdpq.next('td.td-content')
            regCode = td_next.text().strip()
            logger.info("regCode %s", regCode)
        elif tdpq.text() is not None and tdpq.text().strip() == "注册地址:":
            td_next = tdpq.next('td.td-content')
            regAddress = td_next.text().strip()
            logger.info("regAddress %s", regAddress)
        elif tdpq.text() is not None and tdpq.text().strip() == "办公地址:":
            td_next = tdpq.next('td.td-content')
            officeAddress = td_next.text().strip()
            logger.info("officeAddress %s", officeAddress)
        elif tdpq.text() is not None and tdpq.text().strip() == "注册资本(万元)(人民币):":
            td_next = tdpq.next('td.td-content')
            regCapitalRMB = td_next.text().strip()
            logger.info("regCapitalRMB %s", regCapitalRMB)
        elif tdpq.text() is not None and tdpq.text().strip() == "实缴资本(万元)(人民币):":
            td_next = tdpq.next('td.td-content')
            realCapitalRMB = td_next.text().strip()
            logger.info("realCapitalRMB %s", realCapitalRMB)
        elif tdpq.text() is not None and tdpq.text().strip() == "企业性质:":
            td_next = tdpq.next('td.td-content')
            companyType = td_next.text().strip()
            logger.info("companyType %s", companyType)
        elif tdpq.text() is not None and tdpq.text().strip() == "注册资本实缴比例:":
            td_next = tdpq.next('td.td-content')
            capitalProportion = td_next.text().strip()
            logger.info("capitalProportion %s", capitalProportion)
        elif tdpq.text() is not None and tdpq.text().strip() == "申请的其他业务类型:":
            td_next = tdpq.next('td.td-content')
            otherBusType = td_next.text().strip()
            logger.info("otherBusType %s", otherBusType)
        elif tdpq.text() is not None and tdpq.text().strip() == "员工人数:":
            td_next = tdpq.next('td.td-content')
            headCount = td_next.text().strip()
            logger.info("headCount %s", headCount)

        elif tdpq.text() is not None and tdpq.text().strip() == "法律意见书状态:":
            td_next = tdpq.next('td.td-content')
            legalOpinionState = td_next.text().strip()
            logger.info("legalOpinionState %s", legalOpinionState)

        elif tdpq.text() is not None and tdpq.text().strip() == "律师事务所名称:":
            td_next = tdpq.next('td.td-content')
            lawOrganization = td_next.text().strip()
            logger.info("lawOrganization %s", lawOrganization)

        elif tdpq.text() is not None and tdpq.text().strip() == "律师姓名:":
            td_next = tdpq.next('td.td-content')
            lawyer = td_next.text().strip()
            logger.info("lawyer %s", lawyer)

        elif tdpq.text() is not None and tdpq.text().strip() == "登记时间:":
            td_next = tdpq.next('td.td-content')
            regDate = td_next.text().strip()
            logger.info("regDate %s", regDate)
        elif tdpq.text() is not None and tdpq.text().strip() == "成立时间:":
            td_next = tdpq.next('td.td-content')
            establishDate = td_next.text().strip()
            logger.info("establishDate %s", establishDate)
        elif tdpq.text() is not None and tdpq.text().strip() == "机构信息最后更新时间:":
            td_next = tdpq.next('td.td-content')
            lastUdpateDate = td_next.text().strip()
            logger.info("lastUdpateDate %s", lastUdpateDate)
        elif tdpq.text() is not None and tdpq.text().strip() == "管理基金主要类别:":
            td_next = tdpq.next('td.td-content')
            managerType = td_next.text().strip()
            logger.info("managerType %s", managerType)
        elif tdpq.text() is not None and tdpq.text().strip() == "机构网址:":
            td_next = tdpq.next('td.td-content')
            try:
                website = td_next.text().strip()
                if website == "": website = None
                flag, domain = url_helper.get_domain(website)
                logger.info("website %s|%s", website, domain)
            except:
                pass
        elif tdpq.text() is not None and tdpq.text().strip() == "法定代表人/执行事务合伙人(委派代表)姓名:":
            td_next = tdpq.next('td.td-content')
            managerLegalPerson = td_next.text().strip()
            logger.info("managerLegalPerson %s", managerLegalPerson)

        elif tdpq.text() is not None and tdpq.text().strip() == "是否有从业资格:":
            td_next = tdpq.next('td.td-content')
            managerLegalPerson_qualification = td_next.text().strip()
            logger.info("managerLegalPerson_qualified %s", managerLegalPerson_qualification)

        elif tdpq.text() is not None and tdpq.text().strip() == "资格取得方式:":
            td_next = tdpq.next('td.td-content')
            managerLegalPerson_qualificationType = td_next.text().strip()
            logger.info("managerLegalPerson_qualificationType %s", managerLegalPerson_qualificationType)

        elif tdpq.text() is not None and tdpq.text().strip() == "法定代表人/执行事务合伙人(委派代表)工作履历:":
            td_nexts = tdpq.next('td.td-content> table.table-center> tbody> tr')
            for tdn in td_nexts:
                timeline = ("").join(pq(tdn)('td').eq(0).text().strip().split())
                organization = pq(tdn)('td').eq(1).text().strip()
                title = pq(tdn)('td').eq(2).text().strip()
                managerLegalPerson_workingHistory.append({"timeline": timeline, "organization": organization, "title": title})
                logger.info("workinghis %s|%s|%s", timeline, organization, title)

        elif tdpq.text() is not None and tdpq.text().strip() == "高管情况:":
            td_nexts = tdpq.next('td.td-content> table.table-center> tbody> tr')
            for tdn in td_nexts:
                name = pq(tdn)('td').eq(0).text().strip()
                position = pq(tdn)('td').eq(1).text().strip()
                qualification = pq(tdn)('td').eq(2).text().strip()
                executives.append({"name": name, "postion": position, "qualification": qualification})
                logger.info("executives %s|%s|%s", name, position, qualification)
        elif tdpq.text() is not None and tdpq.text().strip() == "暂行办法实施前成立的基金:":
            td_nexts = tdpq.next('td.td-content> p> a')
            fundsBeforeReg = []
            for tdn in td_nexts:
                fundName = pq(tdn).text().strip()
                fundUrl = pq(tdn).attr("href").replace("..", "http://gs.amac.org.cn/amac-infodisc/res/pof")
                fundsBeforeReg.append({"fundName": fundName, "fundUrl": fundUrl})
                logger.info("fundsBeforeReg %s|%s", fundName, fundUrl)
        elif tdpq.text() is not None and tdpq.text().strip() == "暂行办法实施后成立的基金:":
            td_nexts = tdpq.next('td.td-content> p> a')
            fundsAfterReg = []
            for tdn in td_nexts:
                fundName = pq(tdn).text().strip()
                fundUrl = pq(tdn).attr("href").replace("..", "http://gs.amac.org.cn/amac-infodisc/res/pof")
                fundsAfterReg.append({"fundName": fundName, "fundUrl": fundUrl})
                logger.info("fundsAfterReg %s|%s", fundName, fundUrl)

    if managerName is None or managerName == "":
        return {"status": "Fail"}
    else:
        record = {
            "status": "Success",
            "managerName": managerName.replace("(", "（").replace(")", "）"),
            "managerEnglishName": managerEnglishName if managerEnglishName !="" else None,
            "organizationCode": organizationCode if organizationCode != "" else None,
            "regDate": regDate if regDate != "" else None,
            "establishDate": establishDate if establishDate !="" else None,
            "lastUpdateDate": lastUdpateDate if lastUdpateDate != "" else None,
            "managerType": managerType if managerType != "" else None,
            "website": website,
            "domain": domain,
            "managerLegalPerson": managerLegalPerson if managerLegalPerson != "" else None,
            "executives": executives,
            "managerLegalPerson_workingHistory": managerLegalPerson_workingHistory,
            "fundsBeforeReg": fundsBeforeReg,
            "fundsAfterReg": fundsAfterReg,
            "source": 13630,
            "sourceId": company_key,
            "sourceUrl": item["url"],
            "regCode": regCode if regCode != "" else None,
            "regAddress": regAddress if regAddress != "" else None,
            "officeAddress": officeAddress if officeAddress != "" else None,
            "regCapitalRMB": regCapitalRMB if regCapitalRMB != "" else None,
            "realCapitalRMB": realCapitalRMB if realCapitalRMB != "" else None,
            "companyType": companyType if companyType != "" else None,
            "capitalProportion": capitalProportion if capitalProportion != "" else None,
            "otherBusType": otherBusType if otherBusType != "" else None,
            "headCount": headCount if headCount != "" else None,
            "legalOpinionState": legalOpinionState if legalOpinionState != "" else None,
            "lawOrganization": lawOrganization if lawOrganization != "" else None,
            "lawyer": lawyer if lawyer != "" else None,
            "managerLegalPerson_qualification": managerLegalPerson_qualification if managerLegalPerson_qualification != "" else None,
            "managerLegalPerson_qualificationType": managerLegalPerson_qualificationType if managerLegalPerson_qualificationType != "" else None,

        }
        return record
if __name__ == "__main__":
    while True:
        process()
        #break   #test
        time.sleep(30*60)