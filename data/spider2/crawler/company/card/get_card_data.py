# -*- coding: utf-8 -*-
import random, math
import os, sys, datetime, re, json, time
import calendar
import requests
from lxml import html
from pyquery import PyQuery as pq
import subprocess
import threading
from card_prepare import save_dates, save_unionid

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import proxy_pool

# logger
loghelper.init_logger("crawler_qmp", stream=True)
logger = loghelper.get_logger("crawler_qmp")


class TransformMd5(object):
    """
    利用 card_data.js 对 爬取下来的data1进行解码
    返回 data
    """

    def __init__(self):
        self.process = None
        self.data = None

    def run(self, data1, timeout=2):
        def target():
            cmd = '/opt/phantomjs/bin/phantomjs card_data.js "%s"' % (data1)
            logger.info('js parse start')
            self.process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.process.wait()
            stdout = self.process.stdout.read()
            if (stdout.find("list") >= 0 or stdout.find("yearcount") >= 0) and self.data is None:
                self.data = (stdout)
            logger.info('finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            logger.info('Terminating process')
            self.process.terminate()
            thread.join()
        logger.info("return code %s", self.process.returncode)
        if self.process.returncode != 0:
            logger.info('js parse error%s' % self.process.stderr.read())
        return self.data


def get_proxy(http_type='http'):
    """
    获取可以访问的ip
    """

    proxy = {'type': http_type, 'anonymity': 'high'}
    proxy_ip = None
    url = "http://www.qimingpian.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }
    timeout = 5
    while True:
        logger.info("Start proxy_pool.get_single_proxy")
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            logger.info("proxy_pool.get_single_proxy return None")
            continue
        proxies = {
            'http': proxy_ip['ip:port']
        }
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('var title') >= 0:
                logger.info('ip:%s for qmp' % proxy_ip['ip:port'])
                return proxies
        except Exception, e:
            logger.info('Proxy Exception:%s' % e)


def take_dates():
    """
    从 mongo 中获取 date
    返回 dates
    :return:
    """

    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_dates
    try:
        item = collection.find_one({'type': 'date'})
        dates = []
        if item is not None:
            dates = item['content']
            logger.info('dates list length : %d | first date : %s' % (len(dates), dates[-1]))
        mongo.close()
        return dates
    except:
        logger.info('mongo error')
    mongo.close()


def make_dates():
    Dates = []
    year = time.localtime()[0]
    month = time.localtime()[1]-1
    if month == 1:
        year = year - 1
        month = 12
    days = list(range(1, calendar.monthrange(year, month)[1] + 1))
    for day in days:
        date = "%d.%02d.%02d" % (year, month, day)
        Dates.append(date)
    return Dates


def wait_time():
    """
    晚 9 点到早 9 点 sleep
    :return:
    """
    hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 21, 22, 23]
    while True:
        hour = time.localtime()[3]
        if hour not in hours:
            break
        logger.info('the hour:%d cant work' % hour)
        time.sleep(60 * 60)


def make_payload(date, page=1, lunci='全部融资'):
    """
    组织 post 请求的 form data 除 unionid（unionid 与 proxy 绑定直接从mongo获取）
    :param country:
    :param date:
    :param page:
    :param lunci:
    :return:
    """

    ticket = '7a8ded5e56db69797ebc290154fa3d2f'
    if page == 2:
        ticket = 'd0c03aa8c7108189d51f91d63de4f7fd'

    payload = {
        'rongzi_count': '',
        'country': '国内',
        'tag': '',
        'lunci': lunci,
        'jigou': '',
        'recentTime': '',
        'startTime': date,
        'endTime': date,
        'curpage': page,
        'num': 20,
        'ticket': ticket,
        'mhangye': '',
        'tag_type': '',
        'ptype': 'qmp_pc',
        'version': 2.0,
        'unionid': '',
        'jtype': 'vip',
        'time_token': '',
    }
    return payload


def save(postdata, date, data):
    """
    将经过 js 解码的 data 保存到数据库，数据库已存在的 pass不作处理
    :param postdata:
    :param date:
    :param data:
    :return:
    """

    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_rz
    # country = postdata['country']
    lunci = postdata['lunci']
    page = postdata['curpage']

    try:
        item = collection.find_one({'lunci': lunci, 'page': page, 'date': date})
        if item is None:
            collection_content = {
                'check': 'N',
                'createtime': datetime.datetime.now(),
                # 'country':country,
                'lunci': lunci,
                'page': page,
                'date': date,
                'postdata': postdata,
                'content': data
            }
            collection.insert_one(collection_content)
            logger.info('save data done ---  lunci:%s | page:%d | date:%s' % (lunci, page, date))
    except:
        logger.info('mongo error')
    mongo.close()


