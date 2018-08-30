#/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from readability.readability import Document 
import urllib 
from HTMLParser import HTMLParser
import urlparse
import util
import datetime, time
import re
reload(sys)
sys.setdefaultencoding( "utf-8" )

class MyHTMLParser(HTMLParser):
    def __init__(self,url):
        HTMLParser.__init__(self)
        self.contents = []
        self.url = url
        self.tmp = ""

    def handle_starttag(self, tag, attrs):
        # print "Encountered the beginning of a %s tag" % tag
        if tag == "img":
            # print attrs
            if len(attrs) == 0: pass
            else:
                for (variable, value)  in attrs:
                    if variable == "src" or variable == "data-lazyload" or (
                            variable == 'zoomfile' and value.find("useit") >= 0) or (
                            variable == 'data-original' and value.find("ctoutiao") >= 0):
                        if value is not None and value.strip() != "":
                            aurl = urlparse.urljoin(self.url, value)
                            self.contents.append({"type":"img", "data":aurl})

    def handle_data(self, data):
        str = data.strip()
        if len(str) > 0:
            #self.contents.append({"type":"text", "data":str})
            self.tmp += str

    def handle_endtag(self, tag):
        # print "Encountered the end of a %s tag" % tag
        # print self.tmp
        if tag == "p" or tag == "div" or tag == "br" or tag == 'strong' :
            if self.tmp != "":
                # print "here %s" % self.tmp
                self.contents.append({"type":"text", "data":self.tmp})
                self.tmp = ""

def extractContents(url, html, document=True):
    if html == "":
        return []

    try:
        if document:
            content = Document(html).summary(html_partial=True)
            # print content
        else:
            content = '<div><body id="readabilityBody">'+html+'</body></div>'
            # print content
        hp = MyHTMLParser(url)
        hp.feed(content)
        hp.close()
        return hp.contents
    except:
        pass

    return []


def extractTitle(html):
    if html == "":
        return None
    try:
        doc = Document(html)
        short_title = doc.short_title()
        title = doc.title()
        if short_title is not None and short_title.strip() != "":
            title = short_title

        for delimiter in ['|', '-', '::', '/', '_']:
            if delimiter in title:
                parts = title.split(delimiter)
                if len(parts[0]) >= 4:
                    title = parts[0]
                    break
                elif len(parts[-1]) >= 4:
                    title = parts[-1]
                    break

        return title
    except:
        pass
    return None


# def extractContents_newspaper(url, html):
#     from newspaper import Article
#     a = Article(url, language='zh')  # Chinese
#     a.download(html=html)
#     a.parse()
#     return a

def extracttime(datecontent):
    date = None
    if datecontent.find("小时前") != -1:
        r = util.re_get_result(u"(.*?)小时前", datecontent)
        if r is not None:
            hour, = r
            try:
                date = datetime.datetime.now() - datetime.timedelta(hours=int(hour))
            except:
                date = None
        else:
            date = None
    elif datecontent.find("天前") != -1:
        r = util.re_get_result(u"(.*?)天前", datecontent)
        if r is not None:
            day, = r
            try:
                date = datetime.datetime.now() - datetime.timedelta(days=int(day))
            except:
                date = None
        else:
            date = None
    elif datecontent.find("昨天") != -1:
        date = datetime.datetime.now() - datetime.timedelta(days=1)

    elif datecontent.find("分钟前") != -1:
        r = util.re_get_result(u"(.*?)分钟前", datecontent)
        if r is not None:
            min, = r
            try:
                date = datetime.datetime.now() - datetime.timedelta(minutes=int(min))
            except:
                date = None
        else:
            date = None
    elif re.search("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", datecontent) :
        r = util.re_get_result("(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", datecontent)
        if r is not None:
            post_time, = r
            date = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
        else:
            date = None
    elif re.search("\d{4}-\d{2}-\d{2} \d{2}:\d{2}", datecontent):
        r = util.re_get_result("(\d{4}-\d{2}-\d{2} \d{2}:\d{2})", datecontent)
        if r is not None:
            post_time, = r
            date = datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M")
        else:
            date = None
    elif re.search("\d{4}-\d{2}-\d{2}", datecontent):
        r = util.re_get_result("(\d{4}-\d{2}-\d{2})", datecontent)
        if r is not None:
            post_time, = r
            date = datetime.datetime.strptime(post_time, "%Y-%m-%d")
        else:
            date = None
    elif re.search("\d{13}", datecontent):
        r = util.re_get_result("(\d{13})", datecontent)
        if r is not None:
            posttime, = r
            post_time = time.localtime(int(posttime) / 1000)
            date = datetime.datetime(post_time.tm_year, post_time.tm_mon, post_time.tm_mday, post_time.tm_hour,
                                 post_time.tm_min, post_time.tm_sec)
        else:
            date = None

    return date

if __name__ == '__main__':
    url1 = "http://auto.sohu.com/20150721/n417222681.shtml"
    url2 = "http://news.xinhuanet.com/politics/2015-06/17/c_1115638309.htm"
    url3 = "http://36kr.com/p/5038192.html"
    url4 = "http://itjuzi.com/overview/get_news/10146"
    url5 = "http://36kr.com/p/5050790.html"
    url6 = "http://www.lieyunwang.com/archives/205427"
    url7 = "https://www.huxiu.com/article/161354.html"
    url8 = "http://www.iyiou.com/p/31037"
    url9 = "https://www.huxiu.com/article/162518.html"
    url10 = "http://www.ctsbw.com/article-7665.html"
    print extracttime(u"3小时前")
    print extracttime(u"3分钟前")
    print extracttime(u"3天前")
    print extracttime("昨天")
    print extracttime("2016-10-08 07:00")
    print extracttime("2016-10-08 07:00:35")
    print datetime.datetime.now()
    print extracttime("1476153357182")
    print extracttime("1476153363284")

    # html = urllib.urlopen(url10).read()
    # # #print extractTitle(html)
    # # '''
    # contents = extractContents(url10, html)
    # # print "contents:"
    # for t in contents:
    #     print t["data"]
    #     print ""
    #     print ""
    #
    # '''
    # a = extractContents_newspaper(url10, html)
    # print(a.top_image)
    # print(a.acticle_html)

