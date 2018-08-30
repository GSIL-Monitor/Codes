# -*- encoding=utf-8 -*-
__author__ = "kailu"

import os
import sys
import math
import cPickle as pickle
import re
import urllib
from collections import Counter
from bson import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], ".."))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], "../../util"))

from datetime import datetime, timedelta, date
import ast

import numpy as np
import pandas as pd
# import matplotlib as mpl

mpl.use('Agg')

# import matplotlib.pyplot as plt

import db as dbcon
import loghelper

# logger
loghelper.init_logger("user_log", stream=True)
logger = loghelper.get_logger("user_log")


db = dbcon.connect_torndb()
mongo = dbcon.connect_mongo()


def get_user_name(uid):
    global db
    r = db.query("select username from user where id =%s", uid)
    if r:
        return r[0]["username"]
    else:
        return None


def get_news_title(nid):
    global mongo
    r = mongo.article.news.find_one({"_id":ObjectId(nid)})
    if r:
        return r.get('title')
    else:
        return None


def get_organization_ids(oname="烯牛"):
    db = dbcon.connect_torndb()
    query_string = "select id from organization where name like '%%{}%%';".format(oname)
    oids = [item.id for item in db.query(query_string)]
    db.close()
    return oids


def get_all_user_ids():
    db = dbcon.connect_torndb()
    query_string = "select id from user where active='Y';"
    uids = [item.id for item in db.query(query_string)]
    db.close()
    return uids


def get_organization_user_ids(oids):
    db = dbcon.connect_torndb()
    query_string = "select userId from user_organization_rel where organizationId in %s and active='Y';"
    uids = [item["userId"] for item in db.query(query_string, oids)]
    db.close()
    return uids


def get_log_df(condition=None):
    mongo = dbcon.connect_mongo()
    cr = mongo.log.user_log.find(condition)
    mongo.close()
    return pd.DataFrame(list(cr))


def clean_users(df):
    xoids = get_organization_ids(oname="烯牛")
    xuids = get_organization_user_ids(oids=xoids)
    all_uids = get_all_user_ids()

    new_df = df[df["userId"].isin(all_uids)]
    new_df = new_df[~new_df["userId"].isin(xuids)]

    return new_df


def get_pageview_df(**kwargs):

    condition = {"requestURL": "/api-company/api/company/crawler/log/addPageView"}

    if "time_begin" in kwargs:
        time_subcondition = condition.setdefault("time", {})
        time_subcondition["$gt"] = kwargs["time_begin"]

    if "time_end" in kwargs:
        time_subcondition = condition.setdefault("time", {})
        time_subcondition["$lt"] = kwargs["time_end"]

    return get_log_df(condition)


# unpack jsonRequest payload
def get_unpacked_df(pageview_df):
    temp_l = []
    for row in pageview_df.iterrows():
        r = row[1]
        d = dict()
        d["ip"] = r["ip"]
        d["userId"] = r["userId"]

        jsonRequest = r["jsonRequest"]

        if type(jsonRequest) == unicode:
            try:
                s = ast.literal_eval(jsonRequest)["payload"]
            except SyntaxError:
                logger.warning("The payload of {} can not be unfolded".format(str(r["_id"])))
        elif type(jsonRequest) == dict:
            s = jsonRequest["payload"]
        else:
            s = {}

        for k, v in s.iteritems():
            d[k] = v
        d["time"] = r["time"]
        temp_l.append(d)

    unpacked_df = pd.DataFrame(temp_l)
    unpacked_df[["subRouter"]] = unpacked_df[["subRouter"]].fillna(value="")
    return unpacked_df


