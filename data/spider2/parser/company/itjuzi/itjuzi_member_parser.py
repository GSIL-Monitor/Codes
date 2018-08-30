# -*- coding: utf-8 -*-
import os, sys
from pyquery import PyQuery as pq
import json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, download,util,name_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("itjuzi_member_parser", stream=True)
logger = loghelper.get_logger("itjuzi_member_parser")


SOURCE = 13030  #ITJUZI
TYPE = 36005    #公司成员

download_crawler = download.DownloadCrawler()

def process():
    logger.info("itjuzi_member_parser begin...")
    items = parser_db_util.find_process(SOURCE, TYPE)
    #items = parser_db_util.find_all_limit(SOURCE,TYPE,0,5)
    for item in items:
        logger.info(item["key_int"])
        logger.info(item["url"])
        flag = parser_save_member(item)
        #if r is None:
        #    continue
        #parser_db_util.save_member(r, SOURCE, download_crawler)
        parser_db_util.update_processed(item["_id"])
    logger.info("itjuzi_member_parser end.")


def parser_save_member(item):
    if item is None:
        return None

    member_key = item["key"]

    html = item["content"]
    #logger.info(html)
    d = pq(html)
    name = d('span.name').text().strip()
    logger.info("name: %s" % name)
    if name is None or name == "":
        return None

    company_p ={}
    titles = d('p.titleset> span')
    for t in titles:
        e = pq(t)
        company_key = e('a').attr('href').split("/")[-1]
        temp = e.text()
        position = temp.split("·")[-1].strip()
        company_p[company_key] = position

        logger.info("company key: %s" % company_key)
        logger.info("position: %s" % position)

    weibo = d('div.bottom-links> a').eq(0).attr("href")
    if weibo is not None:
        weibo = weibo.strip()
    logger.info("weibo: %s" %  weibo)

    personurl = d('div.bottom-links> a').eq(1).attr("href")
    if personurl is not None:
        personurl = personurl.strip()
    logger.info("personurl: %s" % personurl)

    sec = d('i.fa-folder-o').parents("div.sec")
    introduction = pq(sec)('div> div.block-v').text().strip()
    if introduction == u"未收录相关信息":
        introduction = ""
    logger.info("introduction: %s" % introduction)

    sec = d('i.fa-briefcase').parents("div.sec")
    work = pq(sec)('div.wp100> ul> li> span> span> a').text().strip()
    if work == u"未收录相关信息":
        work = ""
    logger.info("work: %s" % work)

    sec = d('i.fa-book').parents("div.sec")
    education = pq(sec)('div.wp100> ul> li> span> span.right> a').text().strip()
    if education == u"未收录相关信息":
        education = ""
    logger.info("education: %s" % education)

    sec = d('i.fa-map-marker').parents("p")
    location = pq(sec).text().strip()
    logger.info("location: %s" % location)

    role = d('span.bg-blue').text().strip()
    logger.info("role: %s" % role)

    pictureUrl = d('div.infohead-person> div> div> p> span> img').attr("src").strip()
    if pictureUrl.find("icon-person.png") > 0:
        pictureUrl = None
    logger.info("picture url: %s" % pictureUrl)

    logger.info("")
    for i in company_p:
        company_key = i
        position = company_p[company_key]
        r = member_key, name, weibo, introduction, education, work, location, role, pictureUrl, company_key, position
        logger.info(json.dumps(r, ensure_ascii=False, cls=util.CJsonEncoder))
        parser_db_util.save_member(r, SOURCE, download_crawler)


if __name__ == "__main__":
    process()