#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-
from tld import get_tld
from urlparse import urlsplit
from urlparse import urlparse
import util


def url_normalize(url):
    if url is None:
        return None

    url = url.strip().lower()
    if url == "":
        return None

    if url.find("zanwu.com") >= 0:
        return None

    if not url.startswith("http"):
        url = "http://" + url

    url = url.replace("。", ".")

    try:
        res = get_tld(url, fail_silently=True, as_object=True)
        domain = res.tld
        subdomain = res.subdomain
    except:
        return None

    res = urlsplit(url,allow_fragments=False)
    if res.query == "":
        if res.path == "/" or \
            res.path == "/index" or \
            res.path == "/index.htm" or \
            res.path == "/index.html" or \
            res.path == "/default.htm" or \
            res.path == "/default.html" or \
            res.path == "/index.do" or \
            res.path.startswith("/contact") or \
            res.path.startswith("/support"):
            url = "%s://%s" % (res.scheme, res.netloc)
    return url


def get_domain(url):
    url = url_normalize(url)
    if url is None:
        return None, None

    flag = True
    try:
        res = get_tld(url, fail_silently=True, as_object=True)
        domain = res.tld
        subdomain = res.subdomain
    except:
        return None, None

    if subdomain != "www" and subdomain != "m" and subdomain != "":
        flag = False
    else:
        s = urlsplit(url, allow_fragments=False)
        if s.query != '' or s.path != '':
            flag = False
    return flag, domain


def get_hostname(url):
    p = urlparse(url)
    return p.hostname


def get_market(url):
    if url is None:
        return None,None,None
    if url.find("itunes.apple.com") != -1:
        r = util.re_get_result('/id(\d*)', url)
        if r is None:
            return 4040, 16100, None
        else:
            track_id, = r
            try:
                track_id = int(track_id)
            except:
                track_id = None
            return 4040, 16100, track_id
    elif url.find("zhushou.360.cn") != -1:
        r = util.re_get_result("soft_id/(\d*)", url)
        if r is None:
            return 4050, 16010, None
        else:
            soft_id, = r
            return 4050, 16010, int(soft_id)
    elif url.find("shouji.baidu.com") != -1:
        r = util.re_get_result("/(\d*).html", url)
        if r is not None:
            soft_id, = r
            return 4050, 16020, int(soft_id)

        r = util.re_get_result("docid=(\d*)", url)
        if r is None:
            return 4050, 16020, None
        else:
            soft_id, = r
            return 4050, 16020, int(soft_id)
    elif url.find("www.wandoujia.com") != -1 or url.find("apps.wandoujia.com") != -1:
        r = util.re_get_result("/apps/([^?&#]*)", url)
        if r is None:
            return 4050, 16030, None
        else:
            apkname, = r
            return 4050, 16030, apkname.strip().lower()
    elif url.find("app.qq.com") != -1 or url.find("android.myapp.com") != -1 or url.find("sj.qq.com") != -1:
        r = util.re_get_result("apkName=([^?&#]*)", url)
        if r is not None:
            apkname, = r
            return 4050, 16040, apkname.strip().lower()

        r = util.re_get_result("pkgname=([^?&#]*)", url)
        if r is None:
            return 4050, 16040, None
        else:
            apkname, = r
            return 4050, 16040, apkname.strip().lower()
    elif url.find("play.google.com") != -1:
        r = util.re_get_result("id=([^?&#]*)", url)
        if r is None:
            return 4050, 16050, None
        else:
            apkname, = r
            return 4050, 16050, apkname.strip().lower()
    elif url.find("weibo.com") != -1:
        return 4030, None, None
    elif url.find("weixin.com") != -1:
        return 4020, None, None
    else:
        flag,domain=get_domain(url)
        if flag is None:
            return None,None,None
        if flag is False:
            domain = None
        return 4010, None, domain


if __name__ == '__main__':
    #print url_normalize("https://www.test.com/index.html")
    print get_domain("https://v.qq.com/x/page/d03578au4os.html")
    '''
    print get_domain("http://暂无")
    print get_market("http://weibo.com/u/5241794078")
    print get_market("http://zhushou.360.cn/detail/index/soft_id/712754?recrefer=SE_D_teambition")
    print get_market("http://shouji.baidu.com/software/9434635.html")
    print get_market("http://www.wandoujia.com/apps/com.talkweb.dadwheregoing")
    print get_market("http://a.app.qq.com/o/simple.jsp?pkgname=com.longlife.freshpoint")
    print get_market("http://m2.app.qq.com/app/appDetails.htm?apkName=com.umpay.huafubao")
    print get_market("http://android.myapp.com/myapp/detail.htm?apkName=com.cmt.figure.share")
    print get_market("http://sj.qq.com/myapp/detail.htm?apkName=com.foryou.truck")
    print get_market("https://play.google.com/store/apps/details?id=com.Qunar")
    '''
