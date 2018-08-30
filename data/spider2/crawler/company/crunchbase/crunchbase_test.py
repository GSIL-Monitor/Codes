# -*- coding: utf-8 -*-
import os, sys, datetime
import requests, json
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
import random

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import proxy_pool



TYPE = 36001
SOURCE = 13130
URLS = []
Cookie = ''
Rule = {'type':'HTTPS', 'anonymous':'high'}

class NokeyDict():
    def __init__(self,item):
        self.item = dict(item)

    def __getitem__(self, key):
        return self.item.get(key)

# def get_proxy():
#     global Proxiesr
#     if len(Proxiesr) == 0:
#         Proxiesr = proxy_pool.get_single_proxy_x(Rule,1000)
#     while True:
#         try:
#             item = Proxiesr[random.randint(0, len(Proxiesr) - 1)]
#             ip, port = item['ip'], item['port']
#             ip_port = ip + ':' + str(port)
#             print('%s:%s' % (ip, port))
#             url = "https://www.baidu.com/"
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
#             }
#             timeout = 30
#             proxies = {
#                 'https': ip_port
#             }
#             r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
#             if r.text.find('hao123') >= 0:
#                 print('ip:%s for crunchbase' % ip_port)
#                 return ip, port
#         except Exception,e:
#             print('Proxy Exception:%s' % e)

def get_cookie():
    global Cookie
    print('to get cookie...')
    # ip,port = get_proxy()
    i = 1
    while Cookie == '':
        # while i >3 :
        #     ip, port = get_proxy()
        #     i = 0
        options = webdriver.FirefoxOptions()
        options.binary_location = '/root/firefox/firefox'
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument(
            'User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36')
        options.add_argument('Accept=text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type', 1)
        # profile.set_preference('network.proxy.http', '120.52.73.1')
        # profile.set_preference('network.proxy.http_port', 96)  # int
        # profile.set_preference('network.proxy.ssl', ip)
        # profile.set_preference('network.proxy.ssl_port', int(port))
        # profile.update_preferences()

        # bro = webdriver.Firefox(firefox_profile=profile,firefox_options=options,executable_path='./geckodriver')
        bro = webdriver.Firefox(firefox_options=options,executable_path='./geckodriver')
        # bro.implicitly_wait(60)
        # # 设置超时
        # bro.set_page_load_timeout(60)
        # bro.set_script_timeout(60)

        try:
            bro.get('https://www.crunchbase.com')
            time.sleep(60)

            cookie = [item["name"] + "=" + item["value"] for item in bro.get_cookies()]
            if cookie is not None:
                cookiestr = ';'.join(item for item in cookie)
                print('cookie:',cookiestr)
                if cookiestr.find('D_HID') >= 0 or cookiestr.find('_ok') >= 0:
                    print(cookiestr)
                    Cookie = cookiestr
                    bro.quit()
                    __clear_brs()
                    return Cookie
                else:
                    bro.quit()
                    __clear_brs()
                    print('fail to get cookie...')
        except Exception, e:
            bro.quit()
            __clear_brs()
            print(e)
            i += 1

