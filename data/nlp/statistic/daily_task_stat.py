# -*- encoding=utf-8 -*-
__author__ = "kailu"

import os
import sys
import shutil
import datetime
import codecs
from bson import ObjectId

import pandas as pd
import numpy as np


reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))


import db as dbcon

db = dbcon.connect_torndb()
mongo = dbcon.connect_mongo()


from itertools import chain

import loghelper
loghelper.init_logger("daily_task_stat", stream=True)
logger = loghelper.get_logger("daily_task_stat")


def turn_date_to_datetime(d):
    """
    :param d: datetime.date 时间日期
    :return: datetime.datetime 给定日期零点对应时间
    """
    t = datetime.datetime(d.year, d.month, d.day)
    return t


def modify_df_columns(df, new_columns):
    for col in new_columns:
        if col not in df.columns:
            df[col] = np.nan
    return df[new_columns]


def zip_gb_size(pandas_group_by_object):
    s = pandas_group_by_object.size()
    return zip(s.index.tolist(), s.values.tolist())


def get_user_name_helper(obj, uid):
    uid = int(uid)

    if uid not in obj.userId_name_dict:
        r = db.get("select * from user where id=%s", uid)
        if r:
            obj.userId_name_dict[uid] = r["username"]
        else:
            obj.userId_name_dict[uid] = None

    return obj.userId_name_dict[uid]


def clean_collection_daily_statistics_method_helper(obj, coll, fields, filter_condition=None):
    if filter_condition is None:
        filter_condition = dict()
        filter_condition["date_yyyymmdd"] = obj.yyyymmdd
    filter_condition.setdefault("date_yyyymmdd", obj.yyyymmdd)
    unset_condition = {field: "" for field in fields}
    set_condition = dict()
    set_condition["lastUpdateTime"] = datetime.datetime.utcnow()

    ur = coll.update_many(filter_condition, {"$unset": unset_condition, "$set": set_condition})
    logger.info("{} fields {} filter by {} "
                "in collection {} have been upset, "
                "{} docs modified out of {} docs total.".format(obj.yyyymmdd, fields, filter_condition,
                                                                coll.name, ur.modified_count,
                                                                ur.matched_count))


def delete_collection_daily_records_method_helper(obj, coll):
    dr = coll.delete_many({"date_yyyymmdd": obj.yyyymmdd})
    logger.info("{} collection {} records have been removed, {} in total".format(obj.yyyymmdd, coll.name, dr.deleted_count))


