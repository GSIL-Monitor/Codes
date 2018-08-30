# -*- coding: utf-8 -*-
import sys,os
import time
import requests
from requests.adapters import HTTPAdapter
import random
from PIL import Image
from StringIO import StringIO
import proxy_pool

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper

#logger
loghelper.init_logger("my_request", stream=True)
logger = loghelper.get_logger("my_request")


http_session = None
user_agent_list = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36",
       ]


def get_a_user_agent():
    idx = random.randint(0, len(user_agent_list)-1)
    return user_agent_list[idx]


def get_session(proxy, new, agent):
    global http_session
    if new or http_session == None:
        http_session = requests.Session()
        #http_session.mount('http', HTTPAdapter(max_retries=5))

        if agent:
            user_agent = get_a_user_agent()
            # print user_agent
            http_session.headers["User-Agent"] = user_agent

        proxy_ip = None
        while proxy_ip is None:
            proxy_ip = proxy_pool.get_single_proxy(proxy)
            if proxy_ip is None:
                time.sleep(60)
        logger.info(proxy_ip)

        #http_session.proxies={proxy['type']:"http://%s:%s" % (proxy_ip["ip"], proxy_ip["port"])}
        http_session.proxies={"http":"http://%s:%s" % (proxy_ip["ip"], proxy_ip["port"]),
                              "https":"http://%s:%s" % (proxy_ip["ip"], proxy_ip["port"])}

    return http_session

def get_http_session(new=False, agent=True):
    proxy = {'type': 'http', 'anonymity':'high', 'ping':0.5, 'transferTime':3}
    return get_session(proxy, new, agent)

def get_https_session(new=False, agent=True):
    proxy = {'type': 'https', 'anonymity':'high', 'ping':0.5, 'transferTime':3}
    return get_session(proxy, new, agent)

def get_single_session(proxy, new=False, agent=True):
    return get_session(proxy, new, agent)

def get_agent_session():
    global http_session
    http_session = requests.Session()
    user_agent = get_a_user_agent()
    http_session.headers["User-Agent"] = user_agent

    return http_session


def get(logger, url):
    if url is None or url == '' or len(url) < 4:
        return (0, None)

    retry_times = 0
    timeout = 10
    while retry_times < 3:
        logger.info("No.%d, %s" % (retry_times+1,url))
        try:
            r = http_session.get(url, timeout=timeout)
            # use page encoding
            r.encoding = r.apparent_encoding

            return (0,r)
        except Exception,ex:
            logger.exception(ex)
            timeout = 20
        retry_times += 1

    return (-1, None)

def get1(logger, url):
    if url is None or url == '' or len(url) < 4:
        return (0, None)

    logger.info("%s", url)
    try:
        r = http_session.get(url, timeout=10)
        # use page encoding
        r.encoding = r.apparent_encoding
        return (0,r)
    except Exception,ex:
        logger.exception(ex)

    return (-1, None)

def get_image(logger, url, agent=False):
    if url.startswith("https://"):
        http_session = get_https_session(new=False, agent=False)
    else:
        http_session = get_http_session(new=False, agent=False)
    if agent:
        http_session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    retry_times = 0
    timeout = 10
    while retry_times < 3:
        try:
            r = http_session.get(url, timeout=timeout)
            img = Image.open(StringIO(r.content))
            output = StringIO()
            try:
                img.save(output, format='jpeg')
            except IOError:
                img.convert("RGB").save(output, format='jpeg')
            return output.getvalue()
        except Exception,ex:
            logger.exception(ex)
            if url.startswith("https://"):
                http_session = get_https_session(new=True, agent=False)
            else:
                http_session = get_http_session(new=True, agent=False)
            if agent:
                http_session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
            timout = 20
        retry_times += 1

    return None

def get_no_sesion(logger, url):
    if url is None or url == '' or len(url) < 4:
        return (0, None)

    retry_times = 0
    timeout = 10
    while retry_times < 2:
        logger.info("No.%d, %s" % (retry_times+1,url))
        try:
            r = requests.get(url, timeout=timeout)
            # use page encoding
            r.encoding = r.apparent_encoding

            return (0,r)
        except Exception,ex:
            logger.exception(ex)
            timeout = 10
        retry_times += 1

    return (-1, None)