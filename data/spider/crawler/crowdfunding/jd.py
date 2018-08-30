#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import datetime
import random
import json


reload(sys)
sys.setdefaultencoding("utf-8")
import my_request
import util
import spider_util
import time
from pyquery import PyQuery as pq

source = 13010
#################################################
def fetch_dj():
    url = 'http://dj.jd.com/'
    threads = []
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        d = pq(r.text)
        links = d('a')
        for link in links:
            link = pq(link)
            link = link.attr('href')
            if link is not None and '/funding/details/' in link:
                print link
                fetch_project(link)

        divs = d('.show-text')
        for div in divs:
            div = pq(div)
            link = div('a').attr('href')
            desc = div('p').attr('title')
            fetch_desc(link, desc)





def fetch_project(url):
    (cf_key, ) = util.re_get_result("http://dj.jd.com/funding/details/(\d+).html", url)
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        html = r.text
        support = fetch_support(cf_key)
        focus = fetch_focus(url, cf_key)
        team = fetch_team(cf_key)
        leader = fetch_leader(cf_key)

        bp = fetch_bp(html, url, cf_key)


        content = {'html': html,
                   'team': team,
                   'support': support,
                   'focus': focus
                   }

        project = {"date":datetime.datetime.now(),
                   "source":source,
                   "url":url,
                   "company_key": cf_key,
                   "cf_key":cf_key,
                   "content":content,
                   'leader': leader,
                   'bp': bp
                   }

        result = cf_collection.find_one({"source":source, "company_key":cf_key, 'cf_key': cf_key})
        if result != None:
            cf_collection.replace_one({'_id': result['_id']}, project)
        else:
            cf_collection.insert_one(project)

        msg = {"type":"cf", "source":source, "cf_key":cf_key}
        logger.info(json.dumps(msg))
        kafka_producer.send_messages("crawler_cf_jd_v2", json.dumps(msg))


def fetch_team(cf_key):
    url = "http://dj.jd.com/funding/findProjectTeam.action?projectId="+cf_key
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        return r.text


def fetch_support(cf_key):
    url = 'http://dj.jd.com/funding/selectSupportCount.action?projectId='+cf_key+'&minimumAmount=100,000&silkmumAmount=10,000'
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        return r.text


def fetch_focus(referer, cf_key):
    s.headers['Referer'] = referer
    url = 'http://sq.jr.jd.com/cm_focus/isFocus?key=4000&systemId='+cf_key

    r= s.get(url)
    return r.text


def fetch_bp(html, referer, cf_key):
    d = pq(html)
    script = d('script').text()
    script = ''.join(script)
    try:
        (pdf_key, ) = util.re_get_result("pptKey = \"(\S+)\"", script)
    except Exception, e:
        return None

    url = 'http://dj.jd.com/funding/downloadPdf.action?projectId='+cf_key
    r = s.post(url, data={'pptkey': pdf_key})
    url = r.text.decode('unicode-escape')
    url = url.replace('"', '')
    print url

    bp = None
    result = cf_collection.find_one({"source":source, "company_key":cf_key, 'cf_key': cf_key})
    if result != None:
        content = result['content']
        if content.get('bp'):
            bp = content.get('bp')
            if pdf_key == bp.get('key'):
                bp = {'bp_id': bp['bp_id'], 'key': pdf_key}
        else:
            file_id = spider_util.save_pdf(r.content, source, cf_key)
            bp = {'bp_id': file_id, 'key': pdf_key}
    else:
        s.headers['Referer'] = referer
        r = s.get(url, stream=True)
        file_id = spider_util.save_pdf(r.content, source, cf_key)
        bp = {'bp_id': file_id, 'key': pdf_key}

    return bp


def fetch_leader(cf_key):
    url = 'http://dj.jd.com/funding/leaderInverstorDetail/'+cf_key+'.html'
    (flag, r) = my_request.get(logger, url)
    if flag == 0:
        if u'东家温馨提示：您查询的内容不存在！' in r.text:
            return None
            
        return r.text



def fetch_desc(link, desc):
    try:
        (cf_key, ) = util.re_get_result("http://dj.jd.com/funding/details/(\d+).html", link)
    except Exception, e:
        cf_key = None

    if cf_key is not None:
        result = cf_collection.find_one({"source":source, "company_key":cf_key, 'cf_key': cf_key})
        if result is not None:
            result['desc'] = desc
            cf_collection.replace_one({'_id': result['_id']}, result)

            msg = {"type":"jd_patch", "source":source, "cf_key":cf_key}
            logger.info(json.dumps(msg))
            kafka_producer.send_messages("crawler_cf_jd_v2", json.dumps(msg))






login_user = {"name":"dqatsh", "pwd":"du51601618"}

def login():
    while True:
        try:
            global s
            s = my_request.get_https_session(new=True, agent=True)
            login_url = 'https://passport.jd.com/uc/login'

            randomCode = random.uniform(0.1, 1.0)
            r = s.get(login_url)
            d = pq(r.text)

            uuid = d('input:eq(0)').attr('value')
            param = d('input:eq(4)').attr('name')
            param_value = d('input:eq(4)').attr('value')

            loginname = login_user['name']
            loginpwd = login_user['pwd']

            verify_url = 'https://passport.jd.com/uc/showAuthCode?r='+str(randomCode)+'&version=2015'
            r = s.post(verify_url, data={'loginName': loginname}, timeout=10)
            result = r.text.replace('(', '').replace(')', '')

            verify = json.loads(result)
            logger.info(verify)
            if not verify['verifycode']:
                data = {'uuid': uuid,
                        param: param_value,
                        'loginname': loginname,
                        'nloginpwd': loginpwd,
                        'loginpwd': loginpwd,
                        'chkRememberMe': 'on',
                        'authcode': None}

                url = 'https://passport.jd.com/uc/loginService?uuid='+uuid+'&version=2015'
                r = s.post(url, data, timeout=10)

                logger.info(r.text)
                if "success" in r.text:
                    return True

        except Exception,ex:
            logger.exception(ex)
            time.sleep(60)

    return False


if __name__ == "__main__":
    (logger, mongo, kafka_producer, company_collection, member_collection, news_collection, cf_collection) \
        = spider_util.spider_cf_init('cf_jd')

    type = ''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            type = 'all'
        else:
            type = 'incr'
    else:
        type = 'incr'

    login()
    fetch_dj()