class Stat_News_Task(object):

    def __init__(self, curr_day=datetime.date.today(), days=1):
        self.curr_day = curr_day
        self.days = days
        self.next_day = self.curr_day + datetime.timedelta(days=self.days)

        self.yyyymmdd = str(curr_day).replace("-", "")

        self.news_type_dict = {"check": u"一般新闻", "fund": u"融资新闻", "report": u"行业报告", "important": u"重要新闻",
                               "review": u'重看新闻'}
        self.userId_name_dict = {}

        self.relate_collections = [mongo.stat.validate_news, mongo.stat.summary_task, mongo.stat.summary_user]

        self.df_new_news_task = self._daily_new_news_task_df()
        self.df_modified_news_task = self._daily_modified_news_task_df()

    def _get_user_name(self, uid):
        return get_user_name_helper(self, uid)

    def _get_news_type_name(self, x):
        return self.news_type_dict.get(x)

    def _daily_new_news_task_df(self):
        t0 = datetime.datetime(self.curr_day.year,
                               self.curr_day.month,
                               self.curr_day.day) - datetime.timedelta(hours=8)

        t1 = datetime.datetime(self.next_day.year,
                               self.next_day.month,
                               self.next_day.day) - datetime.timedelta(hours=8)

        condition = {"createTime": {"$gt": t0, "$lt": t1}}
        cr = mongo.task.news.find(condition)

        df = pd.DataFrame(list(cr))

        columns = ["_id", "modifyUser", "processStatus", "type", "companyIds"]
        for col in columns:
            if col not in df.columns:
                df[col] = np.nan

        df_n = df[columns]
        return df_n

    def _daily_modified_news_task_df(self):
        t0 = datetime.datetime(self.curr_day.year,
                               self.curr_day.month,
                               self.curr_day.day) - datetime.timedelta(hours=8)

        t1 = datetime.datetime(self.next_day.year,
                               self.next_day.month,
                               self.next_day.day) - datetime.timedelta(hours=8)

        condition = {"modifyTime": {"$gt": t0, "$lt": t1}}
        cr = mongo.task.news.find(condition)

        df = pd.DataFrame(list(cr))

        columns = ["_id", "processStatus", "modifyUser", "type", "companyIds"]
        for col in columns:
            if col not in df.columns:
                df[col] = np.nan

        df = df[df["processStatus"].isin([1,-1])]

        df_n = df[columns]
        return df_n

    def insert_new_news_task_stat(self):
        df_new_news_task = self.df_new_news_task

        # news task by type
        coll_news = mongo.stat.validate_news

        reset_statistic_field_list = ["newAmount", "newAmountByProcessStatus"]
        self._clean_collection_daily_statistics(coll_news, reset_statistic_field_list)

        gb_type = df_new_news_task.groupby("type")
        type_amount_list = zip_gb_size(gb_type)

        for TYPE, amount in type_amount_list:
            gb_type_status= df_new_news_task[df_new_news_task["type"]==TYPE].groupby("processStatus")
            amount_by_status = {str(k): int(v) for k, v in zip_gb_size(gb_type_status)}

            filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                                "newsType": TYPE}

            update_fields = dict()
            update_fields["lastUpdateTime"] = datetime.datetime.utcnow()
            update_fields["newsTypeName"] = self._get_news_type_name(TYPE)
            update_fields["newAmount"] = amount
            # update_fields["newAmountByProcessStatus"] = amount_by_status

            ur = coll_news.update_one(filter_condition, {"$set": update_fields}, upsert=True)
            logger.info("{} {} new news task {}, "
                        "{} by news task processStatus.".format(self.yyyymmdd, TYPE, amount, amount_by_status))

        # summary total new news task
        total_new_news_task = len(df_new_news_task)

        gb_status = df_new_news_task.groupby("processStatus")
        amount_by_status = {str(k): v for k, v in zip_gb_size(gb_status)}

        filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                            "type": "summary"}

        update_fields = dict()
        update_fields["lastUpdateTime"] = datetime.datetime.utcnow()
        update_fields["newAmount"] = total_new_news_task
        # update_fields["newAmountByProcessStatus"] = amount_by_status

        ur = coll_news.update_one(filter_condition, {"$set": update_fields}, upsert=True)
        logger.info("{} new news task {} in total, "
                    "{} by news task processStatus.".format(self.yyyymmdd, total_new_news_task, amount_by_status))

    def insert_modified_news_task_stat(self):
        df_modified_news_task = self.df_modified_news_task

        # summary by user
        coll_user = mongo.stat.summary_user

        reset_statistic_field_list = ["totalNewsTaskAmount", "fundNewsTaskAmount", "importantNewsTaskAmount"
                                      "nonFundNewsTaskAmount", "reportTaskAmount", "reviewTaskAmount"]
        self._clean_collection_daily_statistics(coll_user, reset_statistic_field_list)

        gb_user = df_modified_news_task.groupby("modifyUser")
        userId_amount_list = zip_gb_size(gb_user)
        user_stat_dict = {"check": "nonFundNewsTaskAmount",
                          "fund": "fundNewsTaskAmount",
                          "important": "importantNewsTaskAmount",
                          "report": "reportTaskAmount",
                          "review": "reviewTaskAmount"}

        for userId, amount in userId_amount_list:
            userName = self._get_user_name(userId)

            gb_user_type = df_modified_news_task[df_modified_news_task["modifyUser"]==userId].groupby("type")
            type_amount_list = zip_gb_size(gb_user_type)

            filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                                "userId": userId}

            set_condition = dict()
            set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
            set_condition["totalNewsTaskAmount"] = amount
            set_condition["userName"] = userName

            for TYPE, type_amount in type_amount_list:
                set_condition[user_stat_dict[TYPE]] = type_amount

            ur = coll_user.update_one(filter_condition, {"$set": set_condition}, upsert=True)
            logger.info("{} userId:{} userName:{} modified news task {} in total, "
                        "{} by news type.".format(self.yyyymmdd, userId, userName, amount, type_amount_list))

        # summary by type
        coll_news = mongo.stat.validate_news

        reset_statistic_field_list = ["modifiedAmount"]
        self._clean_collection_daily_statistics(coll_news, reset_statistic_field_list)

        gb_type = df_modified_news_task.groupby("type")
        type_amount_list = zip_gb_size(gb_type)

        for TYPE, amount in type_amount_list:
            filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                                "newsType": TYPE}

            set_condition = dict()
            set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
            set_condition["newsTypeName"] = self._get_news_type_name(TYPE)
            set_condition["modifiedAmount"] = amount

            ur = coll_news.update_one(filter_condition, {"$set": set_condition}, upsert=True)
            logger.info("{} {} modified news task {}.".format(self.yyyymmdd, TYPE, amount))

        # summary total modified news task
        total_modified_news_task = len(df_modified_news_task)

        filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                            "type": "summary"}

        set_condition = dict()
        set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
        set_condition["modifiedAmount"] = total_modified_news_task

        ur = coll_news.update_one(filter_condition, {"$set": set_condition}, upsert=True)
        logger.info("{} moidified news task {} in total.".format(self.yyyymmdd, total_modified_news_task))

    def _clean_collection_daily_statistics(self, coll, fields):
        clean_collection_daily_statistics_method_helper(self, coll, fields)

    def _delete_collection_daily_records(self, coll):
        delete_collection_daily_records_method_helper(self, coll)


