# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson import ObjectId
import re
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_funding_gongshang_detect", stream=True)
logger = loghelper.get_logger("patch_funding_gongshang_detect")


conn = db.connect_torndb()
mongo = db.connect_mongo()


def main():
    items = mongo.company.funding_news.find({"title":"工商变更"})
    for item in items:
        funding_id = item["funding_id"]
        detect_time = item["createTime"]
        gs_time  = item.get("date")
        funding = conn.get("select * from funding where id=%s", funding_id)
        if funding is None:
            continue
        if funding["source"] != 69002:
            logger.info("fundingId: %s, gsTime: %s, detectTime: %s", funding_id, gs_time, detect_time)
            conn.update("update funding set source=69002, gsDetectdate=%s, gsChangeDate=%s where id=%s",
                        detect_time, gs_time, funding_id)


def main2():
    fundings = conn.query("select * from funding where source=69002")
    for funding in fundings:
        funding_id = funding["id"]
        publish_date = funding["publishDate"]
        gs_detect_date = funding["gsDetectdate"]
        news_id = funding["newsId"]
        logger.info("fundingId: %s, publish date: %s, gs detect date: %s, newsId: %s", funding_id, publish_date, gs_detect_date, news_id)

        if news_id is not None:
            news = mongo.article.news.find_one({"_id": ObjectId(news_id)})
            if news is None:
                logger.info("remove newsId")
                conn.update("update funding set newsId=null where id=%s", funding_id)
                #exit()
            else:
                logger.info("newsId exists")

        if publish_date is None or gs_detect_date is None:
            continue
        if publish_date < gs_detect_date:
            conn.update("update funding set publishDate=null where id=%s", funding_id)