# get the word searched by users
def extract_word(urlstring):

    def get_str(s):
        if s is None:
            return s
        tp = type(s)
        if tp == str:
            return s
        if tp == unicode:
            t = s.__repr__()
            s = eval(t[1:])
            return s
        return

    pre_m = "http://m.xiniudata.com/#/search/open/"
    m = re.match("{}(.*)".format(pre_m), urlstring)
    if m:
        s =  urllib.unquote(m.group(1))
        return get_str(s)


    pre_www = "http://www.xiniudata.com/search/#/open/"
    m = re.match("{}(.*)".format(pre_www), urlstring)
    if m:
        s =  urllib.unquote(m.group(1))
        return get_str(s)

    return None


def extract_newsid(urlstring):
    pre_m = "http://m.xiniudata.com/#/news/"
    m = re.match("{}(.*)".format(pre_m), urlstring)
    if m:
        return m.group(1)
    pre_www = "http://www.xiniudata.com/#/news/"
    m = re.match("{}(.*)".format(pre_www), urlstring)
    if m:
        return m.group(1)
    return None


def get_all_search_history(unpacked_df):
    df = get_router_df(unpacked_df, "search")
    # df = unpacked_df[unpacked_df["router"] == "search"]

    words = df["url"].map(extract_word).values()

    # words = []
    # for row in df.iterrows():
    #     w = extract_word(row[1]["url"])
    #     if w:
    #         words.append(w)

    return words


def get_router_df(df, router):
    return df[df["router"] == router]


def analyze_search_history(**kwargs):
    pageview_df = get_pageview_df(**kwargs)
    unpacked_df = get_unpacked_df(pageview_df)
    words = get_all_search_history(unpacked_df)
    wc = Counter(words)
    for word, c in wc.most_common(10):
        print word, c


def get_date(t_timestamp):

    d = t_timestamp + timedelta(hours=8)
    return date(d.year, d.month, d.day)


def analyze_recommend(**kwargs):
    pageview_df = get_pageview_df(**kwargs)
    df_r = get_router_df(pageview_df, "recommend")
    df_c = get_router_df(pageview_df, "company")
    isclicked = []
    user_cache = {}

    for row in df_r.iterrows():
        uid = row[1]['userId']
        t = row[1]['time']
        t1 = t + pd.Timedelta(minutes=10)
        if uid not in user_cache:
            udict = {}
            df_p = df_c[df_c['userId'] == uid]
            code_query = "select code from company c, recommendation r where r.userid={} and c.id=r.companyid".format(uid)
            codes = [item['code'] for item in db.query(code_query)]
            code_set = set(['http://www.xiniudata.com/#/company/{}/overview'.format(code) for code in codes])
            user_cache[uid] = {"df": df_p, "codes": code_set}
        codes, df_p = user_cache[uid]["codes"], user_cache[uid]["df"]
        df_p = df_p[df_p['time'] > t]
        df_p = df_p[df_p['time'] < t1]
        urls = set(df_p['url'].tolist())
        visited = codes & urls
        if visited:
            isclicked.append(True)
        else:
            isclicked.append(False)
        user_cache[uid]["visited"] = user_cache[uid].setdefault("visited", set()).union(visited)
        user_cache[uid]["clicks"] = user_cache[uid].setdefault("clicks", 0) + 1

    df_result = pd.DataFrame([{"userId": uid, "clicks": user_cache[uid]["clicks"],
                               "visited": len(user_cache[uid]["visited"]),
                               "total": len(user_cache[uid]["codes"])
                               } for uid in user_cache.keys()])
    df_r["isclicked"] = isclicked

    # 点开咖啡杯人次
    print "点开咖啡杯人次 {}".format(len(df_r))
    # 10分钟内继续点开项目次数
    print "10分钟内继续点开项目次数 {}".format(len(set(df_r['userId'].tolist())))
    # 使用过咖啡杯人数
    print "使用过咖啡杯人数 {}".format(sum(isclicked))
    # 点开过项目人数
    grouped = df_r.groupby('userId')
    print "点开过项目人数 {}".format(sum([max(group['isclicked'].tolist()) for name, group in grouped]))


def test():
    pass

if __name__ == "__main__":
    test()