class Stat_New_Company_Task(object):

    def __init__(self, curr_day=datetime.date.today(), days=1):
        self.curr_day = curr_day
        self.days = days
        self.next_day = self.curr_day + datetime.timedelta(days=self.days)

        self.yyyymmdd = str(curr_day).replace("-", "")

        self.relate_collections = [mongo.stat.validate_new_company, mongo.stat.summary_task]

        self.crawler_source_dict = {13001: u"用户创建",
                                    13022: u"36氪创投助手",
                                    13030: u"IT桔子",
                                    13050: u"拉勾网",
                                    13838: u"天天投"}

        self.raw_df = self._daily_new_company_df()

    def _daily_new_company_df(self):
        r = db.query("SELECT c.*, sc.source FROM company c, source_company sc "
                     "WHERE c.id=sc.companyid "
                     "AND c.createtime>%s And c.createtime<%s "
                     "AND sc.createtime>%s And sc.createtime<%s"
                     ";",
                     self.curr_day, self.next_day,
                     self.curr_day, self.next_day)

        if r:
            df = pd.DataFrame(r)
            df_n = df[["id","active","source","modifyUser"]]
            return df_n
        else:
            return None

    def _daily_new_company_finished_df(self):
        r = db.query("SELECT c.*, sc.source FROM company c, source_company sc "
                     "WHERE c.id=sc.companyid "
                     "AND c.createtime>%s And c.createtime<%s "
                     "AND sc.createtime>%s And sc.createtime<%s"
                     ";",
                     self.curr_day, self.next_day,
                     self.curr_day, self.next_day)

        if r:
            df = pd.DataFrame(r)
            df_n = df[["id","active","source","modifyUser"]]
            return df_n
        else:
            return None

    def insert_new_company_stat(self):
        if self.raw_df is None:
            return

        coll_company = mongo.stat.validate_new_company

        reset_statistic_field_list = ["newAmount", "modifiedAmount", "publishedAmount"]
        self._clean_collection_daily_statistics(coll_company, reset_statistic_field_list)

        # summary all
        total_amount = len(self.raw_df['id'].unique())
        # summary published
        modified_total_amount = len(self.raw_df[~self.raw_df['active'].isnull()]['id'].unique())
        published_total_amount = len(self.raw_df[self.raw_df['active']=='Y']['id'].unique())

        filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                            "type": "summary"}

        set_condition = dict()
        set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
        set_condition["newAmount"] = total_amount
        set_condition["modifiedAmount"] = modified_total_amount
        set_condition["publishedAmount"] = published_total_amount

        ur = coll_company.update_one(filter_condition, {"$set": set_condition}, upsert=True)
        logger.info("{} new company {} in total.".format(self.yyyymmdd, total_amount))
        logger.info("{} modified new company {} in total.".format(self.yyyymmdd, modified_total_amount))
        logger.info("{} published new company {} in total.".format(self.yyyymmdd, published_total_amount))

        # all new company by source
        gb_source =self.raw_df.groupby("source")
        sourceId_amount_list = zip_gb_size(gb_source)

        for source_id, amount in sourceId_amount_list:
            source_id = int(source_id)
            source_name = self.crawler_source_dict.get(source_id)

            if source_name is None:
                source_id = 0

            filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                                "sourceId": source_id}

            set_condition = dict()
            set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
            set_condition["sourceName"] = source_name
            set_condition["newAmount"] = amount

            ur = coll_company.update_one(filter_condition, {"$set": set_condition}, upsert=True)
            logger.info("{} {}: {} new company {}.".format(self.yyyymmdd, source_id, source_name, amount))

        # modified new company by source
        active_df = self.raw_df[~self.raw_df['active'].isnull()]

        gb_source = active_df.groupby("source")
        sourceId_amount_list = zip_gb_size(gb_source)

        for source_id, amount in sourceId_amount_list:
            source_id = int(source_id)
            source_name = self.crawler_source_dict.get(source_id)

            if source_name is None:
                source_id = 0

            filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                                "sourceId": source_id}

            set_condition = dict()
            set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
            set_condition["sourceName"] = source_name
            set_condition["modifiedAmount"] = amount

            ur = coll_company.update_one(filter_condition, {"$set": set_condition}, upsert=True)
            logger.info("{} {}: {} modified new company {}.".format(self.yyyymmdd, source_id, source_name, amount))

        # published new company by source
        active_df = self.raw_df[self.raw_df["active"]=="Y"]

        gb_source = active_df.groupby("source")
        sourceId_amount_list = zip_gb_size(gb_source)

        for source_id, amount in sourceId_amount_list:
            source_id = int(source_id)
            source_name = self.crawler_source_dict.get(source_id)

            if source_name is None:
                source_id = 0

            filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                                "sourceId": source_id}

            set_condition = dict()
            set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
            set_condition["sourceName"] = source_name
            set_condition["publishedAmount"] = amount

            ur = coll_company.update_one(filter_condition, {"$set": set_condition}, upsert=True)
            logger.info("{} {}: {} published new company {}.".format(self.yyyymmdd, source_id, source_name, amount))

    def _clean_collection_daily_statistics(self, coll, fields):
        clean_collection_daily_statistics_method_helper(self, coll, fields)

    def _delete_collection_daily_records(self, coll):
        delete_collection_daily_records_method_helper(self, coll)


