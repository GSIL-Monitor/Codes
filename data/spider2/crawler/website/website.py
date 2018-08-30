# -*- coding: utf-8 -*-
import os, sys
import urllib2
from lxml import html
from pyquery import PyQuery as pq
# import gevent
# from gevent.event import Event
# from gevent import monkey; monkey.patch_all()
import json
from StringIO import StringIO
import gzip

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import util
import loghelper
import url_helper

#logger
loghelper.init_logger("website", stream=True)
logger = loghelper.get_logger("website")

def get_meta_info(url):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
    headers = {'User-Agent': user_agent,
               'accept-language':'zh-CN,zh;q=0.8,en;q=0.6',
               'Accept-Encoding':'gzip'}
    try:
        request = urllib2.Request(url, None, headers)
    except:
        return None
    opener = urllib2.build_opener()
    retries = 0
    while True:
        try:
            r = opener.open(request, timeout=17)
            if r.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(r.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            else:
                data = r.read()
            content = util.html_encode(data)
            redirect_url = url_helper.url_normalize(r.geturl())
            #logger.info(redirect_url)
            #logger.info(content)
            d = pq(html.fromstring(content))
            title = d("title").text()
            #logger.info(title)
            keywords = d("meta[name='keywords']").attr("content")
            if keywords is None:
                keywords = d("meta[name='Keywords']").attr("content")
            #logger.info(keywords)
            description = d("meta[name='description']").attr("content")
            if description is None:
                description = d("meta[name='Description']").attr("content")
            #logger.info(description)

            flag, domain = url_helper.get_domain(url)
            if flag is not True:
                domain = None
            return {
                "url": url,
                "redirect_url": redirect_url,
                "domain": domain,
                "title": title,
                "tags": keywords,
                "description": description,
                "httpcode": 200
            }
            break
        except:
            retries += 1
        if retries >= 3:
            return None
    return None

if __name__ == "__main__":
    url = "http://www.eclss.com"
    #url = "http://news.sina.com.cn/c/nd/2016-06-04/doc-ifxsuypf4962857.shtml"
    #url = "http://cnews.chinadaily.com.cn/2016-06/05/content_25615727.htm"
    #url = "http://ent.aili.com/1475/2734576.html"
    #url = "http://www.wandoujia.com/apps/com.bringmore.SpaceStations"
    result = get_meta_info(url)
    logger.info(json.dumps(result, ensure_ascii=False, cls=util.CJsonEncoder))
