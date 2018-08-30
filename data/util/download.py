# -*- coding: utf-8 -*-
import sys,os
from PIL import Image
from StringIO import StringIO

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../spider2/support'))
import proxy_pool
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../spider2/crawler'))
import BaseCrawler


class DownloadCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, max_crawl=100, timeout=10, use_proxy=True):
        BaseCrawler.BaseCrawler.__init__(self, max_crawl=max_crawl, timeout=timeout, use_proxy=use_proxy)

    def get_image(self, url,  max_retry=20, agent=True):
        retry_times = 0
        while retry_times < max_retry:
            result = self.crawl(url, agent=agent)
            #print result
            if result['get'] == 'success':
                try:
                    img = Image.open(StringIO(result["content"]))
                    output = StringIO()
                    try:
                        img.save(output, format='jpeg')
                    except IOError,e:
                        print e
                        img.convert("RGB").save(output, format='jpeg')
                    return output.getvalue()
                except Exception,e:
                    print e
                    pass
            self.init_http_session(url)
            retry_times += 1

        return None

    def get_image_size(self, url, max_retry=20, agent=True):
        retry_times = 0
        while retry_times < max_retry:
            result = self.crawl(url, agent=agent)
            # print result
            if result['get'] == 'success':
                try:
                    img = Image.open(StringIO(result["content"]))
                    output = StringIO()
                    try:
                        img.save(output, format='jpeg')
                    except IOError, e:
                        print e
                        img.convert("RGB").save(output, format='jpeg')
                    return (output.getvalue(), img.size[0], img.size[1])
                except Exception, e:
                    print e
                    pass
            self.init_http_session(url)
            retry_times += 1

        return (None, None, None)

    def get_image_size_new(self, url, max_retry=20, agent=True):
        retry_times = 0
        while retry_times < max_retry:
            result = self.crawl(url, agent=agent)
            # print result
            if result['get'] == 'success':
                try:
                    img = Image.open(StringIO(result["content"]))
                    output = StringIO()
                    try:
                        if url.find('png') >= 0:
                            img.save(output, format='png')
                        else:
                            img.save(output, format='jpeg')
                    except IOError, e:
                        print e
                        img.convert("RGB").save(output, format='jpeg')
                    return (output, img.size[0], img.size[1])
                except Exception, e:
                    print e
                    pass
            self.init_http_session(url)
            retry_times += 1

        return (None, None, None)

    def get(self, url,  max_retry=20, agent=True):
        retry_times = 0
        while retry_times < max_retry:
            result = self.crawl(url, agent=agent)
            #print result
            if result['get'] == 'success':
                try:
                    return result["content"]
                except Exception,e:
                    print e
                    pass
            self.init_http_session(url)
            retry_times += 1

        return None


if __name__ == "__main__":
    crawler = DownloadCrawler(use_proxy=False)
    #url = "https://www.itjuzi.com/images/5deef08b1b76b4f43d4f5295a8240e8a.jpg"
    #url = "https://pic.36krcnd.com//avatar/201606/14211652/vwwz4kceau5hxcdi.jpg"
    '''
    url = "https://krplus-pic.b0.upaiyun.com/201511/10/f556f52e44642eb2bf893510f92b8a2c.jpg"
    image = crawler.get_image(url, agent=True)
    if image is not None:
        f = open("test.jpg",'wb')
        f.write(image)
        f.close()
        print "Saved."
    else:
        print "Fail to get the image."
    '''
    url = "http://www.audiinnovation.cn/sites/default/files/webform/xiang_mu_xun_gu_zhi_zuo_wei_cheng_ke_shen_geng_v2vman_zu_fu_zhu_jia_shi_xu_yao_.pdf"
    c = crawler.get(url)
    if c:
        f = open("test.pdf","wb")
        f.write(c)
        f.close()