def get_unionid_item(date):
    """
    以 inuse 区分正在使用和未使用的（active=1 可用的unionid）
    inuse 中 daytimes(爬取天数)>15 则将 used 置为1 inuse置为0，否则返回此 item
    没有 inuse 则从 used=0 的获取，将 date 和 inuse set掉
    :param date:
    :return:
    """

    while True:
        mongo = db.connect_mongo()
        collection = mongo.raw.qmp_id
        try:
            item1 = collection.find_one({'active': 1, 'used': 0, 'inuse': 1})
            item2 = collection.find_one({'active': 1, 'used': 0})
            if item1 is not None:
                unionid = item1['unionid']
                randoms = random.randint(15, 20)
                if item1.has_key('daytimes') and item1['daytimes'] >= randoms:
                    collection.update({'unionid': unionid}, {'$set': {'used': 1, 'inuse': 0}})
                    mongo.close()
                    continue
                else:
                    mongo.close()
                    return item1
            elif item2 is not None:
                unionid = item2['unionid']
                collection.update({'unionid': unionid}, {'$set': {'ondate': date, 'inuse': 1}})
                item = collection.find_one({'unionid': unionid})
                mongo.close()
                return item
            else:
                logger.info('no unionid can use')
                mongo.close()
                return
        except Exception, E:
            logger.info(E)
            logger.info('mongo error')
            mongo.close()


def save_unionid_item(unionid, date, active=1, used=0, inuse=0, dayadd=0, proxy=1):
    """
    data 保存成功的 对 date 和 daytimes 进行实时更新
    请求失败的 重置状态
    :param unionid:
    :param date:
    :param active:
    :param used:
    :param inuse:
    :param dayadd:
    :param proxy:
    :return:
    """

    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_id
    try:
        item = collection.find_one({'unionid': unionid})
        if item is not None:
            if proxy == 0:
                proxy = get_proxy()
                collection.update({'unionid': unionid}, {
                    '$set': {'active': active, 'used': used, 'inuse': inuse, 'proxy': proxy,
                             'date': datetime.datetime.now()}})
                item = collection.find_one({'unionid': unionid})
                mongo.close()
                return item
            else:
                daytimes = item['daytimes']
                collection.update({'unionid': unionid}, {
                    '$set': {'active': active, 'used': used, 'inuse': inuse, 'daytimes': daytimes + dayadd,
                             'ondate': date, 'date': datetime.datetime.now()}})
        mongo.close()
    except:
        logger.info('mongo error')
        mongo.close()


def to_crawl(postdata, item, timeout=10):
    """
    分类返回的 status 1：已请求过（针对page1）0：请求成功 2：ticket error 3：frequent access
    5：priveledge   99：need login
    控制好 return 出口 continue 节点
    0：及时更新 item（date，daytimes） daytimes>random.ramdomint(15,20)  get_unionid_item
    3，5，99 ：get_unionid_item

    :param postdata:
    :param item:
    :param timeout:
    :return:
    """

    date = postdata['startTime']
    # country = postdata['country']
    lunci = postdata['lunci']
    page = postdata['curpage']
    ticket = postdata['ticket']

    result = {'status': None, 'rzcount': '', 'msg': '', 'item': {}}
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_rz
    try:
        # item1 = collection.find_one({'country': country, 'lunci': lunci, 'page': page, 'date': date})
        item1 = collection.find_one({'lunci': lunci, 'page': page, 'date': date})
        if item1 is not None:
            logger.info('date:%s | lunci:%s | page:%d had been crawled...' % (date, lunci, page))
            mongo.close()
            result['status'] = 1
            return result
    except:
        logger.info('mongo error')
        mongo.close()
    i = 0
    while True:
        unionid = item['unionid']
        postdata['unionid'] = unionid
        ondate = item['ondate']
        proxy = item['proxy']
        active = item['active']
        used = item['used']
        inuse = item['inuse']
        logger.info('retry:%d' % i)
        if i > 5:
            proxy = ''
        if proxy == '':
            item = save_unionid_item(unionid, date, active=active, used=used, inuse=inuse, proxy=0)
            logger.info(item)
            proxy = item['proxy']

        try:
            url = 'http://vip.api.qimingpian.com/h/touziFilter'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }

            logger.info('start to crawl --- lunci:%s | page:%d | date:%s' % (lunci, page, date))
            time.sleep(random.randint(15, 20))
            r = requests.post(url, headers=headers, data=postdata, timeout=timeout, proxies=proxy)
            if r.text is None:
                continue
            res = json.loads(r.text)
            logger.info('unionid:%s' % unionid)
            logger.info('proxy:%s' % proxy['http'])
            if res.has_key('status') and res['status'] == 0:
                data1 = res['data1']
                md = TransformMd5()
                data = md.run(data1)
                data = json.loads(data)
                save(postdata, date, data)
                result['status'] = res['status']
                result['rzcount'] = data['rzcount']
                result['unionid'] = unionid

                logger.info('rzcount:%s' % result['rzcount'])
                logger.info('date:%s | ondate:%s' % (date, ondate))
                if date != ondate:
                    save_unionid_item(unionid, date, inuse=1, dayadd=1)
                mongo = db.connect_mongo()
                collection = mongo.raw.qmp_id
                try:
                    item = collection.find_one({'unionid': unionid})
                except:
                    logger.info('mongo error')

                randomtimes = random.randint(15, 20)
                daytimes = item['daytimes']
                logger.info('daytimes:%d | randomtimes:%d' % (daytimes, randomtimes))
                if daytimes >= randomtimes:
                    collection.update({'unionid': unionid}, {'$set': {'used': 1, 'inuse': 0}})
                    item = get_unionid_item(date)
                mongo.close()
                result['item'] = item
                return result
            elif res.has_key('status') and (res['status'] == 3 or res['status'] == 5):
                logger.info('frequent access or no priveledge error:%s' % r.text)
                save_unionid_item(unionid, date, active=0, inuse=0)
                item = get_unionid_item(date)
                continue
            elif res.has_key('status') and res['status'] == 99:  # need login
                logger.info('login error:%s' % r.text)
                save_unionid_item(unionid, date, active=0, inuse=0)
                item = get_unionid_item(date)
                continue
            elif res.has_key('status') and res['status'] == 2:
                logger.info('ticket error:%s' % ticket)
                result['status'] = 2
                result['msg'] = 'ticket error'
                return result
            else:
                logger.info('bad content or bad status')
                result['status'] = 100
                result['msg'] = r.text
                return result
        except Exception, e:
            logger.info('proxy matter:%s' % e)
            i += 1


