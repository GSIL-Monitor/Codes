# -*- coding: utf-8 -*-
import os, sys,random, time
import requests
import json
# import requesocks


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config, util
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("crawler_lagou_job", stream=True)
logger = loghelper.get_logger("crawler_lagou_job")


class LagouJobCrawler():
    def __init__(self, timeout=30):
        self.timeout = timeout

    def is_crawl_success(self, url, content):
        if content.find('操作成功') == -1:
            logger.info(content)
            return False
        r = "companyId=(.*?)&pageSize"
        result = util.re_get_result(r, url)
        (id,) = result
        try:
            j = json.loads(content)
            rjobs = j['content']['data']['page']['result']
            if len(rjobs) == 0:
                logger.info("Failed due to 0 jobs under url: %s", url)
                return False
            if len(rjobs) > 0 and rjobs[0].has_key("companyId"):
                companyId = rjobs[0]["companyId"]
                logger.info("Url companyid: %s <-> lagou return companyId: %s", id, companyId)
                if str(companyId) != id:
                    logger.info("Failed due to different companyId: got: %s from request :%s", companyId, url)
                    return False
            return True
        except:
            return True

    def get_proxy(self):
        proxy = {"$or": [{'type': 'socks4'}, {'type': 'socks5'}], 'anonymity': 'high'}
        proxy_ip = None
        while proxy_ip is None:
            proxy_ip = proxy_pool.get_single_proxy(proxy)
            if proxy_ip is None:
                logger.info("No proxy !!!!!!!!!!!!!!!!!!!")
                time.sleep(30)
        return proxy_ip

    def crawler(self, url):
        cookies = dict(user_trace_token="20161221142700-7aded37d-c746-11e6-841f-525400f775ce",
                       LGUID="20161221142700-7aded745-c746-11e6-841f-525400f775ce",
                       LGRID="20161221142700-7aded745-c746-11e6-841f-525400f775ce")
        proxiesDict = {
            'http': 'socks4://180.173.153.98:1080',
            'https': 'socks4://180.173.153.98:1080',
        }

        while True:
                resp = requests.get(url,
                                    proxies=proxiesDict,
                                    cookies=cookies,
                                    timeout=30)
                logger.info(resp.status_code)
                if resp.status_code == 200:
                    logger.info(resp.encoding)
                    logger.info(resp.text.decode('utf-8'))
                    break
            # except Exception, e:
            #     logger.info(e)




if __name__ == '__main__':
    url = 'https://www.lagou.com/gongsi/searchPosition.json?companyId=6502&pageSize=1000&positionFirstType=%E5%B8%82%E5%9C%BA%E4%B8%8E%E9%94%80%E5%94%AE&pageNo=1'
    # url = "https://www.baidu.com"
    crawl = LagouJobCrawler()
    crawl.crawler(url)