class Stat_Company_Maintainence(object):

    def __init__(self, curr_day=datetime.date.today(), days=1):

        self.curr_date = datetime.datetime.now()
        self.curr_day = curr_day
        self.days = days
        self.next_day = self.curr_day + datetime.timedelta(days=self.days)

        self.yyyymmdd = str(curr_day).replace("-", "")

        self.relate_collections = [mongo.stat.validate_maintain_company, mongo.stat.summary_task]

        self.stat_collection = mongo.stat.validate_maintain_company
        self.summary_stat_collection = mongo.stat.summary_task

        self.df_processed_article_news = self._daily_processed_article_news_df()
        self.df_new_company_ids = self._daily_new_company_ids_df()

        self.userId_name_dict = dict()
        self.user_stat_collection = mongo.stat.summary_user
        self.df_company_task = self._daily_company_task_df()

        self.maintain_type_list = ["nonFundNews", "fundNews", "fa",
                                   "topicMessage", "companyMessage",
                                   "xiniuVisit",
                                   # "xiniuVisitWeb", "xiniuVisitApp",
                                   "openapiVisit",
                                   "newCrawler", "newCreated",
                                   "portfolio", "gongshang", "split"]

        self.maintain_type_log_message_dict = {"nonFundNews": u"non fund news task",
                                               "fundNews": u"fund news task",
                                               "fa": u"fa maintainence",
                                               "topicMessage": u"topic message maintainence",
                                               "companyMessage": u"company message maintainence",
                                               "xiniuVisit": u"visited company information through xiniu",
                                               "xiniuVisitWeb": u"visited company information through web",
                                               "xiniuVisitApp": u"visited company information through app",
                                               "openapiVisit": u"visited company information through api",
                                               "newCrawler": u"new crawlered companies from other sources",
                                               "newCreated": u"new created companies by users",
                                               "portfolio": u"fund portfolio",
                                               "gongshang": u'gongshang change',
                                               "split": u'split'}

        self.maintain_type_mongo_task_company_type_dict = {"nonFundNews": "news_funding",
                                                           "fundNews": "news_regular",
                                                           "fa": "company_fa",
                                                           "topicMessage": "track_topic",
                                                           "companyMessage": "track_company",
                                                           "xiniuVisit": "visit_local",
                                                           "xiniuVisitWeb": "visit_web",
                                                           "xiniuVisitApp": "visit_app",
                                                           "openapiVisit": "visit_openapi",
                                                           "newCrawler": "company_newcover",
                                                           "newCreated": "company_create",
                                                           "portfolio": "investor_portfolio",
                                                           "gongshang": "track_gongshang",
                                                           "split": "company_split"}

        self.maintain_type_related_company_ids_method = {"nonFundNews": self._get_non_fund_news_task_related_company_ids_list,
                                                         "fundNews": self._get_fund_news_task_related_company_ids_list,
                                                         "fa": self._get_fa_related_company_ids_list,
                                                         "topicMessage": self._get_topic_message_related_company_ids_list,
                                                         "companyMessage": self._get_company_message_related_company_ids_list,
                                                         "xiniuVisit": self._get_xiniu_visit_company_ids_list,
                                                         "xiniuVisitWeb": self._get_xiniu_visit_web_company_ids_list,
                                                         "xiniuVisitApp": self._get_xiniu_visit_app_company_ids_list,
                                                         "openapiVisit": self._get_openapi_visit_related_company_ids_list,
                                                         "newCrawler": self._get_new_crawlered_related_company_ids_list,
                                                         "newCreated": self._get_new_created_related_company_ids_list,
                                                         "portfolio": self._get_investor_portfolio_task_related_company_ids_list,
                                                         "gongshang": self._get_gongshang_related_company_ids_list,
                                                         "split": self._get_split_related_company_ids_list}

    def _clean_collection_daily_statistics(self, coll, fields, **kwargs):
        return clean_collection_daily_statistics_method_helper(self, coll, fields, **kwargs)

    def _get_username(self, uid):
        return get_user_name_helper(self, uid)

    def _daily_processed_article_news_df(self):
        t0 = turn_date_to_datetime(self.curr_day)
        t1 = turn_date_to_datetime(self.next_day)

        # mongo.article.news modifytime utc+8
        condition = dict()
        condition["modifyTime"] = {"$gt": t0, "$lt": t1}
        condition["processStatus"] = 1
        cr = mongo.article.news.find(condition)

        df = pd.DataFrame(list(cr))
        columns = ["_id", "features", "companyIds"]

        df = modify_df_columns(df, columns)

        # 融资新闻tagid = 578349
        tagid = 578349
        df["isFundNews"] = df["features"].map(lambda x: type(x) is list and tagid in x)

        columns = ["_id", "isFundNews", "companyIds"]
        df = modify_df_columns(df, columns)

        return df

    def _daily_new_company_ids_df(self):
        r = db.query("SELECT c.*, sc.source FROM company c, source_company sc "
                     "WHERE c.id=sc.companyid "
                     "AND c.createtime>%s And c.createtime<%s "
                     "AND sc.createtime>%s And sc.createtime<%s;",
                     self.curr_day, self.next_day,
                     self.curr_day, self.next_day)
        df = pd.DataFrame(r)

        columns = ["id", "source", "active"]

        for col in columns:
            if col not in df.columns:
                df[col] = np.nan

        df = modify_df_columns(df, columns)
        return df

    def insert_all_related_company_stat(self):

        cids_list = [self._insert_related_company_stat_template(maintain_type)
                     for maintain_type in self.maintain_type_list]

        # insert summary stat
        cids = [cid for cids in cids_list for cid in cids]

        reset_statistic_field_list = ["relatedAmount", "relatedCompanyIds"]
        filter_condition = dict()
        filter_condition["date_yyyymmdd"] = self.yyyymmdd
        filter_condition["type"] = "summary"
        self._clean_collection_daily_statistics(self.stat_collection, reset_statistic_field_list,
                                                filter_condition=filter_condition)

        related_company_ids_list = list(set(cids))
        related_company_amount = len(related_company_ids_list)

        set_condition = dict()
        set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
        set_condition["relatedAmount"] = related_company_amount
        set_condition["relatedCompanyIds"] = related_company_ids_list

        ur = self.stat_collection.update_one(filter_condition, {"$set": set_condition}, upsert=True)
        logger.info("{} new related companies "
                    "{} in total.".format(self.yyyymmdd,
                                          related_company_amount))

    def _insert_related_company_stat_template(self, maintain_type):
        reset_statistic_field_list = ["relatedAmount", "relatedCompanyIds"]
        filter_condition = dict()
        filter_condition["date_yyyymmdd"] = self.yyyymmdd
        filter_condition["maintainType"] = maintain_type
        self._clean_collection_daily_statistics(self.stat_collection, reset_statistic_field_list,
                                                filter_condition=filter_condition)

        related_company_ids_list = self.maintain_type_related_company_ids_method[maintain_type]()
        related_company_amount = len(related_company_ids_list)

        set_condition = dict()
        set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
        set_condition["relatedAmount"] = related_company_amount
        set_condition["relatedCompanyIds"] = related_company_ids_list

        ur  = self.stat_collection.update_one(filter_condition, {"$set": set_condition}, upsert=True)
        logger.info("{} new related companies related to {} "
                    "{} in total.".format(self.yyyymmdd, self.maintain_type_log_message_dict[maintain_type],
                                          related_company_amount))

        return related_company_ids_list

    # drop duplicates
    def _get_non_fund_news_task_related_company_ids_list(self):
        df = self.df_processed_article_news
        df = df[~df["isFundNews"]]
        df = df[~df["companyIds"].isnull()]
        cids = [cid for subcids in df["companyIds"].tolist() for cid in subcids]
        return list(set(cids))

    def _get_fund_news_task_related_company_ids_list(self):
        df = self.df_processed_article_news
        df = df[df["isFundNews"]]
        df = df[~df["companyIds"].isnull()]
        cids = [cid for subcids in df["companyIds"].tolist() for cid in subcids]
        return list(set(cids))

    def _get_investor_portfolio_task_related_company_ids_list(self):

        r = db.query('select * from audit_investor_company where operateTime>%s and operateTime<%s;',
                     self.curr_day, self.next_day)
        cids = [int(x['companyId']) for x in r if x['companyId'] is not None]
        return list(set(cids))

    def _get_fa_related_company_ids_list(self):
        r = db.query("select * from company_fa "
                     "where modifytime > %s "
                     "and modifytime < %s "
                     "and processStatus in (1, 2);",
                     self.curr_day, self.next_day)
        cids = [int(x['companyId']) for x in r if x['companyId'] is not None]
        return list(set(cids))

    def _get_gongshang_related_company_ids_list(self):

        r = db.query("select * from company_message "
                     "where publishtime > %s "
                     "and publishtime < %s "
                     "and trackdimension=5001;",
                     self.curr_day, self.next_day)
        cids = [int(x['companyId']) for x in r if x['companyId'] is not None]
        return list(set(cids))

    def _get_split_related_company_ids_list(self):

        cids = [record.get('replacement', [])
                for record in mongo.task.corporate_decompose.find({'modifyTime': {'$gt': self.curr_date}})]
        cids = [item.get('newCompanyId') for item in chain(*cids)
                if item.get('newCompanyId') and isinstance(item.get('newCompanyId'), int)]
        return list(set(cids))

    def _get_topic_message_related_company_ids_list(self):
        r = db.query("select * from topic_company "
                     "where publishtime > %s "
                     "and publishtime < %s "
                     "and active='Y';",
                     self.curr_day, self.next_day)
        cids = [int(x['companyId']) for x in r if x['companyId'] is not None]
        return list(set(cids))

    def _get_company_message_related_company_ids_list(self):
        r = db.query("select * from company_message "
                     "where publishtime > %s "
                     "and publishtime < %s "
                     "and active in ('P', 'Y', 'N');",
                     self.curr_day, self.next_day)
        cids = [int(x['companyId']) for x in r if x['companyId'] is not None]
        return list(set(cids))

    def _get_xiniu_visit_company_ids_list(self):

        cids = self._get_xiniu_visit_app_company_ids_list() + self._get_xiniu_visit_web_company_ids_list()
        return list(set(cids))

    def _get_xiniu_visit_web_company_ids_list(self):
        # 网页 mongo.log.user_log.find({"requestURL": "/xiniudata-api/api2/service/company/basic"}, {"jsonRequest": 1})
        #     jsonRequest->payload->code
        t0 = turn_date_to_datetime(self.curr_day) - datetime.timedelta(hours=8)
        t1 = turn_date_to_datetime(self.next_day) - datetime.timedelta(hours=8)
        condition_web = {"requestURL": "/xiniudata-api/api2/service/company/basic",
                         "time": {"$gt": t0, "$lt": t1},
                         "userId": {"$exists":1}}
        cr_web = mongo.log.user_log.find(condition_web)

        ccodes_web = [x.get("jsonRequest", dict()).get("payload", dict()).get("code", "")
                      for x in cr_web if type(x.get("jsonRequest", dict())) is dict]
        ccodes_web.append(u"")
        ccodes_web = list(set(ccodes_web))
        cids_web = [x["id"] for x in db.query("select id from company where code in %s;", ccodes_web)]
        cids_web = map(int, set(cids_web))

        return cids_web

    def _get_xiniu_visit_app_company_ids_list(self):
        # iOS mongo.log.user_log.find({"requestURL": "/xiniudata-api/api/mobile/company/info"}, {"jsonRequest": 1})
        #     jsonRequest->payload->companyId
        t0 = turn_date_to_datetime(self.curr_day) - datetime.timedelta(hours=8)
        t1 = turn_date_to_datetime(self.next_day) - datetime.timedelta(hours=8)
        condition_iOS = {"requestURL": "/xiniudata-api/api/mobile/company/info",
                         "time": {"$gt": t0, "$lt": t1}}
        cr_iOS = mongo.log.user_log.find(condition_iOS)

        cids_iOS = [x.get("jsonRequest", dict()).get("payload", dict()).get("companyId", None) for x in cr_iOS
                    if type(x.get("jsonRequest", dict())) is dict]
        cids_iOS = filter(None, cids_iOS)
        cids_iOS = map(int, set(cids_iOS))

        return cids_iOS

    def _get_openapi_visit_related_company_ids_list(self):
        return []

    def _get_new_crawlered_related_company_ids_list(self):
        df = self._daily_new_company_ids_df()
        # sourceid 不为 13001: 人工创建(归入new_created); 13030: IT桔子(不需要审核即发布);
        df = df[~df["source"].isin([13001, 13030])]
        cids = df["id"].tolist()
        return map(int, set(cids))

    def _get_new_created_related_company_ids_list(self):
        df = self._daily_new_company_ids_df()
        # sourceid 为 13001: 人工创建(归入new_created); 13030: IT桔子(不需要审核即发布); 13050: 36kr助手(不需要审核即发布);
        df = df[df["source"].isin([13001])]
        cids = df["id"].tolist()
        return map(int, set(cids))

    def insert_all_task_validated_company_stat(self):

        cids_tuple_list = [self._insert_validated_company_stat_template(maintain_type)
                           for maintain_type in self.maintain_type_list]

        # summary
        ncids = [cid for cids_tuple in cids_tuple_list for cid in cids_tuple[0]]
        modcids = [cid for cids_tuple in cids_tuple_list for cid in cids_tuple[1]]
        mcids = [cid for cids_tuple in cids_tuple_list for cid in cids_tuple[2]]

        reset_statistic_field_list = ["newAmount", "newCompanyIds",
                                      "modifiedOnDayAmount", "modifiedOnDayCompanyIds",
                                      "modifiedAmount", "modifiedCompanyIds"]
        filter_condition = {"date_yyyymmdd": self.yyyymmdd,
                            "type": "summary"}
        self._clean_collection_daily_statistics(self.stat_collection, reset_statistic_field_list,
                                                filter_condition=filter_condition)

        cids_lists = [list(set(ncids)), list(set(modcids)), list(set(mcids))]

        new_validated_company_ids_list = cids_lists[0]
        modified_on_day_validated_company_ids_list = cids_lists[1]
        modified_validated_company_ids_list = cids_lists[2]
        new_validated_company_amount = len(new_validated_company_ids_list)
        modified_on_day_validated_company_amount = len(modified_on_day_validated_company_ids_list)
        modified_validated_company_amount = len(modified_validated_company_ids_list)

        set_condition = dict()
        set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
        set_condition["newAmount"] = new_validated_company_amount
        set_condition["newCompanyIds"] = new_validated_company_ids_list
        set_condition["modifiedOnDayAmount"] = modified_on_day_validated_company_amount
        set_condition["modifiedOnDayCompanyIds"] = modified_on_day_validated_company_ids_list
        set_condition["modifiedAmount"] = modified_validated_company_amount
        set_condition["modifiedCompanyIds"] = modified_validated_company_ids_list

        ur = self.stat_collection.update_one(filter_condition, {"$set": set_condition}, upsert=True)
        logger.info("{} new validated companies "
                    "{} in total.".format(self.yyyymmdd,
                                          new_validated_company_amount))
        logger.info("{} new validated companies modified on current day "
                    "{} in total.".format(self.yyyymmdd,
                                          modified_on_day_validated_company_amount))
        logger.info("{} modified validated companies "
                    "{} in total.".format(self.yyyymmdd,
                                          modified_validated_company_amount))

    def _insert_validated_company_stat_template(self, maintain_type):
        reset_statistic_field_list = ["newAmount", "newCompanyIds",
                                      "modifiedOnDayAmount", "modifiedOnDayCompanyIds",
                                      "modifiedAmount", "modifiedCompanyIds"]
        filter_condition = {"date_yyyymmdd": self.yyyymmdd, "maintainType": maintain_type}
        self._clean_collection_daily_statistics(self.stat_collection, reset_statistic_field_list,
                                                filter_condition=filter_condition)

        cids_lists = self._get_validated_company_ids_list(maintain_type)

        new_validated_company_ids_list = cids_lists[0]
        modified_on_day_validated_company_ids_list = cids_lists[1]
        modified_validated_company_ids_list = cids_lists[2]
        new_validated_company_amount = len(new_validated_company_ids_list)
        modified_on_day_validated_company_amount = len(modified_on_day_validated_company_ids_list)
        modified_validated_company_amount = len(modified_validated_company_ids_list)

        set_condition = dict()
        set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
        set_condition["newAmount"] = new_validated_company_amount
        set_condition["newCompanyIds"] = new_validated_company_ids_list
        set_condition["modifiedOnDayAmount"] = modified_on_day_validated_company_amount
        set_condition["modifiedOnDayCompanyIds"] = modified_on_day_validated_company_ids_list
        set_condition["modifiedAmount"] = modified_validated_company_amount
        set_condition["modifiedCompanyIds"] = modified_validated_company_ids_list

        ur = self.stat_collection.update_one(filter_condition, {"$set": set_condition}, upsert=True)
        logger.info("{} new validated companies related to {} "
                    "{} in total.".format(self.yyyymmdd, self.maintain_type_log_message_dict[maintain_type],
                                          new_validated_company_amount))
        logger.info("{} new validated companies modified on current day related to {} "
                    "{} in total.".format(self.yyyymmdd, self.maintain_type_log_message_dict[maintain_type],
                                          modified_on_day_validated_company_amount))
        logger.info("{} modified validated companies related to {} "
                    "{} in total.".format(self.yyyymmdd, self.maintain_type_log_message_dict[maintain_type],
                                          modified_validated_company_amount))

        return new_validated_company_ids_list, modified_on_day_validated_company_ids_list, modified_validated_company_ids_list

    def _daily_company_task_df(self):
        t0 = turn_date_to_datetime(self.curr_day) - datetime.timedelta(hours=8)
        t1 = turn_date_to_datetime(self.next_day) - datetime.timedelta(hours=8)

        condition = dict()
        condition["finishTime"] = {"$gt": t0, "$lt": t1}

        return_fields_condition = dict()
        return_fields_condition["taker"] = 1
        return_fields_condition["processStatus"] = 1

        cr = mongo.task.company.find(condition, return_fields_condition)

        df = pd.DataFrame(list(cr))

        columns = ["_id", "taker", "processStatus"]

        df = modify_df_columns(df, columns)

        return df

    def _get_validated_company_ids_list(self, maintain_type):
        t0 = turn_date_to_datetime(self.curr_day) - datetime.timedelta(hours=8)
        t1 = turn_date_to_datetime(self.next_day) - datetime.timedelta(hours=8)

        condition_new = {"types": self.maintain_type_mongo_task_company_type_dict[maintain_type],
                         "taskDate": self.yyyymmdd}
        condition_modified = {"types": self.maintain_type_mongo_task_company_type_dict[maintain_type],
                              "finishTime": {"$gt": t0, "$lt": t1},
                              "processStatus": {"$in": [1, 2]}}
        cr_new = mongo.task.company.find(condition_new)
        cr_modified = mongo.task.company.find(condition_modified)

        cids_new = [x.get("companyId") for x in cr_new]
        cids_modified = [x.get("companyId") for x in cr_modified]

        cids_new = filter(None, cids_new)
        cids_modified = filter(None, cids_modified)

        cids_new = set(cids_new)
        cids_modified = set(cids_modified)
        cids_modified_on_day = cids_new & cids_modified

        cids_new = map(int, cids_new)
        cids_modified_on_day = map(int, cids_modified_on_day)
        cids_modified = map(int, cids_modified)

        return cids_new, cids_modified_on_day, cids_modified

    def insert_company_task_by_user_stat(self):
        reset_statistic_field_list = ["companyTaskTotalAmount",
                                      "companyTaskUnqualifiedAmount",
                                      "companyTaskFinishedAmount",
                                      "companyTaskQualifiedAmount"]
        filter_condition = {"date_yyyymmdd": self.yyyymmdd}
        self._clean_collection_daily_statistics(self.stat_collection, reset_statistic_field_list,
                                                filter_condition=filter_condition)

        df = self.df_company_task
        gb = df.groupby("taker")

        for group in gb:
            uid = group[0]
            if uid:
                uid = int(uid)
            else:
                continue
            uname = self._get_username(uid)

            df0 = group[1]

            filter_condition = {"date_yyyymmdd": self.yyyymmdd}
            filter_condition["userId"] = uid

            df_finished = df0[df0["processStatus"] == 1]
            df_qualified = df0[df0["processStatus"] == 2]
            df_unqualified = df0[df0["processStatus"] == -1]
            df_total = df0[df0["processStatus"].isin([-1, 1, 2])]

            set_condition = dict()
            set_condition["lastUpdateTime"] = datetime.datetime.utcnow()
            set_condition["userName"] = uname
            set_condition["companyTaskFinishedAmount"] = len(df_finished)
            set_condition["companyTaskQualifiedAmount"] = len(df_qualified)
            set_condition["companyTaskTotalAmount"] = len(df_total)

            row = self.user_stat_collection.find_one(filter_condition)
            ori_unqualified_list = row.get("unqualifiedTaskIdHistory") if row else None
            if ori_unqualified_list is None:
                ori_unqualified_list = list()
            new_unqualified_list = map(str, df_unqualified["_id"].tolist())
            if new_unqualified_list is None:
                new_unqualified_list = list()
            new_unqualified_list.extend(ori_unqualified_list)
            new_unqualified_list = list(set(new_unqualified_list))

            set_condition["companyTaskUnqualifiedAmount"] = len(new_unqualified_list)
            set_condition["unqualifiedTaskIdHistory"] = new_unqualified_list

            ur = self.user_stat_collection.update_one(filter_condition, {"$set": set_condition}, upsert=True)
            logger.info("{} userId:{} userName:{} modified "
                        "task company {} in total, "
                        "unqualifed {}, "
                        "finished {}, "
                        "qualified {}".format(self.yyyymmdd, uid, uname,
                                              set_condition["companyTaskTotalAmount"],
                                              set_condition["companyTaskUnqualifiedAmount"],
                                              set_condition["companyTaskFinishedAmount"],
                                              set_condition["companyTaskQualifiedAmount"]))