def main3():
    str = """
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 78227, publish date: 2017-05-08 08:00:00, gs detect date: 2017-06-22 20:05:08
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 78621, publish date: 2016-08-31 08:00:00, gs detect date: 2017-07-06 18:28:07
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 79598, publish date: 2014-09-17 08:00:00, gs detect date: 2017-03-18 18:58:12
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 79603, publish date: 2014-04-25 08:00:00, gs detect date: 2017-07-14 09:34:07
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 79604, publish date: 2013-05-09 08:00:00, gs detect date: 2017-07-14 01:33:12
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 79605, publish date: 2015-06-16 08:00:00, gs detect date: 2017-07-14 01:41:39
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 79851, publish date: 2016-10-22 08:00:00, gs detect date: 2017-03-04 20:48:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 80481, publish date: 2015-08-20 08:00:00, gs detect date: 2017-07-25 08:30:44
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 80482, publish date: 2014-07-28 08:00:00, gs detect date: 2017-07-25 08:32:51
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 81765, publish date: 2014-08-25 08:00:00, gs detect date: 2017-03-13 22:49:49
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 83178, publish date: 2014-09-22 08:00:00, gs detect date: 2017-03-19 12:56:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 87177, publish date: 2016-03-03 08:00:00, gs detect date: 2017-07-14 10:05:55
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 87178, publish date: 2015-12-02 08:00:00, gs detect date: 2017-07-14 10:03:59
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 87984, publish date: 2016-05-12 08:00:00, gs detect date: 2017-08-14 15:42:20
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 88388, publish date: 2015-08-04 08:00:00, gs detect date: 2016-12-15 11:59:55
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 88985, publish date: 2016-05-05 08:00:00, gs detect date: 2017-07-20 10:27:24
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 89307, publish date: 2016-03-29 08:00:00, gs detect date: 2017-07-28 18:59:24
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 90217, publish date: 2016-01-14 08:00:00, gs detect date: 2017-03-12 22:11:45
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 90606, publish date: 2016-02-25 08:00:00, gs detect date: 2017-07-21 10:10:55
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 91247, publish date: 2014-08-27 08:00:00, gs detect date: 2017-02-15 19:00:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 92520, publish date: 2016-04-21 19:57:34, gs detect date: 2017-05-23 18:59:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 92521, publish date: 2016-04-21 19:57:34, gs detect date: 2017-05-24 02:57:10
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 93072, publish date: 2015-07-29 00:00:00, gs detect date: 2017-03-07 02:17:54
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 93422, publish date: 2016-02-26 08:00:00, gs detect date: 2017-05-26 17:22:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 93526, publish date: 2017-03-14 08:00:00, gs detect date: 2017-05-27 18:13:20
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 94254, publish date: 2016-03-07 08:00:00, gs detect date: 2017-08-15 13:49:48
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 94597, publish date: 2015-09-02 08:00:00, gs detect date: 2017-07-27 13:37:04
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 95459, publish date: 2017-04-26 08:00:00, gs detect date: 2017-06-24 18:38:39
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 95856, publish date: 2015-07-07 08:00:00, gs detect date: 2017-06-24 11:39:32
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 97348, publish date: 2016-03-15 02:02:25, gs detect date: 2017-03-11 23:57:38
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 97986, publish date: 2016-03-30 08:00:00, gs detect date: 2017-03-15 11:22:19
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 100238, publish date: 2016-09-23 08:00:00, gs detect date: 2016-12-30 23:40:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101239, publish date: 2015-08-31 08:00:00, gs detect date: 2017-02-17 01:51:53
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101915, publish date: 2017-03-10 00:00:00, gs detect date: 2017-03-10 14:50:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101917, publish date: 2016-04-06 08:00:00, gs detect date: 2017-03-11 07:06:06
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101931, publish date: 2017-03-11 00:00:00, gs detect date: 2017-03-11 06:32:35
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101932, publish date: 2017-03-11 00:00:00, gs detect date: 2017-03-11 06:38:20
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101937, publish date: 2017-03-11 00:00:00, gs detect date: 2017-03-11 07:44:47
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101938, publish date: 2017-03-11 00:00:00, gs detect date: 2017-03-11 07:45:50
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101939, publish date: 2017-03-11 00:00:00, gs detect date: 2017-03-11 07:46:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101940, publish date: 2017-03-11 00:00:00, gs detect date: 2017-03-11 07:47:27
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101941, publish date: 2017-03-11 00:00:00, gs detect date: 2017-03-11 07:49:21
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 101951, publish date: 2017-03-11 00:00:00, gs detect date: 2017-03-11 10:12:59
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102014, publish date: 2017-03-12 00:00:00, gs detect date: 2017-03-12 06:27:45
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102015, publish date: 2017-03-12 00:00:00, gs detect date: 2017-03-12 06:29:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102019, publish date: 2017-03-12 00:00:00, gs detect date: 2017-03-12 06:54:34
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102026, publish date: 2017-03-12 00:00:00, gs detect date: 2017-03-12 07:42:06
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102037, publish date: 2015-04-13 08:00:00, gs detect date: 2017-03-13 01:00:20
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102044, publish date: 2017-03-12 00:00:00, gs detect date: 2017-03-12 09:32:04
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102045, publish date: 2017-03-12 00:00:00, gs detect date: 2017-03-12 09:34:33
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102077, publish date: 2017-03-12 00:00:00, gs detect date: 2017-03-12 12:12:46
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102098, publish date: 2016-03-29 08:00:00, gs detect date: 2017-03-13 05:24:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102099, publish date: 2014-08-12 08:00:00, gs detect date: 2017-03-13 05:25:51
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102154, publish date: 2017-03-13 00:00:00, gs detect date: 2017-03-13 09:04:22
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102180, publish date: 2017-03-13 00:00:00, gs detect date: 2017-03-13 12:36:34
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102181, publish date: 2015-02-02 00:00:00, gs detect date: 2017-03-13 12:37:43
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102197, publish date: 2017-03-14 00:00:00, gs detect date: 2017-03-14 00:59:30
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102198, publish date: 2017-03-14 00:00:00, gs detect date: 2017-03-14 01:00:48
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102217, publish date: 2017-03-14 00:00:00, gs detect date: 2017-03-14 02:42:50
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102228, publish date: 2017-03-14 00:00:00, gs detect date: 2017-03-14 03:46:38
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102289, publish date: 2017-03-14 00:00:00, gs detect date: 2017-03-14 13:29:11
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102290, publish date: 2017-03-14 00:00:00, gs detect date: 2017-03-14 14:07:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102344, publish date: 2017-03-15 00:00:00, gs detect date: 2017-03-15 06:52:03
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102346, publish date: 2017-03-15 00:00:00, gs detect date: 2017-03-15 06:57:29
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102360, publish date: 2017-03-15 00:00:00, gs detect date: 2017-03-15 08:21:44
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102380, publish date: 2017-03-15 00:00:00, gs detect date: 2017-03-15 10:05:26
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102421, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 03:53:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102422, publish date: 2016-08-03 08:00:00, gs detect date: 2017-03-16 12:17:53
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102424, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 05:23:32
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102426, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 05:37:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102453, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 08:53:45
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102456, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 09:09:46
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102458, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 09:16:37
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102459, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 10:28:24
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102529, publish date: 2017-03-18 00:00:00, gs detect date: 2017-03-18 02:52:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102533, publish date: 2017-03-18 00:00:00, gs detect date: 2017-03-18 04:22:50
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102534, publish date: 2017-03-18 00:00:00, gs detect date: 2017-03-18 05:37:30
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102535, publish date: 2017-03-18 00:00:00, gs detect date: 2017-03-18 06:03:07
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102537, publish date: 2017-03-18 00:00:00, gs detect date: 2017-03-18 07:58:23
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102538, publish date: 2017-03-18 00:00:00, gs detect date: 2017-03-18 07:58:23
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102546, publish date: 2017-03-18 00:00:00, gs detect date: 2017-03-18 08:21:58
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102568, publish date: 2017-03-18 00:00:00, gs detect date: 2017-03-18 12:20:21
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102613, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 04:46:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102635, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 09:03:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102636, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 09:04:13
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102660, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 11:21:38
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102663, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 11:27:58
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102669, publish date: 2016-10-18 08:00:00, gs detect date: 2017-03-19 19:46:29
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102682, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 12:43:46
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102710, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 14:34:06
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102712, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 14:35:34
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102713, publish date: 2017-03-19 00:00:00, gs detect date: 2017-03-19 14:39:34
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102850, publish date: 2017-03-22 00:00:00, gs detect date: 2017-03-22 07:40:33
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102888, publish date: 2017-03-23 00:00:00, gs detect date: 2017-03-23 03:51:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102892, publish date: 2017-03-23 00:00:00, gs detect date: 2017-03-23 06:10:48
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102893, publish date: 2017-03-23 00:00:00, gs detect date: 2017-03-23 06:13:30
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102898, publish date: 2017-03-23 00:00:00, gs detect date: 2017-03-23 07:18:43
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102903, publish date: 2017-03-23 00:00:00, gs detect date: 2017-03-23 07:49:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102909, publish date: 2014-06-06 08:00:00, gs detect date: 2017-03-23 16:35:34
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102973, publish date: 2017-03-25 00:00:00, gs detect date: 2017-03-25 15:48:28
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102974, publish date: 2017-03-25 00:00:00, gs detect date: 2017-03-25 15:49:22
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102993, publish date: 2017-03-26 00:00:00, gs detect date: 2017-03-26 01:50:49
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 102996, publish date: 2017-03-26 00:00:00, gs detect date: 2017-03-26 02:05:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103034, publish date: 2017-03-27 00:00:00, gs detect date: 2017-03-27 02:56:24
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103046, publish date: 2017-03-28 00:00:00, gs detect date: 2017-03-28 06:32:31
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103062, publish date: 2017-03-28 00:00:00, gs detect date: 2017-03-28 10:30:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103063, publish date: 2017-03-28 00:00:00, gs detect date: 2017-03-28 10:33:08
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103064, publish date: 2017-03-28 00:00:00, gs detect date: 2017-03-28 10:33:10
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103065, publish date: 2017-03-28 00:00:00, gs detect date: 2017-03-28 10:33:46
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103066, publish date: 2017-03-28 00:00:00, gs detect date: 2017-03-28 10:35:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103151, publish date: 2017-03-31 00:00:00, gs detect date: 2017-03-31 02:35:59
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103169, publish date: 2017-04-01 00:00:00, gs detect date: 2017-04-01 02:07:29
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 103411, publish date: 2017-04-07 00:00:00, gs detect date: 2017-04-07 11:02:16
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 104021, publish date: 2017-01-17 08:00:00, gs detect date: 2017-05-01 04:25:33
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 104043, publish date: 2016-02-25 08:00:00, gs detect date: 2017-05-02 17:26:30
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 104103, publish date: 2015-05-25 08:00:00, gs detect date: 2017-05-03 16:32:33
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 104447, publish date: 2015-01-31 08:00:00, gs detect date: 2017-05-13 22:42:16
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 104791, publish date: 2016-08-10 08:00:00, gs detect date: 2017-05-20 00:35:35
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 104793, publish date: 2015-10-28 08:00:00, gs detect date: 2017-05-19 16:47:17
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 104954, publish date: 2016-08-31 08:00:00, gs detect date: 2017-05-24 06:34:43
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 104959, publish date: 2016-07-04 08:00:00, gs detect date: 2017-05-23 23:13:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 105149, publish date: 2014-12-12 08:00:00, gs detect date: 2017-05-25 20:06:51
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 105155, publish date: 2016-07-21 08:00:00, gs detect date: 2017-05-25 20:18:30
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 105164, publish date: 2015-09-30 08:00:00, gs detect date: 2017-05-26 04:23:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 105229, publish date: 2015-12-29 08:00:00, gs detect date: 2017-05-26 22:21:44
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 105249, publish date: 2016-06-28 08:00:00, gs detect date: 2017-05-27 09:00:06
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 105358, publish date: 2016-11-30 08:00:00, gs detect date: 2017-05-27 18:05:01
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 105410, publish date: 2015-04-23 08:00:00, gs detect date: 2017-05-31 14:12:49
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 105412, publish date: 2015-09-09 08:00:00, gs detect date: 2017-05-31 22:13:51
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 106497, publish date: 2016-05-04 08:00:00, gs detect date: 2017-06-26 14:47:27
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 107192, publish date: 2017-04-19 08:00:00, gs detect date: 2017-07-06 18:29:16
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 107623, publish date: 2017-01-19 08:00:00, gs detect date: 2017-07-14 10:43:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 107907, publish date: 2017-06-21 08:00:00, gs detect date: 2017-07-18 20:28:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 107908, publish date: 2015-08-07 08:00:00, gs detect date: 2017-07-18 20:37:19
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 108241, publish date: 2017-05-24 08:00:00, gs detect date: 2017-07-21 18:34:37
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 108358, publish date: 2015-05-26 08:00:00, gs detect date: 2017-03-09 13:57:17
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 108678, publish date: 2015-01-31 08:00:00, gs detect date: 2017-05-14 06:42:16
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 108679, publish date: 2016-08-31 08:00:00, gs detect date: 2017-05-25 14:34:43
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 108680, publish date: 2015-01-31 08:00:00, gs detect date: 2017-05-13 22:42:16
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 108681, publish date: 2016-08-31 08:00:00, gs detect date: 2017-05-24 06:34:43
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 108828, publish date: 2017-01-23 08:00:00, gs detect date: 2017-08-27 00:49:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 109236, publish date: 2016-08-16 08:00:00, gs detect date: 2017-08-01 02:23:43
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 109465, publish date: 2014-06-18 08:00:00, gs detect date: 2017-08-02 17:36:01
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 109503, publish date: 2016-11-11 12:51:37, gs detect date: 2017-08-03 18:00:31
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 109619, publish date: 2017-06-06 08:00:00, gs detect date: 2017-08-04 11:16:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 109820, publish date: 2016-05-16 08:18:48, gs detect date: 2017-08-08 14:55:39
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 109908, publish date: 2016-08-11 08:00:00, gs detect date: 2017-08-09 23:39:10
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 109973, publish date: 2015-04-22 08:00:00, gs detect date: 2017-08-10 14:20:25
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110011, publish date: 2017-04-20 08:00:00, gs detect date: 2017-08-10 17:41:57
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110073, publish date: 2015-07-31 08:00:00, gs detect date: 2017-08-12 01:06:41
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110124, publish date: 2017-07-18 08:00:00, gs detect date: 2017-08-15 02:57:12
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110138, publish date: 2015-04-21 08:00:00, gs detect date: 2017-08-14 14:18:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110154, publish date: 2017-02-15 08:00:00, gs detect date: 2017-08-15 00:16:31
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110156, publish date: 2017-05-16 08:00:00, gs detect date: 2017-08-15 00:27:04
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110165, publish date: 2014-01-03 08:00:00, gs detect date: 2017-08-14 17:46:59
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110202, publish date: 2017-01-09 08:00:00, gs detect date: 2017-08-15 10:53:08
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110232, publish date: 2015-03-26 08:00:00, gs detect date: 2017-08-15 13:18:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110246, publish date: 2017-05-03 08:00:00, gs detect date: 2017-08-15 22:59:50
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110265, publish date: 2017-04-17 08:00:00, gs detect date: 2017-08-16 01:46:59
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110267, publish date: 2015-06-29 08:00:00, gs detect date: 2017-08-15 17:59:06
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110299, publish date: 2017-05-08 08:00:00, gs detect date: 2017-08-16 14:11:04
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110302, publish date: 2016-01-26 08:00:00, gs detect date: 2017-08-16 10:02:51
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110303, publish date: 2017-07-17 08:00:00, gs detect date: 2017-08-16 10:10:51
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110308, publish date: 2017-01-18 08:00:00, gs detect date: 2017-08-16 18:55:31
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110315, publish date: 2017-01-13 08:00:00, gs detect date: 2017-08-16 12:27:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110353, publish date: 2016-11-01 08:00:00, gs detect date: 2017-08-16 16:16:11
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110355, publish date: 2017-07-07 08:00:00, gs detect date: 2017-08-16 16:28:50
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110359, publish date: 2017-02-24 08:00:00, gs detect date: 2017-08-17 00:49:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110377, publish date: 2017-05-04 08:00:00, gs detect date: 2017-08-16 17:33:48
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110410, publish date: 2017-02-22 08:00:00, gs detect date: 2017-08-16 18:36:11
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110411, publish date: 2017-02-15 08:00:00, gs detect date: 2017-08-17 02:40:50
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110432, publish date: 2016-01-27 08:00:00, gs detect date: 2017-08-16 20:02:27
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110433, publish date: 2017-01-09 08:00:00, gs detect date: 2017-08-16 20:44:46
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110434, publish date: 2017-04-05 08:00:00, gs detect date: 2017-08-16 20:54:25
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110437, publish date: 2017-03-07 08:00:00, gs detect date: 2017-08-17 09:26:30
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110444, publish date: 2017-06-28 08:00:00, gs detect date: 2017-08-17 18:25:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110457, publish date: 2017-01-23 08:00:00, gs detect date: 2017-08-17 11:19:33
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110458, publish date: 2016-07-27 08:00:00, gs detect date: 2017-08-17 11:23:28
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110461, publish date: 2017-03-02 08:00:00, gs detect date: 2017-08-17 11:27:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110463, publish date: 2017-06-05 08:00:00, gs detect date: 2017-08-17 11:46:42
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110464, publish date: 2015-09-22 08:00:00, gs detect date: 2017-08-17 11:53:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110465, publish date: 2017-01-03 08:00:00, gs detect date: 2017-08-17 11:54:19
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110468, publish date: 2017-07-11 08:00:00, gs detect date: 2017-08-17 12:50:54
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110471, publish date: 2017-06-02 08:00:00, gs detect date: 2017-08-17 21:13:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110484, publish date: 2017-07-26 08:00:00, gs detect date: 2017-09-06 09:57:54
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110489, publish date: 2017-07-25 08:00:00, gs detect date: 2017-08-17 14:23:32
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110494, publish date: 2017-04-18 08:00:00, gs detect date: 2017-08-17 14:40:33
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110514, publish date: 2017-01-16 08:00:00, gs detect date: 2017-08-18 07:58:59
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110555, publish date: 2017-06-26 08:00:00, gs detect date: 2017-08-18 02:01:04
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110560, publish date: 2017-04-19 08:00:00, gs detect date: 2017-08-18 10:22:28
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110563, publish date: 2017-01-23 08:00:00, gs detect date: 2017-08-18 10:31:12
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110568, publish date: 2017-05-09 08:00:00, gs detect date: 2017-08-18 02:43:51
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110573, publish date: 2017-03-03 08:00:00, gs detect date: 2017-08-18 02:49:13
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110577, publish date: 2017-06-22 08:00:00, gs detect date: 2017-08-18 09:59:37
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110587, publish date: 2017-06-20 08:00:00, gs detect date: 2017-08-18 10:15:12
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110591, publish date: 2016-02-25 08:00:00, gs detect date: 2017-08-18 10:31:44
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110592, publish date: 2017-04-20 08:00:00, gs detect date: 2017-08-19 02:38:08
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110597, publish date: 2017-02-23 08:00:00, gs detect date: 2017-08-18 18:51:34
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110604, publish date: 2017-01-17 08:00:00, gs detect date: 2017-08-18 12:00:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110605, publish date: 2017-06-20 08:00:00, gs detect date: 2017-08-18 20:08:37
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110608, publish date: 2017-06-29 08:00:00, gs detect date: 2017-08-18 13:25:35
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110614, publish date: 2017-03-08 08:00:00, gs detect date: 2017-08-18 13:59:26
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110617, publish date: 2017-04-22 08:00:00, gs detect date: 2017-08-18 14:06:07
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110619, publish date: 2017-07-07 08:00:00, gs detect date: 2017-08-19 08:00:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110622, publish date: 2017-07-20 08:00:00, gs detect date: 2017-08-18 22:33:25
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110627, publish date: 2017-01-20 08:00:00, gs detect date: 2017-08-18 15:19:58
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110631, publish date: 2017-06-06 08:00:00, gs detect date: 2017-08-18 15:52:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110643, publish date: 2016-11-22 08:00:00, gs detect date: 2017-08-18 17:07:29
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110645, publish date: 2015-01-21 08:00:00, gs detect date: 2017-08-18 17:16:56
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110646, publish date: 2017-05-26 08:00:00, gs detect date: 2017-08-19 01:19:17
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110650, publish date: 2017-01-20 08:00:00, gs detect date: 2017-08-18 17:45:46
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110652, publish date: 2017-06-19 08:00:00, gs detect date: 2017-08-18 17:54:39
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110653, publish date: 2015-04-09 08:00:00, gs detect date: 2017-08-18 17:57:34
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110654, publish date: 2017-07-05 08:00:00, gs detect date: 2017-08-18 17:58:31
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110656, publish date: 2017-03-09 08:00:00, gs detect date: 2017-08-19 10:09:48
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110657, publish date: 2015-08-21 08:00:00, gs detect date: 2017-08-18 18:10:35
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110658, publish date: 2017-04-25 08:00:00, gs detect date: 2017-08-18 18:11:43
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110659, publish date: 2017-04-12 08:00:00, gs detect date: 2017-08-18 18:20:20
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110660, publish date: 2017-06-15 08:00:00, gs detect date: 2017-08-19 02:30:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110662, publish date: 2017-02-07 08:00:00, gs detect date: 2017-08-19 02:43:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110663, publish date: 2017-04-12 08:00:00, gs detect date: 2017-08-18 18:43:19
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110665, publish date: 2017-03-21 08:00:00, gs detect date: 2017-08-19 02:46:07
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110671, publish date: 2017-06-06 08:00:00, gs detect date: 2017-08-18 21:08:47
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110695, publish date: 2017-02-17 08:00:00, gs detect date: 2017-08-19 15:10:07
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110706, publish date: 2017-02-28 08:00:00, gs detect date: 2017-08-20 07:35:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110709, publish date: 2017-06-07 08:00:00, gs detect date: 2017-08-19 23:38:29
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110726, publish date: 2017-04-06 08:00:00, gs detect date: 2017-08-19 16:43:48
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110728, publish date: 2017-07-20 08:00:00, gs detect date: 2017-08-20 00:53:42
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110732, publish date: 2017-02-07 08:00:00, gs detect date: 2017-08-20 09:05:20
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110733, publish date: 2017-05-10 08:00:00, gs detect date: 2017-08-20 01:07:04
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110734, publish date: 2017-02-10 08:00:00, gs detect date: 2017-08-20 09:12:21
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110735, publish date: 2017-07-25 08:00:00, gs detect date: 2017-08-20 01:16:08
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110743, publish date: 2017-03-16 08:00:00, gs detect date: 2017-08-19 18:14:55
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110745, publish date: 2017-07-18 08:00:00, gs detect date: 2017-08-19 18:21:57
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110766, publish date: 2017-06-12 08:00:00, gs detect date: 2017-08-21 10:44:38
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110773, publish date: 2017-01-22 08:00:00, gs detect date: 2017-08-21 11:39:10
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110774, publish date: 2017-02-07 08:00:00, gs detect date: 2017-08-21 13:26:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110775, publish date: 2017-06-23 08:00:00, gs detect date: 2017-08-21 14:14:45
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110776, publish date: 2017-07-13 08:00:00, gs detect date: 2017-08-21 14:23:41
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110790, publish date: 2017-01-05 08:00:00, gs detect date: 2017-08-21 16:57:59
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110804, publish date: 2017-04-24 08:00:00, gs detect date: 2017-08-21 18:11:08
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110828, publish date: 2017-02-13 08:00:00, gs detect date: 2017-08-22 10:13:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110834, publish date: 2016-09-01 08:00:00, gs detect date: 2017-08-23 03:19:07
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110835, publish date: 2017-01-22 08:00:00, gs detect date: 2017-08-23 11:27:31
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110841, publish date: 2017-06-13 08:00:00, gs detect date: 2017-08-22 14:27:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110844, publish date: 2017-07-07 08:00:00, gs detect date: 2017-08-22 23:18:28
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110889, publish date: 2016-09-29 08:00:00, gs detect date: 2017-08-23 17:21:25
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110892, publish date: 2017-03-21 08:00:00, gs detect date: 2017-08-23 09:39:16
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110893, publish date: 2015-01-09 08:00:00, gs detect date: 2017-08-23 10:07:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110898, publish date: 2016-11-09 08:00:00, gs detect date: 2017-08-23 10:54:16
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110907, publish date: 2017-02-15 08:00:00, gs detect date: 2017-08-23 13:57:01
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 110910, publish date: 2017-01-22 08:00:00, gs detect date: 2017-08-23 14:10:23
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111024, publish date: 2016-11-24 08:00:00, gs detect date: 2017-08-25 17:57:21
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111090, publish date: 2017-01-12 08:00:00, gs detect date: 2017-08-25 17:01:42
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111091, publish date: 2017-06-30 08:00:00, gs detect date: 2017-08-25 17:02:17
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111198, publish date: 2016-10-27 08:00:00, gs detect date: 2017-08-29 14:34:33
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111240, publish date: 2017-02-16 08:00:00, gs detect date: 2017-08-30 19:43:15
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111241, publish date: 2017-03-16 08:00:00, gs detect date: 2017-08-31 04:34:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111242, publish date: 2017-04-21 08:00:00, gs detect date: 2017-08-30 20:50:42
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111243, publish date: 2017-06-12 08:00:00, gs detect date: 2017-08-31 04:53:26
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111246, publish date: 2017-03-06 08:00:00, gs detect date: 2017-08-30 14:04:55
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111248, publish date: 2017-01-09 08:00:00, gs detect date: 2017-08-30 14:16:04
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111250, publish date: 2017-03-30 08:00:00, gs detect date: 2017-08-30 14:30:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111251, publish date: 2017-05-15 08:00:00, gs detect date: 2017-08-30 22:33:19
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111256, publish date: 2017-06-16 08:00:00, gs detect date: 2017-08-30 15:09:24
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111257, publish date: 2017-04-13 08:00:00, gs detect date: 2017-08-30 15:15:31
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111259, publish date: 2017-06-28 08:00:00, gs detect date: 2017-08-30 23:22:31
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111260, publish date: 2017-04-13 08:00:00, gs detect date: 2017-08-30 15:25:26
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111261, publish date: 2017-05-03 08:00:00, gs detect date: 2017-08-30 15:32:01
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111262, publish date: 2017-04-17 08:00:00, gs detect date: 2017-08-30 15:33:23
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111268, publish date: 2017-07-14 08:00:00, gs detect date: 2017-08-30 15:48:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111269, publish date: 2017-08-08 08:00:00, gs detect date: 2017-08-30 15:50:14
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111290, publish date: 2017-03-24 08:00:00, gs detect date: 2017-08-30 19:36:58
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111311, publish date: 2017-04-12 08:00:00, gs detect date: 2017-08-31 11:17:55
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111371, publish date: 2017-03-16 08:00:00, gs detect date: 2017-09-01 18:56:40
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111372, publish date: 2016-08-19 08:00:00, gs detect date: 2017-09-01 18:59:08
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111376, publish date: 2017-01-13 08:00:00, gs detect date: 2017-09-01 11:26:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111378, publish date: 2017-07-26 08:00:00, gs detect date: 2017-09-01 11:32:23
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111379, publish date: 2017-08-14 08:00:00, gs detect date: 2017-09-01 11:36:50
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111380, publish date: 2017-02-28 08:00:00, gs detect date: 2017-09-01 11:46:25
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111386, publish date: 2017-02-13 08:00:00, gs detect date: 2017-09-01 12:44:52
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111389, publish date: 2017-04-14 08:00:00, gs detect date: 2017-09-01 12:58:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111390, publish date: 2017-02-20 08:00:00, gs detect date: 2017-09-01 13:01:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111408, publish date: 2017-06-22 08:00:00, gs detect date: 2017-09-01 23:52:59
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111421, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 03:53:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111424, publish date: 2017-03-16 00:00:00, gs detect date: 2017-03-16 03:53:05
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111448, publish date: 2017-01-24 08:00:00, gs detect date: 2017-09-02 11:34:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111454, publish date: 2017-03-17 08:00:00, gs detect date: 2017-09-03 06:21:15
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111466, publish date: 2017-08-23 08:00:00, gs detect date: 2017-09-19 15:13:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111492, publish date: 2017-01-19 08:00:00, gs detect date: 2017-09-04 11:23:10
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111494, publish date: 2017-01-06 08:00:00, gs detect date: 2017-09-04 11:31:23
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111497, publish date: 2017-02-20 08:00:00, gs detect date: 2017-09-04 12:56:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111502, publish date: 2016-12-29 08:00:00, gs detect date: 2017-09-05 05:39:37
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111504, publish date: 2017-06-06 08:00:00, gs detect date: 2017-09-04 13:50:37
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111509, publish date: 2017-03-30 08:00:00, gs detect date: 2017-09-04 15:14:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111510, publish date: 2017-05-26 08:00:00, gs detect date: 2017-09-04 15:16:26
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111525, publish date: 2017-06-15 08:00:00, gs detect date: 2017-09-04 18:21:00
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111570, publish date: 2017-02-24 08:00:00, gs detect date: 2017-09-06 10:15:54
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111579, publish date: 2017-04-13 08:00:00, gs detect date: 2017-09-06 13:48:21
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111624, publish date: 2017-03-22 08:00:00, gs detect date: 2017-09-06 17:57:29
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111646, publish date: 2017-03-20 08:00:00, gs detect date: 2017-09-07 11:04:17
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111649, publish date: 2017-08-16 08:00:00, gs detect date: 2017-09-07 11:22:53
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111650, publish date: 2017-04-24 08:00:00, gs detect date: 2017-09-07 11:31:54
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111663, publish date: 2017-06-06 08:00:00, gs detect date: 2017-09-07 14:45:32
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111698, publish date: 2016-05-17 08:00:00, gs detect date: 2017-09-08 10:22:52
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111722, publish date: 2017-02-16 08:00:00, gs detect date: 2017-09-08 22:25:03
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 111732, publish date: 2017-03-06 08:00:00, gs detect date: 2017-09-08 15:42:03
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112084, publish date: 2017-01-16 08:00:00, gs detect date: 2017-09-16 23:45:35
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112148, publish date: 2017-03-16 08:00:00, gs detect date: 2017-08-31 12:34:18
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112200, publish date: 2017-07-18 08:00:00, gs detect date: 2017-09-19 23:14:10
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112203, publish date: 2017-05-22 08:00:00, gs detect date: 2017-09-19 23:14:50
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112292, publish date: 2017-01-06 08:00:00, gs detect date: 2017-09-21 01:46:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112294, publish date: 2016-10-22 08:00:00, gs detect date: 2017-03-04 20:48:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112295, publish date: 2017-01-06 08:00:00, gs detect date: 2017-09-21 01:46:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112298, publish date: 2017-07-14 08:00:00, gs detect date: 2017-09-21 10:32:36
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112301, publish date: 2017-01-16 08:00:00, gs detect date: 2017-09-20 19:01:58
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112302, publish date: 2017-01-16 08:00:00, gs detect date: 2017-09-20 19:02:22
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112310, publish date: 2017-05-23 08:00:00, gs detect date: 2017-09-21 09:56:11
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112311, publish date: 2017-06-20 08:00:00, gs detect date: 2017-09-21 10:10:09
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112326, publish date: 2017-03-07 08:00:00, gs detect date: 2017-09-21 11:49:49
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 112359, publish date: 2017-01-22 08:00:00, gs detect date: 2017-09-21 23:42:27
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 113763, publish date: 2014-06-06 08:00:00, gs detect date: 2017-03-23 16:35:34
patch_funding_gongshang_detect Fri, 27 Oct 2017 18:29:54 INFO     fundingId: 113765, publish date: 2014-06-06 08:00:00, gs detect date: 2017-03-23 16:35:34
    """

    lines = str.splitlines()
    for line in lines:
        if not line.startswith("patch_funding_gongshang_detect"):
            continue
        #logger.info(line)
        reg = re.compile(r'fundingId: (.*?), publish date: (.*?),')
        m = reg.search(line)
        fundingId = int(m.group(1))
        datestr = m.group(2)
        logger.info("fundingId: %s, date: %s", fundingId, datestr)
        conn.update("update funding set publishDate=%s where id=%s", datestr, fundingId)

if __name__ == "__main__":
    main2()