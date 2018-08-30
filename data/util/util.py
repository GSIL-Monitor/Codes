#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import random
import datetime
import os
import shutil
import chardet
import re
import urllib2, urllib
import string
import StringIO
import time
import gzip
from bs4 import BeautifulSoup
from tld import get_tld
from urlparse import urlsplit
import tldextract
import json
import pythonwhois
import traceback
import io
from PIL import Image
import cStringIO
import uuid
import commands
import loghelper

#logger
loghelper.init_logger("util", stream=True)
logger = loghelper.get_logger("util")


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def re_get_result(reStr, content):
    re1 = re.compile(reStr,flags=re.S|re.I)
    m = re1.search(content)
    if m != None:
        return m.groups()
    return None


def md5str(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()


def get_file_md5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read(1024*1024)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest().lower()


def id_generator(size=6, chars="0123456789abcdefghjkmnpqrstuvwxyz"):
    return ''.join(random.choice(chars) for x in range(size))


def mkdirs(baseDir , relativeDir):
    dir = "%s/%s" % (baseDir, relativeDir)
    if not os.path.exists(dir):
        os.makedirs(dir)


def get_text_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text()


def html_encode(html):
    encoding = ""
    regCharset = re.compile(r'<meta[^>]*?charset=([^"\'>]*)',flags=re.S|re.I)
    m = regCharset.search(html)
    if m != None:
        encoding = m.group(1)

    if encoding == "":
        regCharset = re.compile(r'<meta[^>]*?charset=["\']([^"\'>]*)["\']',flags=re.S|re.I)
        m = regCharset.search(html)
        if m != None:
            encoding = m.group(1)

    if encoding == "":
        try:
            encoding_opinion = chardet.detect(html)
            encoding = encoding_opinion['encoding']
        except Exception,e:
            pass
    # print encoding
    try:
        html = unicode(html,encoding=encoding,errors='replace')
    except Exception,e:
        pass

    return html


def html_encode_4_requests(html,content,original_encoding):
    if original_encoding == None:
        return html

    encoding = ""
    regCharset = re.compile(r'<meta[^>]*?charset=([^"\'>]*)',flags=re.S|re.I)
    m = regCharset.search(html)
    if m != None:
        encoding = m.group(1)

    if encoding == "":
        regCharset = re.compile(r'<meta[^>]*?charset=["\']([^"\'>]*)["\']',flags=re.S|re.I)
        m = regCharset.search(html)
        if m != None:
            encoding = m.group(1)

    if encoding == "":
        try:
            encoding_opinion = chardet.detect(content)
            encoding = encoding_opinion['encoding']
        except Exception,e:
            pass
    html = content.decode(encoding)

    return html


def get_main_beianhao(beianhao):
    strs = beianhao.split("-")
    if len(strs[-1]) <=3:
        del strs[-1]
    main_beianhao = "-".join(strs)
    return main_beianhao


###deprecated
def norm_company_name_deprecated(name):
    if name is None:
        return name
    name = name.strip().replace("(", "（").replace(")", "）").replace(" ","")
    return name


def get_url_connect(url):
    urlConnect = None
    cnt = 0
    while cnt < 3:
        cnt += 1
        try:
            headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'}
            req = urllib2.Request(url, None, headers)
            urlConnect = urllib2.urlopen(req, timeout=30)
        except Exception,x:
            time.sleep(30)
            continue
        if urlConnect.getcode() == 200:
            break
        else:
            time.sleep(30)

    return (urlConnect, urlConnect.geturl())


def get_html_content(url):
    (urlConnect, actualUrl) = get_url_connect(url)
    if urlConnect == None or urlConnect.getcode() != 200:
        return None
    if urlConnect.info().get('Content-Encoding') == 'gzip':
        print "gzip!!!!!!!!!!!!!!!!!!!"
        buf = StringIO.StringIO( urlConnect.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
        f.close()
    else:
        data = urlConnect.read()

    html = html_encode(data)
    return (html, actualUrl)


def get_post_htmlContent(url, values):
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    urlConnect = urllib2.urlopen(req, timeout=30)

    if urlConnect == None or urlConnect.getcode() != 200:
        return None
    if urlConnect.info().get('Content-Encoding') == 'gzip':
        print "gzip!!!!!!!!!!!!!!!!!!!"
        buf = StringIO.StringIO( urlConnect.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
        f.close()
    else:
        data = urlConnect.read()

    html = html_encode(data)
    return html


def download(url, filePathName):
    (urlConnect,actualUrl) = get_html_content(url)
    if urlConnect == None:
        return (False, 0 , 0)

    if urlConnect.getcode() == 200:
        fileData = urlConnect.read()
        file = open(filePathName,'wb')
        file.write(fileData)
        file.close()


TIMEOUT = 10.0 # timeout in seconds
pythonwhois.net.socket.setdefaulttimeout(TIMEOUT)


def whois_creation_date(domain):
    #print domain
    cnt = 0
    while True:
        try:
            info = pythonwhois.get_whois(domain)
            if info.has_key("creation_date"):
                return info["creation_date"][0]
            for raw in info["raw"]:
                for line in raw.split("\n"):
                    if line.startswith("Registration Time"):
                        #print line
                        str = line.replace("Registration Time:","").strip()
                        return datetime.datetime.strptime(str, "%Y-%m-%d %H:%M:%S")
        except Exception,e:
            #print domain, e
            pass
        cnt += 1
        if cnt > 5:
            break

    return None

    # cnt = 0
    # while True:
    #     try:
    #         info = whois.query(domain)
    #         return info.creation_date
    #     except Exception,e:
    #         print domain, e
    #         traceback.print_exc()
    #         pass
    #     cnt += 1
    #     if cnt > 3:
    #         break
    #
    # return None


def get_poster_from_news(contents):
    if contents is None:
        return None
    for content in contents:
        if content["image_src"] != "" and content["image_src"] is not None:
            return content["image_src"]

    return None


def get_posterId_from_news(contents):
    if contents is None:
        return None
    for content in contents:
        if content["image"] != "" and content["image"] is not None:
            if content.has_key("height") and content["height"] < 50:
                continue
            return content["image"]

    return None


def get_brief_from_news(contents):
    brief = ""
    if contents is None:
        return brief
    for content in contents:
        if content["content"] != "" and content["content"] is not None:
            brief += " " + content["content"].strip()
            if len(brief) > 100:
                return brief.strip()

    return brief.strip()


def convert_image(fp, file_name, size=512):
    size = float(size)
    if file_name is not None and file_name.endswith(".svg"):
        # img = Image.open(io.BytesIO(cairosvg.SURFACES["PNG"].convert(fp.read(),parent_width=int(size),parent_height=int(size))))
        # /opt/py3-env/bin/cairosvg image.svg -o image.png
        rnd = id_generator()
        s_file = "/tmp/%s.svg" % rnd
        d_file = "/tmp/%s.png" % rnd
        s = open(s_file,"w")
        s.write(fp.read())
        s.close()
        cmd = "/opt/py3-env/bin/cairosvg %s -o %s" % (s_file, d_file)
        commands.getoutput(cmd)
        img = Image.open(d_file)
        os.remove(s_file)
        os.remove(d_file)
    else:
        img = Image.open(fp)
    xsize, ysize = img.size
    logger.info("xsize: %s, ysize: %s", xsize, ysize)
    if xsize > size or ysize > size:
        if xsize > ysize:
            x_s = size
            y_s = ysize * x_s / xsize
        else:
            y_s = size
            x_s = xsize * y_s / ysize
        logger.info("adjust xsize: %s, ysize: %s", int(x_s), int(y_s))
        if int(x_s) > 0 and int(y_s) > 0 :
            img = img.resize((int(x_s), int(y_s)), Image.ANTIALIAS)
    img = img.convert("RGBA")
    imagefile = cStringIO.StringIO()
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, img)
    bg.save(imagefile, format="JPEG") # 直接保存时转换不清楚！
    xsize, ysize = bg.size
    return imagefile.getvalue(), xsize, ysize


def get_uuid():
    return str(uuid.uuid1()).replace("-","")


if __name__ == '__main__':

    '''
    while True:
        print whois_creation_date("ichaixin.com")
        print whois_creation_date("xiniudata.cn")
    '''

    contents = [
        {
            "content" : "当客要在映客开直播啦，诸位最想扯什么蛋？DUNKHOME2016-07-12 18:20",
            "image" : "",
            "image_src" : "",
            "rank" : 1
        },
        {
            "content" : "虽然有点羞涩，但我们还是做出了这个决定，开启当客直播间。",
            "image" : "",
            "image_src" : "",
            "rank" : 2
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p3.pstatp.com/large/b4a0001c5290cc32a27",
            "rank" : 3
        },
        {
            "content" : "先说说直播风格吧，我们不是这样的",
            "image" : "",
            "image_src" : "",
            "rank" : 4
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p3.pstatp.com/large/b490001c6218c54be66",
            "rank" : 5
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p3.pstatp.com/large/b540001c41dfb3aa3a3",
            "rank" : 6
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p3.pstatp.com/large/b8b0001a2290c2715a5",
            "rank" : 7
        },
        {
            "content" : "更不是这样的",
            "image" : "",
            "image_src" : "",
            "rank" : 8
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p3.pstatp.com/large/b4a0001c52b95ac9a27",
            "rank" : 9
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p9.pstatp.com/large/b490001c624631a59e7",
            "rank" : 10
        },
        {
            "content" : "我们的目的是打造中国头号运动装备讲解直播间，恩，之一。这才是我们的画风",
            "image" : "",
            "image_src" : "",
            "rank" : 11
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p2.pstatp.com/large/b540001c424a6e8c034",
            "rank" : 12
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p3.pstatp.com/large/b490001c6266bdaec17",
            "rank" : 13
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p2.pstatp.com/large/b1e000528165c897781",
            "rank" : 14
        },
        {
            "content" : "当然还有一个重要的目标,就是建立用户和当客的桥梁，对，就是bridge。让更多的用户真正了解一下，你平常再用的get APP是一群什么样的人开发的，资讯是一群什么样的人写的，给你们打包商品的是一群什么样的人，我相信过不久你就会发现，这都是同样一批人。",
            "image" : "",
            "image_src" : "",
            "rank" : 15
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p1.pstatp.com/large/b1e0005281734675262",
            "rank" : 16
        },
        {
            "content" : "我们除了讲解运动装备之外，还会给大家分析一些情感生活问题，学科都是互通的嘛，相比大家都能理解。太黄的我就不讲了，总有一些刁民在背后说我污，我更喜欢污而不淫。反正从外太空到内子公，量子力学到母猪的产后护理，我会为大家一一解惑。",
            "image" : "",
            "image_src" : "",
            "rank" : 17
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p3.pstatp.com/large/b4b0001c571174e3b2b",
            "rank" : 18
        },
        {
            "content" : "至于主播本人，就是笔者，而笔者，就是当客的编辑，写过几期深夜课堂和人物志，涉及篮球、足球、跑步、健身、骑行等行业，给诸君截个图，看看在下的风格是什么样的：",
            "image" : "",
            "image_src" : "",
            "rank" : 19
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p1.pstatp.com/large/b490001c62b6f989b75",
            "rank" : 20
        },
        {
            "content" : "",
            "image" : "",
            "image_src" : "http://p1.pstatp.com/large/b8b0001a2324ec2e988",
            "rank" : 21
        },
        {
            "content" : "希望大家多多关注，鄙人一定尽全力为大家献上最精彩的直播。（直接在映客搜索当客，或输入房间号121094619）",
            "image" : "",
            "image_src" : "",
            "rank" : 22
        }
    ]

    print get_poster_from_news(contents)
    print get_brief_from_news(contents)