def crawler_news(properties):
    global Cookie
    # ip, port = get_proxy()
    i = 1
    j = 0
    while True:
        while i >3 :
            # ip, port = get_proxy()
            i = 0

        # proxies = {
        #     'https':'%s:%d'%(ip,port)
        # }

        company = {}
        name = properties['name']
        uuid = properties['uuid']
        permalink = properties['permalink']
        print('start crawler %s|%s' % (name, uuid))
        cookie = Cookie
        headers = {'Cookie': '%s' % cookie,
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0'}
        url = 'https://www.crunchbase.com/v4/data/entities/organizations/{}?field_ids=["identifier","layout_id","facet_ids","title","short_description","is_locked"]&layout_mode=view'.format(
            permalink)

        try:
            result = requests.get(url, headers=headers)#, proxies=proxies,timeout=30)
            time.sleep(2)
            content = result.text

            if content.find('properties') >= 0:
                print('success to get %s msg' % name)

                try:
                    j_comp = json.loads(content)
                    j_cards = j_comp['cards']

                except:
                    print('wrong content not json')
                    return

                company_base = company['company_base'] = {}
                member = company['member'] = {}
                past_finance = company['past_finance'] = {}
                product = company['product'] = {}
                events = company['events'] = {}

                logo = None
                if properties['logo_id'] is not None:
                    logo = properties['logo_id']
                company_base['logo'] = logo
                tags = None
                if properties['categories'] is not None:
                    tags = properties['categories']
                company_base['tags'] = tags

                company_base['overview_funding'] = {}
                if j_cards.has_key('overview_headline'):
                    company_base['overview_funding'] = j_cards['overview_headline']
                company_base['properties'] = j_comp['properties']
                company_base['num_exits'] = j_cards['exits_headline']
                company_base['locations'] = j_cards['overview_image_description']
                company_base['overview_fields'] = j_cards['overview_fields']
                company_base['overview_fields2'] = j_cards['overview_fields2']
                company_base['overview_school_fields'] = j_cards['overview_school_fields']
                company_base['num_overview_investor'] = j_cards['overview_investor_fields']
                company_base['company_type'] = j_cards['overview_company_fields']
                company_base['description'] = j_cards['overview_description']
                company_base['twitter'] = j_cards['twitter']

                member['current_advisors'] = j_cards['current_advisors_image_list']  # 董事会成员 投资者
                member['num_current_advisors'] = j_cards['advisors_headline']
                member['past_employees'] = j_cards.get('past_employees_image_list')
                member['num_past_employees'] = j_cards['past_employees_headline']
                member['current_employees'] = j_cards['current_employees_image_list']
                member['num_current_employees'] = j_cards['current_employees_headline']

                past_finance['acquired_by_fields'] = j_cards['acquired_by_fields']
                past_finance['funds'] = j_cards['funds_list']
                past_finance['acquisitions'] = j_cards['acquisitions_list']
                past_finance['num_acquisitions'] = j_cards['acquisitions_headline']
                past_finance['num_investments'] = j_cards['investments_headline']
                past_finance['investments'] = j_cards['investments_list']
                past_finance['num_investors'] = j_cards['investors_headline']
                past_finance['investors'] = j_cards['investors_list']
                past_finance['exits_company'] = j_cards['exits_image_list']
                past_finance['funding_rounds'] = j_cards['funding_rounds_list']
                past_finance['funding_total'] = j_cards['funding_rounds_headline']
                past_finance['funds_headline'] = j_cards['funds_headline']
                past_finance['ipo_fields'] = j_cards['ipo_fields']

                product['num_sub_organizations'] = j_cards['sub_organizations_headline']
                product['sub_organizations'] = j_cards['sub_organizations_image_list']

                events['event_appearances'] = j_cards['event_appearances_list']
                events['num_event_appearances'] = j_cards['event_appearances_headline']
                # print(json.dumps(company, ensure_ascii=False,indent=4))
                acquired = past_finance['acquired_by_fields']
                funding = past_finance['funding_rounds']
                if acquired is not None or len(funding) > 0:
                    save(SOURCE, TYPE, url, uuid, name, company)
                else:
                    print('no funding msg!')
                return

            else:
                # print(content)
                print 'fail to crawl %s'% name
                i += 1
                j += 1
                if j >=5 :
                    raise ValueError('bad detail content')
        except Exception as e:
            print 'requests or mongo error:%s'%e
            i += 1
            j += 1
            if j >= 10:
                return

def save(SOURCE, TYPE, url, key, name, content):
    print("Saving: %s"% url)

    collection_content = {
        "date": datetime.datetime.now(),
        "source": SOURCE,
        "type": TYPE,
        "url": url,
        "key": key,
        "name": name,
        "content": content,
        "count":0
    }

    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key": key})
    if item is not None :
        try:
            if item.has_key('count') is False:
                collection.update({"source": SOURCE, "type": TYPE, "key": key},{"$set":{"count":0,'date':datetime.datetime.now()}})
                item['count'] = 0
            if item["content"] != content and item['count'] == 0:
                collection.update({"source": SOURCE, "type": TYPE, "key": key},{"$set":{"content":content,"count":1,'date':datetime.datetime.now()}})
                print("old data changed for company: %s"%key)
            else:
                if item['count'] == 0:
                    print("old data not changed for company: %s"%key)
                    collection.update({"source": SOURCE, "type": TYPE, "key": key},{"$set": {"count": 1,'date':datetime.datetime.now()}})
                else:
                    print("count = 1,do nothing")
        except Exception as e:
            print('mongo error:%s!'%e)
    else:
        try:
            collection.insert_one(collection_content)
        except:
            print('mongo error!')
    mongo.close()
    print("Saved: %s", url)

def run():
    global Proxiesr
    Proxiesr = []
    global Cookie
    # Cookie = get_cookie()
    Cookie = '' #TODO
    uuid = 'd433f3f7-bddf-b606-d095-77f37d8badca'
    name = 'HousingMan.com'
    permalink = 'housingman-com'
    logo_id = 'v1463997249/kycplzp5fm0o6eab0dog.jpg'
    categories = None
    properties = {
        'uuid': uuid,
        'name': name,
        'permalink': permalink,
        'logo_id': logo_id,
        "categories": categories,
    }
    print('cralw company:%s'%name)
    crawler_news(properties)



def __clear_brs():
    gcs = map(lambda y: str(y[1]),
              filter(lambda x: int(x[2]) == 1,
                     [line.split() for line in os.popen('ps -ef | grep firefox').readlines()]))
    if gcs:
        os.popen('kill %s' % ' '.join(gcs))

    gcs = map(lambda y: str(y[1]),
              filter(lambda x: int(x[2]) == 1,
                     [line.split() for line in os.popen('ps -ef | grep Xvfb').readlines()]))
    if gcs:
        os.popen('kill %s' % ' '.join(gcs))

    print('clear firefox done')


if __name__ == '__main__':
    print('gogogo')
    run()

