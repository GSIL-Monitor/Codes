# -*- coding: utf-8 -*-

import sys,os
import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import config
import loghelper
import my_request
import util
import db
import extract
import requests
from pyquery import PyQuery as pq


# logger
loghelper.init_logger("trends_tool", stream=True)
logger = loghelper.get_logger("trends_tool")


def get_alexa(domain):
    url = 'http://www.alexa.com/siteinfo/'+domain

    proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
    while True:
        my_request.get_single_session(proxy, new=True, agent=False)
        # url = 'http://www.alexa.com/siteinfo/'+domain
        (flag, r) = my_request.get1(logger, url)
        if flag == 0:
            break

    d = pq(r.text)
    datas = d('strong.metrics-data')
    data_len = len(datas)

    global_rank = None
    country_rank = None
    bounce_rate = None
    daily_pageviews_per_visitor = None
    daily_time_on_site = None
    search_visits = None

    if data_len == 6:
        global_rank = pq(datas[0]).text()
        country_rank = pq(datas[1]).text()
        bounce_rate = pq(datas[2]).text()
        daily_pageviews_per_visitor = pq(datas[3]).text()
        daily_time_on_site = pq(datas[4]).text()
        search_visits = pq(datas[5]).text()
    elif data_len == 5:
        global_rank = pq(datas[0]).text()
        country_rank = ''
        bounce_rate = pq(datas[1]).text()
        daily_pageviews_per_visitor = pq(datas[2]).text()
        daily_time_on_site = pq(datas[3]).text()
        search_visits = pq(datas[4]).text()

    result = {
              'global_rank': global_rank,
              'country_rank': country_rank,
              'bounce_rate':bounce_rate,
              'daily_pageviews_per_visitor':daily_pageviews_per_visitor,
              'daily_time_on_site': daily_time_on_site,
              'search_visits':search_visits
              }

    return result



def website_info(domain):
    url = 'http://'+domain
    r = requests.get(url, timeout = 30)
    r.encoding = r.apparent_encoding
    if r.status_code == 200:
        d = pq(r.text)
        keywords = d('meta[name="keywords"]').attr('content')
        desc = d('meta[name="description"]').attr('content')
        result = {'keywords':keywords, 'desc': desc}
    else:
        result = -1

    return result


#########     baidu     #############
def baidu_index(keyword):
    url = 'http://index.baidu.com/?tpl=trend&word='+keyword
    d = pq(get(url))


def baidu_baike(keyword):
    url = 'http://baike.baidu.com/search/word?word='+keyword
    d = pq(get(url))
    content = d('.lemma-summary').text()

    return content

def baidu_search(keyword):
    url = 'http://www.baidu.com/s?ie=utf-8&fr=bks0000&wd='+keyword
    d = pq(get(url))
    nums = d('.nums').text()
    nums = nums.split('约')[1].replace('个','').replace(',','')

    rel_keywords = []
    for rel_keyword in d('th > a'):
        rel_keyword = pq(rel_keyword).text()
        rel_keywords.append(rel_keyword)

    result = {'total': int(nums), 'rel_keywords': rel_keywords}
    return result



#########     haosou     #############
def haosou_index(keyword):
    url = 'http://index.haosou.com/index.php?a=indexQuery&q='+keyword
    data = json.loads(get(url))
    data = data["data"]
    if not data.get('yes'):
        return -1

    url = 'http://index.haosou.com/index.php?a=soIndexJson&q='+keyword+'&area=%E5%85%A8%E5%9B%BD'
    index_data = json.loads(get(url))

    url = 'http://index.haosou.com/index.php?a=soMediaJson&q='+keyword
    media_data = json.loads(get(url))


def haosou_search(keyword):
    url = 'http://www.haosou.com/s?q='+ keyword
    d = pq(get(url))

    nums = d('span.nums').text()
    nums = nums[7:]
    nums = nums[0:len(nums)-1]
    nums = nums.replace(',', '')

    rel_keywords = []
    for rel_keyword in d('th > a'):
        rel_keyword = pq(rel_keyword).text()
        rel_keywords.append(rel_keyword)

    result = {'total': int(nums), 'rel_keywords': rel_keywords}
    return result



def haosou_news(keyword):
    url = 'http://news.haosou.com/ns?q='+keyword
    d = pq(get(url))

    result = []
    for li in d('.res-list'):
        li = pq(li)
        title = li('a.news_title').text()
        link = li('a.news_title').attr('href')
        site_name = li('span.sitename').text()
        post_time = li('span.posttime').attr('title')

        news_tag = []
        for tag in d('p.news_tag > a'):
            tag = pq(tag).text()
            if tag != '加入讨论>>':
                news_tag.append(tag)

        news = {'title': title, 'link': link, 'site_name': site_name, 'date': post_time, 'news_tag': news_tag}
        result.append(news)

    return result