def test():
    test_all()


def test_news_task():

    curr = datetime.date.today()
    back_day = curr -  datetime.timedelta(0)
    st = Stat_News_Task(back_day)
    st.insert_new_news_task_stat()
    st.insert_modified_news_task_stat()


def test_new_company():

    curr = datetime.date.today()
    for i in range(30):
        back_day = curr - datetime.timedelta(i)
        st = Stat_New_Company_Task(curr_day=back_day)
        st.insert_new_company_stat()


def test_maintainence():
    s = Stat_Company_Maintainence()
    s.insert_all_task_validated_company_stat()


def test_new_company_ids():
    s = Stat_Company_Maintainence()
    df = s.df_new_company_ids
    df = df[~df["source"].isin([13001, 13030])]
    print df


def test_all():

    d = datetime.date.today()- datetime.timedelta(1)

    snt = Stat_News_Task(d)
    snt.insert_new_news_task_stat()
    snt.insert_modified_news_task_stat()

    snct = Stat_New_Company_Task(d)
    snct.insert_new_company_stat()

    scm = Stat_Company_Maintainence(d)
    scm.insert_all_related_company_stat()
    scm.insert_all_task_validated_company_stat()
    scm.insert_company_task_by_user_stat()


def main():

    snt = Stat_News_Task()
    snt.insert_new_news_task_stat()
    snt.insert_modified_news_task_stat()

    snct = Stat_New_Company_Task()
    snct.insert_new_company_stat()

    scm = Stat_Company_Maintainence()
    scm.insert_all_related_company_stat()
    scm.insert_all_task_validated_company_stat()
    scm.insert_company_task_by_user_stat()


def makeup():

    for delta in xrange(6, 45, 1):
        # company
        scm = Stat_Company_Maintainence(datetime.date.today()-datetime.timedelta(days=delta))
        scm.insert_company_task_by_user_stat()
        # news
        snt = Stat_News_Task(datetime.date.today()-datetime.timedelta(days=delta))
        snt.insert_modified_news_task_stat()


def _clean_all():

    pass


if __name__ == "__main__":
    if sys.argv[1] == "main":
        main()
    elif sys.argv[1] == "test":
        test()
    elif sys.argv[1] == 'makeup':
        makeup()
    db.close()
    mongo.close()