def refetch():
    # 补小分类大于40的第二页融资
    with open('refetch.txt','r') as f:
        content = f.readlines()
    lis = []
    for c in content:
        date = c.split('+')[0]
        lunci = c.split('+')[1]
        tup = (date,lunci)
        lis.append(tup)
    return lis


def run(flag='incr'):
    """
    初次 item 通过 date 获取 (2012-2017 6年)
    抓取国内国外2个 part ，通过返回的 rzcount 确定请求参数和次数 ---> 改版 没有国内国外
    :return:
    """

    global Dates
    if flag == 'all':
        Dates = take_dates()
    else:
        Dates = make_dates()
    # rzs = refetch()
    while True:
        date = Dates.pop()
        # wait_time()
        # if len(rzs) == 0:
        #     return
        # rz = rzs.pop()
        # date = rz[0]
        # lunci = rz[1]
        logger.info("date:%s"%(date))
        # countries = ['国内','国外']
        item = get_unionid_item(date)
        if item is None:
            break
        # for country in countries:
        payload = make_payload(date)
        result = to_crawl(payload, item)
        if result['status'] == 1:
            continue
        elif result['status'] != 0:
            logger.info('something wrong : %s ' % result['msg'])
            continue
        item = result['item']
        rzcount = int(result['rzcount'])
        logger.info("rzcount:%d" % (rzcount))
        if rzcount <= 20:
            continue
        elif rzcount <= 40:
            payload2 = make_payload(date, page=2)
            result2 = to_crawl(payload2, item)
            if result2['status'] == 1:
                continue
            elif result2['status'] != 0:
                logger.info('something wrong : %s ' % result2['msg'])
                continue
            item = result2['item']
        else:
            luncis = ['种子轮', '天使轮', 'Pre-A轮', 'A轮', 'A+轮', 'Pre-B轮', 'B轮', 'B+轮', 'C轮', 'C+轮', 'D轮~Pre-IPO', '战略融资']
            for lunci in luncis:
                payload3 = make_payload(date, lunci=lunci)
                result3 = to_crawl(payload3, item)
                if result3['status'] == 1:
                    continue
                elif result3['status'] != 0:
                    logger.info('something wrong : %s ' % result3['msg'])
                    continue
                item = result3['item']
                rzcount = int(result3['rzcount'])
                logger.info('lunci:%s|rzcount:%s' % (lunci, rzcount))
                if rzcount <= 20:
                    continue
                elif rzcount > 20:
                    payload4 = make_payload(date, lunci=lunci, page=2)
                    result4 = to_crawl(payload4, item)
                    if result4['status'] != 0:
                        logger.info('something wrong : %s ' % result4['msg'])
                        continue
                    item = result4['item']


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run(flag='all')
    else:
        run()