#########     weibo     #############
def find_weibo(name):
    url = 'http://s.weibo.com/user/&work='+name
    cnt = 1
    while cnt < 100:
        result = []
        proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
        my_request.get_single_session(proxy, new=True, agent=False)
        (flag, r) = my_request.get(logger, url)
        if flag == 0:
            d = pq(r.text)

            find = True
            for s in d('script'):
                s = pq(s).text()
                s = ''.join(s)
                if 'STK && STK.pageletM && STK.pageletM.view' in s:
                    s = s.replace('STK && STK.pageletM && STK.pageletM.view(', '')
                    s = s[0: len(s)-1]
                    data = json.loads(s)
                    html = data['html']

                    if '你的行为有些异常，请输入验证码' in  html:
                        find = False

                    result.append(html)

        if not find or len(result) == 0:
            cnt +=1
        else:
            break

    data = result[2]

    d = pq(data)

    result = []
    for li in d('div.list_person'):
        li = pq(li)
        verify = li('p.person_name > a:eq(1)').attr('title')
        if verify == '微博机构认证':
            name = li('p.person_name > a:eq(0)').text()
            uid = li('p.person_name > a:eq(0)').attr('uid')
            location = li('p.person_addr > span:eq(1)').text()
            link = li('p.person_addr > a').text()

            follow = li('p.person_num > span:eq(0) > a').text()
            fans = li('p.person_num > span:eq(1) > a').text()
            publish = li('p.person_num > span:eq(2) > a').text()

            desc = li('div.person_info > p').text().replace('简介:', '').strip()
            tags = []
            for tag in li('p.person_label:eq(0) > a'):
                tag = pq(tag).text()
                tags.append(tag)

            tags = ','.join(tags)

            verify_company_name = li('person_label:eq(1) > a').text()

            account = {'name': name,
                       'uid': uid,
                       'location': location,
                       'link': link,
                       'follow': follow,
                       'fans': fans,
                       'publish': publish,
                       'desc': desc,
                       'tags': tags,
                       'verify_company_name': verify_company_name
                       }
            result.append(account)

    weibo = []
    for r in result:
        if r['verify_company_name'] == name or r['name'] == name:
            weibo.append(r)

    return weibo



def find_wechat(name, full_name):
    url = 'http://weixin.sogou.com/weixin?type=1&query='+name
    cnt = 1
    while cnt < 100:
        result = []
        proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
        my_request.get_single_session(proxy, new=True, agent=False)
        (flag, r) = my_request.get(logger, url)
        if flag == 0:
            if '您的访问过于频繁，为确认本次访问为正常用户行为，需要您协助验证' in r.text:
                find = False

            else:
                d = pq(r.text)

                for rt in d('div.wx-rb'):
                    rt = pq(rt)
                    name = rt('.txt-box > h3').text()
                    wechat_id = rt('.txt-box > h4').text()
                    if len(rt('.s-p3')) == 3:
                        brief = rt('.s-p3:eq(0) > .sp-txt').text()
                        verify = rt('.s-p3:eq(1) > .sp-txt').text()

                        name_str = ''
                        for n in name:
                            if n is None or n == ' ' :
                                pass
                            else:
                                name_str += n

                        wechat_id = wechat_id[4:]

                        wechat = {'name': name_str, 'id': wechat_id, 'brief': brief, 'verify_company_name': verify}
                        result.append(wechat)

                if len(result) > 0:
                    find = True

        if not find:
            cnt += 1
        else:
            break

    wechat = []
    for r in result:
        if r['verify_company_name'] == full_name:
            wechat.append(r)

    return wechat


def find_wechat1(name, full_name):
    url = 'http://weixin.sogou.com/weixin?type=1&query='+name

    # proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
    # my_request.get_single_session(proxy, new=True, agent=False)
    # (flag, r) = my_request.get(logger, url)
    # if flag == 0:

    r = requests.get(url)
    content = r.text
    headers = r.headers

    print content
    print headers





def get(url):
    r = requests.get(url, timeout = 10)
    r.encoding = r.apparent_encoding
    return r.text

if __name__ == '__main__':
    # domain = 'xin.com'

    # print get_alexa(domain)
    # print website_info(domain)

    # keyword = 'teambition'
    # print baidu_search(keyword)

    # company_name = '上海汇翼信息科技有限公司'
    # find_weibo(company_name)

    name = '篮圈'
    full_name = '厦门壹战信息科技有限公司'
    print find_wechat1(name, full_name)
