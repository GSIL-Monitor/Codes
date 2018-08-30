# -*- coding: utf-8 -*-
import os, sys, re
import gevent
from gevent import monkey; monkey.patch_all()
import json


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper

#logger
loghelper.init_logger("crawler_mindst_next", stream=True)
logger = loghelper.get_logger("crawler_mindst_next")

def stripe(text):
    return text.strip()


class MindstCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self, url, content):
        if content.find(', "tagline":') == -1:
            return False
        return True


def process(g, content,crawler):
    data = json.loads(content)
    logger.info('totally %s items today'%len(data['objects']))

    for item in data['objects']:
        text = item['title']
        tag = None
        name = None
        match = re.search('#', text)
        if match:
            tags = text.split("#")
            tags = map(stripe, tags)
            name = tags[0]
            del tags[0]
            tag = " ".join(tags)
        else:
            name = text

        website = item['link']
        score = item['vote_count']
        desc = item['tagline']
        key = item['id']
        url = "http://mindstore.io/mind/%s" % key

        logger.info("key: %s, name: %s, desc: %s, score: %s, website: %s, tag: %s", key, name, desc, score, website,
                    tag)
        data = {
            "name": name,
            "website": website,
            "score": score,
            "desc": desc,
        }
        crawler.save(g.SOURCE, g.TYPE, url, key, data)


def run(g, crawler):
    url = "http://mindstore.io/api/v3/lime/mind/?look_back_days=0"

    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            process(g, result['content'],crawler)
            break


def start_run():
    while True:
        logger.info("Mindstore next start...")
        g = GlobalValues.GlobalValues(13111, 36009, "incr")
        thread = gevent.spawn(run, g, MindstCrawler())
        thread.join()
        logger.info("Mindstore next end.")

        gevent.sleep(60*30)        #30 minutes


if __name__ == "__main__":
    start_run()